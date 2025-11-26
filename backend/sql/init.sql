CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS entities (
    entity_id UUID PRIMARY KEY,
    external_id TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    status TEXT NOT NULL,
    last_seen_at TIMESTAMPTZ NOT NULL,
    last_latitude DOUBLE PRECISION NOT NULL,
    last_longitude DOUBLE PRECISION NOT NULL,
    last_speed DOUBLE PRECISION,
    last_heading DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS position_events (
    event_id UUID PRIMARY KEY,
    entity_id UUID NOT NULL REFERENCES entities(entity_id),
    event_time TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    speed DOUBLE PRECISION,
    heading DOUBLE PRECISION,
    source TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    geom geography(Point, 4326)
);

CREATE INDEX IF NOT EXISTS ix_position_events_entity_time
    ON position_events(entity_id, event_time DESC);

CREATE INDEX IF NOT EXISTS ix_position_events_geom_gist
    ON position_events USING GIST(geom);
