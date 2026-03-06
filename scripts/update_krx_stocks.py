#!/usr/bin/env python3
"""
KRX 종목 목록을 FinanceDataReader로 조회하여 backend/data/krx_stocks.json을 갱신한다.
로컬 환경에서 실행 (Docker 외부에서만 사용).

실행 방법:
    pip install finance-datareader
    python scripts/update_krx_stocks.py
"""
import json
import sys
from pathlib import Path


def main() -> None:
    try:
        import FinanceDataReader as fdr
    except ImportError:
        print("FinanceDataReader가 설치되지 않았습니다. pip install finance-datareader 를 실행하세요.")
        sys.exit(1)

    stocks: list[dict] = []
    seen: set[str] = set()

    # KOSPI/KOSDAQ: kind.krx.co.kr 기반 (-DESC 접미사)
    # ETF/KR: 네이버 금융 기반
    for market, label in [("KOSPI-DESC", "KOSPI"), ("KOSDAQ-DESC", "KOSDAQ"), ("ETF/KR", "ETF")]:
        print(f"{label} 종목 조회 중...")
        try:
            df = fdr.StockListing(market)
            count = 0
            for _, row in df.iterrows():
                symbol = str(row.get("Code", row.get("Symbol", ""))).strip()
                name = str(row.get("Name", "")).strip()
                if not symbol or not name or symbol in seen:
                    continue
                seen.add(symbol)
                stocks.append({"symbol": symbol, "name": name, "market": label})
                count += 1
            print(f"  {label}: {count}개")
        except Exception as e:
            print(f"  {label} 조회 실패: {e}")

    if not stocks:
        print("조회된 종목이 없습니다. 네트워크 상태를 확인하세요.")
        sys.exit(1)

    output_path = Path(__file__).parent.parent / "backend" / "data" / "krx_stocks.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stocks, f, ensure_ascii=False, indent=2)

    print(f"\n저장 완료: {output_path} (총 {len(stocks)}개 종목)")


if __name__ == "__main__":
    main()
