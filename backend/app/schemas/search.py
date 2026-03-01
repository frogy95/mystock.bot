"""
종목 검색 관련 Pydantic 스키마
"""
from pydantic import BaseModel


class StockSearchResult(BaseModel):
    """종목 검색 결과 스키마"""

    symbol: str   # 종목 코드 (예: 005930)
    name: str     # 종목명 (예: 삼성전자)
    market: str   # 시장 구분 (KOSPI / KOSDAQ)
