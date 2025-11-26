from datetime import UTC, datetime

from pydantic import BaseModel, Field


class TelemetryRecord(BaseModel):
    external_id: str = Field(min_length=1, max_length=64)
    entity_type: str = Field(default="vehicle", max_length=32)
    status: str = Field(default="active", max_length=32)
    event_time: datetime = Field(default_factory=lambda: datetime.now(UTC))
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed: float | None = Field(default=None, ge=0)
    heading: float | None = Field(default=None, ge=0, le=360)


class PositionBatchRequest(BaseModel):
    records: list[TelemetryRecord] = Field(min_length=1)


class IngestAck(BaseModel):
    status: str
    event_id: str
    entity_id: str


class PositionEventMessage(BaseModel):
    type: str = "position_update"
    event_id: str
    entity_id: str
    external_id: str
    status: str
    event_time: datetime
    latitude: float
    longitude: float
    speed: float | None = None
    heading: float | None = None


class BatchIngestResponse(BaseModel):
    accepted: int
    rejected: int
    errors: list[str] = Field(default_factory=list)
