import asyncio

from fastapi import WebSocket


class LiveStreamHub:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, message: dict) -> None:
        stale: list[WebSocket] = []
        async with self._lock:
            targets = list(self._connections)

        for connection in targets:
            try:
                await connection.send_json(message)
            except Exception:
                stale.append(connection)

        if not stale:
            return

        async with self._lock:
            for connection in stale:
                self._connections.discard(connection)

    @property
    def connection_count(self) -> int:
        return len(self._connections)
