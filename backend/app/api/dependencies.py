from typing import Annotated

from fastapi import Header, HTTPException, Query, status

from app.core.config import get_settings


def _verify_api_key(api_key_value: str | None) -> None:
    settings = get_settings()
    if settings.api_key is None:
        return

    if api_key_value != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )


async def require_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    _verify_api_key(x_api_key)


def require_ws_api_key(api_key: Annotated[str | None, Query()] = None) -> None:
    _verify_api_key(api_key)
