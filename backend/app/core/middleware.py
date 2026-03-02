"""
HTTP 미들웨어 모듈
요청 추적을 위한 Request ID 미들웨어를 제공한다.
"""
import uuid
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("mystock.bot")


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    모든 HTTP 요청에 고유 ID를 부여하는 미들웨어
    응답 헤더에 X-Request-ID를 추가하고, 요청 처리 시간을 로깅한다.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 요청 ID 생성 (클라이언트가 제공한 경우 재사용)
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # request.state에 저장하여 라우터에서 접근 가능
        request.state.request_id = request_id

        start_time = time.monotonic()
        response = await call_next(request)
        process_time = time.monotonic() - start_time

        # 응답 헤더에 Request ID 추가
        response.headers["X-Request-ID"] = request_id

        # 요청 처리 완료 로그 (500 이상은 ERROR, 나머지는 DEBUG)
        log_fn = logger.error if response.status_code >= 500 else logger.debug
        log_fn(
            f"request_id={request_id} method={request.method} "
            f"path={request.url.path} status={response.status_code} "
            f"duration={process_time:.3f}s"
        )

        return response
