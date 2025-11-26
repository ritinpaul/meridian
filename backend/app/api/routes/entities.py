from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import require_api_key
from app.db.repository import PositionRepository
from app.db.session import get_session
from app.stream.schemas import BatchIngestResponse, PositionBatchRequest

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("/positions/batch", response_model=BatchIngestResponse, dependencies=[Depends(require_api_key)])
async def ingest_position_batch(
    payload: PositionBatchRequest,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> BatchIngestResponse:
    repository = PositionRepository(session)
    event_bus = request.app.state.event_bus
    stream_hub = request.app.state.live_hub

    accepted = 0
    errors: list[str] = []

    try:
        event_messages = await repository.ingest_many(payload.records, source="batch")
        accepted = len(event_messages)
        for event_message in event_messages:
            outgoing = event_message.model_dump(mode="json")
            if event_bus.is_connected:
                await event_bus.publish(outgoing)
            else:
                await stream_hub.broadcast(outgoing)
    except Exception as exc:
        await session.rollback()
        errors.append(f"batch rejected: {exc}")

    return BatchIngestResponse(
        accepted=accepted,
        rejected=len(errors),
        errors=errors,
    )


@router.get("/live", dependencies=[Depends(require_api_key)])
async def get_live_entities(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, list[dict[str, str | float | None]]]:
    repository = PositionRepository(session)
    entities = await repository.get_live_entities(limit=1000)
    return {"entities": entities}
