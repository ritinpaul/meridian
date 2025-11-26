# Meridian

Meridian is a real-time geospatial operations command center built to demonstrate
production-style streaming architecture, low-latency event processing, and
high-volume live map rendering.

## Why This Project Stands Out

- End-to-end real-time pipeline: WebSocket ingest, Redis fanout, and live UI updates
- Geospatial state layer with PostgreSQL/PostGIS schema and query-ready entity snapshots
- Operational dashboard with marker clustering and status-aware map visualization
- Measured performance evidence: median stream latency of 6.37 ms on benchmark runs

## Performance Snapshot

From the latest benchmark report:

- Events tested: 220
- Median latency: 6.37 ms
- P95 latency: 7.72 ms
- Max latency: 18.56 ms
- Sub-500 ms target: PASS

## Core Capabilities

- Real-time telemetry ingest via `WS /stream/positions`
- Live subscriber stream via `WS /stream/live`
- Batch ingestion endpoint for bulk updates
- Persistent entity + event history storage
- Live entity snapshot API for map clients

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Redis Pub/Sub
- Data: PostgreSQL + PostGIS
- Frontend: Next.js 14, TypeScript, React Leaflet
- Infra: Docker Compose

## Local Setup

### Run Full Stack

```bash
docker compose up --build
```

### Access Services

- Dashboard: http://localhost:3000
- Backend API: http://localhost:8000

### Health Checks

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

## Quick Telemetry Example

Send this JSON payload to `WS /stream/positions` using any WebSocket client:

```json
{
  "external_id": "VEH-001",
  "entity_type": "vehicle",
  "status": "active",
  "event_time": "2026-04-20T10:00:00Z",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "speed": 22.5,
  "heading": 120
}
```

## Benchmark Command

```bash
cd backend
python scripts/benchmark_stream_latency.py --events 300
```

## Project Structure

```text
Meridian/
  backend/
    app/
    scripts/
    sql/
    tests/
  frontend/
    app/
    components/
    lib/
  benchmark/
  docker-compose.yml
```

## Resume-Ready Highlights

- Built a real-time geospatial tracking system with WebSocket and Redis event fanout.
- Designed and implemented persistent entity/event state for low-latency map updates.
- Delivered measurable streaming performance with single-digit millisecond median latency.
