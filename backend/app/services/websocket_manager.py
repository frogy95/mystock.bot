"""
WebSocket 관리 모듈
연결된 클라이언트에게 실시간 데이터를 브로드캐스트한다.
KIS REST API를 주기적으로 폴링하여 시세 데이터를 전달한다.
"""
import asyncio
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger("mystock.bot")


class WebSocketManager:
    """WebSocket 연결 관리 및 브로드캐스트."""

    def __init__(self):
        self._connections: list[WebSocket] = []
        self._polling_task: asyncio.Task | None = None
        self._watched_symbols: set[str] = set()

    async def connect(self, websocket: WebSocket) -> None:
        """클라이언트 WebSocket 연결을 수락하고 등록한다."""
        await websocket.accept()
        self._connections.append(websocket)
        logger.info(f"WebSocket 연결: 총 {len(self._connections)}개")

    def disconnect(self, websocket: WebSocket) -> None:
        """클라이언트 WebSocket 연결을 해제한다."""
        if websocket in self._connections:
            self._connections.remove(websocket)
        logger.info(f"WebSocket 해제: 총 {len(self._connections)}개")

    def subscribe(self, symbols: list[str]) -> None:
        """관심 종목을 등록한다."""
        self._watched_symbols.update(symbols)

    async def broadcast(self, data: dict[str, Any]) -> None:
        """모든 연결된 클라이언트에게 데이터를 전송한다."""
        disconnected = []
        for ws in self._connections:
            try:
                await ws.send_json(data)
            except Exception:
                disconnected.append(ws)
        # 끊어진 연결 정리
        for ws in disconnected:
            if ws in self._connections:
                self._connections.remove(ws)

    async def start_polling(self) -> None:
        """KIS API 폴링 루프를 시작한다."""
        if self._polling_task and not self._polling_task.done():
            return
        self._polling_task = asyncio.create_task(self._poll_loop())
        logger.info("시세 폴링 시작")

    async def stop_polling(self) -> None:
        """폴링 루프를 중단한다."""
        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass
            logger.info("시세 폴링 중단")

    async def _poll_loop(self) -> None:
        """30초마다 관심 종목 현재가를 조회하여 브로드캐스트한다."""
        from app.services.kis_client import kis_client

        while True:
            try:
                await asyncio.sleep(30)
                if not self._connections or not self._watched_symbols:
                    continue

                for symbol in list(self._watched_symbols):
                    try:
                        quote = await kis_client.get_quote(symbol)
                        if quote:
                            await self.broadcast({
                                "type": "quote",
                                "symbol": symbol,
                                "data": quote,
                            })
                    except Exception as e:
                        logger.debug(f"시세 조회 오류 [{symbol}]: {e}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"폴링 루프 오류: {e}")


# 싱글턴 인스턴스
ws_manager = WebSocketManager()
