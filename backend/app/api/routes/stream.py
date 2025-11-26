from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.api.dependencies import require_ws_api_key
from app.db.repository import PositionRepository
from app.db.session import SessionLocal
from app.stream.schemas import IngestAck, TelemetryRecord

router = APIRouter(tags=["stream"])


@router.websocket("/stream/live")
async def subscribe_live_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        require_ws_api_key(websocket.query_params.get("api_key"))
    except Exception:
        await websocket.send_json({"status": "error", "detail": "invalid api key"})
        await websocket.close(code=4401)
        return

    hub = websocket.app.state.live_hub
    await hub.connect(websocket)
    await websocket.send_json({"type": "connected", "connections": hub.connection_count})

    try:
        while True:
            message = await websocket.receive_text()
            if message == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await hub.disconnect(websocket)


@router.websocket("/stream/positions")
async def ingest_positions(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        require_ws_api_key(websocket.query_params.get("api_key"))
    except Exception:
        await websocket.send_json({"status": "error", "detail": "invalid api key"})
        await websocket.close(code=4401)
        return

    hub = websocket.app.state.live_hub
    event_bus = websocket.app.state.event_bus

    async with SessionLocal() as session:
        repository = PositionRepository(session)

        try:
            while True:
                payload = await websocket.receive_json()
                try:
                    record = TelemetryRecord.model_validate(payload)
                except ValidationError as exc:
                    await websocket.send_json({"status": "error", "detail": str(exc)})
                    continue

                event_message = await repository.ingest_position(record, source="ws")
                outgoing = event_message.model_dump(mode="json")
                if event_bus.is_connected:
                    await event_bus.publish(outgoing)
                else:
                    await hub.broadcast(outgoing)

                ack = IngestAck(status="ok", event_id=event_message.event_id, entity_id=event_message.entity_id)
                await websocket.send_json(ack.model_dump())
        except WebSocketDisconnect:
            return
