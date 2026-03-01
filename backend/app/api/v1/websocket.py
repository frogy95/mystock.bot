"""
WebSocket 엔드포인트
ws://localhost:8000/api/v1/ws/quotes - 실시간 시세 구독
"""
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.services.websocket_manager import ws_manager

logger = logging.getLogger("mystock.bot")

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/quotes")
async def websocket_quotes(
    websocket: WebSocket,
    symbols: str = Query(default="", description="구독할 종목 코드 (쉼표 구분)"),
):
    """실시간 시세 WebSocket 엔드포인트."""
    await ws_manager.connect(websocket)

    # 쿼리 파라미터로 초기 구독 종목 설정
    if symbols:
        symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
        ws_manager.subscribe(symbol_list)

    # 연결 확인 메시지 전송
    await websocket.send_json({"type": "connected", "message": "시세 구독 연결됨"})

    try:
        while True:
            # 클라이언트 메시지 수신 (keep-alive 및 구독 변경)
            data = await websocket.receive_json()
            if data.get("type") == "subscribe":
                new_symbols = data.get("symbols", [])
                ws_manager.subscribe(new_symbols)
                await websocket.send_json({
                    "type": "subscribed",
                    "symbols": new_symbols,
                })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket 오류: {e}")
        ws_manager.disconnect(websocket)
