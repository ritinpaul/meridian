from fastapi import APIRouter

from app.api.routes.entities import router as entities_router
from app.api.routes.health import router as health_router
from app.api.routes.stream import router as stream_router

router = APIRouter()
router.include_router(health_router)
router.include_router(stream_router)
router.include_router(entities_router)
