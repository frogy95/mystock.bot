"""
글로벌 예외 처리 모듈
AppError 기본 예외 클래스와 FastAPI 글로벌 핸들러를 정의한다.
"""
import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, OperationalError

logger = logging.getLogger("mystock.bot")


# ---------------------------------------------------------------------------
# 에러 응답 스키마
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """표준 에러 응답 스키마"""
    code: str
    message: str
    detail: Any = None


# ---------------------------------------------------------------------------
# 애플리케이션 기본 예외 클래스
# ---------------------------------------------------------------------------

class AppError(Exception):
    """애플리케이션 도메인 예외의 기본 클래스"""

    def __init__(self, code: str, message: str, status_code: int = 400, detail: Any = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


# ---------------------------------------------------------------------------
# 글로벌 예외 핸들러
# ---------------------------------------------------------------------------

async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    """AppError → 적절한 HTTP 상태코드로 변환"""
    logger.warning(f"AppError [{exc.code}]: {exc.message} | path={request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.code,
            message=exc.message,
            detail=exc.detail,
        ).model_dump(),
    )


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    """RequestValidationError → 422 (상세 validation 정보 포함)"""
    logger.warning(f"ValidationError: {exc.errors()} | path={request.url.path}")
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            code="VALIDATION_ERROR",
            message="요청 데이터가 올바르지 않습니다.",
            detail=exc.errors(),
        ).model_dump(),
    )


async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
    """IntegrityError → 409 Conflict (중복 데이터 등 DB 제약 위반)"""
    logger.warning(f"IntegrityError | path={request.url.path}")
    return JSONResponse(
        status_code=409,
        content=ErrorResponse(
            code="CONFLICT",
            message="데이터 충돌이 발생했습니다. 중복된 항목이 있을 수 있습니다.",
        ).model_dump(),
    )


async def handle_operational_error(request: Request, exc: OperationalError) -> JSONResponse:
    """OperationalError → 503 Service Unavailable (DB 연결 실패 등)"""
    logger.error(f"OperationalError | path={request.url.path}")
    return JSONResponse(
        status_code=503,
        content=ErrorResponse(
            code="SERVICE_UNAVAILABLE",
            message="데이터베이스에 연결할 수 없습니다. 잠시 후 다시 시도해주세요.",
        ).model_dump(),
    )


async def handle_general_error(request: Request, exc: Exception) -> JSONResponse:
    """Exception → 500 (내부 상세 메시지는 로그에만 기록, 응답에 노출하지 않음)"""
    logger.error(
        f"UnhandledError: {type(exc).__name__}: {exc} | path={request.url.path}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        ).model_dump(),
    )
