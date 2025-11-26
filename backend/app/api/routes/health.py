from fastapi import APIRouter, Request

from app.db.session import db_ready_check

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def health_live() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def health_ready(request: Request) -> dict[str, str | bool]:
    db_ready = await db_ready_check()
    redis_ready = request.app.state.event_bus.is_connected
    return {
        "status": "ready" if db_ready else "not_ready",
        "db": db_ready,
        "redis": redis_ready,
    }
