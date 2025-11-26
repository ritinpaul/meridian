# Meridian Backend

FastAPI backend for Meridian's real-time geospatial operations platform.

## Features in Phase 1 + 2

- WebSocket ingest endpoint with payload validation
- Redis Pub/Sub fanout for low-latency distribution
- Postgres/SQLite state persistence for position events
- Live entity API for dashboard rendering
- Stream latency benchmark script

## Run Locally

```bash
pip install -e .[dev]
uvicorn app.main:app --reload
```

## Key Endpoints

- `GET /health/live`
- `GET /health/ready`
- `WS /stream/positions` (ingest)
- `WS /stream/live` (subscriber)
- `POST /entities/positions/batch`
- `GET /entities/live`

## Redis Subscriber Demo

```bash
python scripts/redis_subscriber.py
```

## Latency Benchmark

```bash
python scripts/benchmark_stream_latency.py --events 300
```
