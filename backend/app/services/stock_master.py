"""
종목 마스터 서비스 모듈 (레거시 호환 래퍼)
실제 검색 로직은 stock_search.py에서 처리한다.
"""
from app.services.stock_search import search_stocks

__all__ = ["search_stocks"]
