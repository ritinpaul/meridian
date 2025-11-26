from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Entity, PositionEvent
from app.stream.schemas import PositionEventMessage, TelemetryRecord


class PositionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_entity(self, record: TelemetryRecord) -> Entity:
        query = select(Entity).where(Entity.external_id == record.external_id)
        result = await self.session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            entity = Entity(
                external_id=record.external_id,
                type=record.entity_type,
                status=record.status,
                last_seen_at=record.event_time,
                last_latitude=record.latitude,
                last_longitude=record.longitude,
                last_speed=record.speed,
                last_heading=record.heading,
            )
            self.session.add(entity)
            await self.session.flush()
            return entity

        entity.type = record.entity_type
        entity.status = record.status
        entity.last_seen_at = record.event_time
        entity.last_latitude = record.latitude
        entity.last_longitude = record.longitude
        entity.last_speed = record.speed
        entity.last_heading = record.heading
        await self.session.flush()
        return entity

    async def insert_position_event(self, entity: Entity, record: TelemetryRecord, source: str) -> PositionEvent:
        event = PositionEvent(
            entity_id=entity.entity_id,
            event_time=record.event_time,
            latitude=record.latitude,
            longitude=record.longitude,
            speed=record.speed,
            heading=record.heading,
            source=source,
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def ingest_position(self, record: TelemetryRecord, source: str = "api") -> PositionEventMessage:
        events = await self.ingest_many([record], source=source)
        return events[0]

    async def ingest_many(
        self,
        records: list[TelemetryRecord],
        source: str = "api",
    ) -> list[PositionEventMessage]:
        messages: list[PositionEventMessage] = []

        for record in records:
            entity = await self.upsert_entity(record)
            event = await self.insert_position_event(entity, record, source=source)
            messages.append(
                PositionEventMessage(
                    event_id=event.event_id,
                    entity_id=entity.entity_id,
                    external_id=entity.external_id,
                    status=entity.status,
                    event_time=event.event_time,
                    latitude=event.latitude,
                    longitude=event.longitude,
                    speed=event.speed,
                    heading=event.heading,
                )
            )

        await self.session.commit()
        return messages

    async def get_live_entities(self, limit: int = 500) -> list[dict[str, str | float | None]]:
        query = select(Entity).order_by(Entity.last_seen_at.desc()).limit(limit)
        result = await self.session.execute(query)
        entities = result.scalars().all()

        payload: list[dict[str, str | float | None]] = []
        for entity in entities:
            payload.append(
                {
                    "entity_id": entity.entity_id,
                    "external_id": entity.external_id,
                    "type": entity.type,
                    "status": entity.status,
                    "last_seen_at": entity.last_seen_at.isoformat(),
                    "latitude": entity.last_latitude,
                    "longitude": entity.last_longitude,
                    "speed": entity.last_speed,
                    "heading": entity.last_heading,
                }
            )
        return payload
