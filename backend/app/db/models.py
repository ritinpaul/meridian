from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Entity(Base):
    __tablename__ = "entities"

    entity_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    type: Mapped[str] = mapped_column(String(32), default="vehicle")
    status: Mapped[str] = mapped_column(String(32), default="active")
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    last_latitude: Mapped[float] = mapped_column(Float)
    last_longitude: Mapped[float] = mapped_column(Float)
    last_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_heading: Mapped[float | None] = mapped_column(Float, nullable=True)

    position_events: Mapped[list[PositionEvent]] = relationship(back_populates="entity")


class PositionEvent(Base):
    __tablename__ = "position_events"

    event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    entity_id: Mapped[str] = mapped_column(ForeignKey("entities.entity_id"), index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    heading: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="api")
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    entity: Mapped[Entity] = relationship(back_populates="position_events")


Index("ix_position_events_entity_time", PositionEvent.entity_id, PositionEvent.event_time)
