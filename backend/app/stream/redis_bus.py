import asyncio
import contextlib
import json
from collections.abc import Awaitable, Callable

import redis.asyncio as redis


class RedisEventBus:
    def __init__(self, redis_url: str, channel: str) -> None:
        self._redis_url = redis_url
        self._channel = channel
        self._redis: redis.Redis | None = None
        self._listener_task: asyncio.Task | None = None
        self._connected = False

    async def connect(self) -> None:
        try:
            self._redis = redis.from_url(self._redis_url, decode_responses=True)
            await self._redis.ping()
            self._connected = True
        except Exception:
            self._connected = False

    async def publish(self, message: dict) -> None:
        if not self._connected or self._redis is None:
            return

        payload = json.dumps(message)
        await self._redis.publish(self._channel, payload)

    async def start_listener(self, callback: Callable[[dict], Awaitable[None]]) -> None:
        if not self._connected or self._redis is None:
            return

        self._listener_task = asyncio.create_task(self._listen_loop(callback))

    async def _listen_loop(self, callback: Callable[[dict], Awaitable[None]]) -> None:
        if self._redis is None:
            return

        pubsub = self._redis.pubsub()
        await pubsub.subscribe(self._channel)

        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message and message.get("type") == "message":
                    with contextlib.suppress(json.JSONDecodeError, TypeError):
                        payload = json.loads(message["data"])
                        await callback(payload)
                await asyncio.sleep(0)
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe(self._channel)
            await pubsub.close()

    async def close(self) -> None:
        if self._listener_task is not None:
            self._listener_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._listener_task

        if self._redis is not None:
            await self._redis.aclose()

        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected
