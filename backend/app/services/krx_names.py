"""
KRX 한국어 종목명 매핑 서비스
backend/data/krx_stocks.json을 앱 시작 시 메모리에 로드하여 빠른 이름 조회를 제공한다.
"""
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("mystock.bot")

# 모듈 수준 인메모리 캐시 (프로세스당 1회 로드)
_krx_names: dict[str, str] = {}   # {종목코드: 한국어 종목명}
_krx_markets: dict[str, str] = {}  # {종목코드: KOSPI/KOSDAQ}

# JSON 파일 경로 (backend/data/krx_stocks.json)
_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "krx_stocks.json"


async def load_krx_names() -> None:
    """
    JSON 파일에서 KRX 종목 정보를 로드하여 메모리에 캐싱한다.
    앱 시작(lifespan)에서 호출된다.
    """
    global _krx_names, _krx_markets

    if not _DATA_FILE.exists():
        logger.warning(
            f"KRX 종목 데이터 파일 없음: {_DATA_FILE} "
            "- scripts/update_krx_stocks.py를 실행하여 데이터를 생성하세요. "
            "KRX 한국어 이름 매핑 없이 영문명으로 동작합니다."
        )
        return

    try:
        with open(_DATA_FILE, encoding="utf-8") as f:
            stocks: list[dict] = json.load(f)

        _krx_names = {s["symbol"]: s["name"] for s in stocks}
        _krx_markets = {s["symbol"]: s["market"] for s in stocks}

        logger.info(f"KRX 종목명 매핑 로드 완료 (총 {len(_krx_names)}개)")
    except Exception as e:
        logger.warning(f"KRX 종목명 매핑 로드 실패: {e}")


def get_korean_name(symbol: str) -> Optional[str]:
    """종목코드(숫자 6자리)로 한국어 종목명을 반환한다. 없으면 None."""
    return _krx_names.get(symbol)


def get_market(symbol: str) -> Optional[str]:
    """종목코드로 KOSPI/KOSDAQ 구분을 반환한다. 없으면 None."""
    return _krx_markets.get(symbol)


def search_krx_by_name(query: str, limit: int = 20) -> list[dict]:
    """
    한국어 종목명 또는 종목코드로 KRX 종목을 검색한다.
    인메모리 dict를 순회하여 contains 방식으로 매칭한다.
    """
    q = query.strip().lower()
    results = []
    for code, name in _krx_names.items():
        if q in name.lower() or q in code.lower():
            results.append({
                "symbol": code,
                "name": name,
                "market": _krx_markets.get(code, ""),
            })
            if len(results) >= limit:
                break
    return results
