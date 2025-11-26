from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import get_settings
from app.db.session import init_db
from app.stream.hub import LiveStreamHub
from app.stream.redis_bus import RedisEventBus


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.include_router(router)

    @app.on_event("startup")
    async def startup_event() -> None:
        await init_db()
        app.state.live_hub = LiveStreamHub()
        app.state.event_bus = RedisEventBus(
            redis_url=settings.redis_url,
            channel=settings.redis_channel,
        )
        await app.state.event_bus.connect()
        await app.state.event_bus.start_listener(app.state.live_hub.broadcast)

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        await app.state.event_bus.close()

    return app


app = create_app()
