import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from statistics import median
from time import perf_counter

import websockets


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int((len(ordered) - 1) * pct)
    return ordered[index]


async def run_benchmark(events: int, ingest_url: str, live_url: str) -> tuple[float, float, float]:
    latencies_ms: list[float] = []

    async with websockets.connect(live_url) as live_ws, websockets.connect(ingest_url) as ingest_ws:
        # Initial connected event from live stream.
        await live_ws.recv()

        for i in range(events):
            external_id = f"bench-{i % 220:03d}"
            payload = {
                "external_id": external_id,
                "entity_type": "vehicle",
                "status": "active",
                "event_time": datetime.now(UTC).isoformat(),
                "latitude": 37.70 + (i % 20) * 0.005,
                "longitude": -122.50 + (i % 11) * 0.004,
                "speed": 12.0 + (i % 7),
                "heading": float((i * 9) % 360),
            }

            t0 = perf_counter()
            await ingest_ws.send(json.dumps(payload))
            await ingest_ws.recv()  # ack from ingest endpoint

            while True:
                message = json.loads(await live_ws.recv())
                if message.get("type") == "position_update" and message.get("external_id") == external_id:
                    latencies_ms.append((perf_counter() - t0) * 1000)
                    break

    if not latencies_ms:
        return 0.0, 0.0, 0.0

    return median(latencies_ms), percentile(latencies_ms, 0.95), max(latencies_ms)


def write_report(events: int, med: float, p95: float, max_latency: float) -> Path:
    report_path = Path(__file__).resolve().parents[2] / "benchmark" / "phase2_stream_latency_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    target = "PASS" if med < 500 else "FAIL"
    content = f"""# Meridian Phase 2 Latency Benchmark

- Events tested: {events}
- Median latency (ms): {med:.2f}
- P95 latency (ms): {p95:.2f}
- Max latency (ms): {max_latency:.2f}
- Sub-500ms target: {target}

Generated at: {datetime.now(UTC).isoformat()}
"""
    report_path.write_text(content, encoding="utf-8")
    return report_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark Meridian stream latency.")
    parser.add_argument("--events", type=int, default=300)
    parser.add_argument("--ingest-url", default="ws://localhost:8000/stream/positions")
    parser.add_argument("--live-url", default="ws://localhost:8000/stream/live")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    med, p95, max_latency = await run_benchmark(args.events, args.ingest_url, args.live_url)
    report_path = write_report(args.events, med, p95, max_latency)
    print(f"Median: {med:.2f}ms | P95: {p95:.2f}ms | Max: {max_latency:.2f}ms")
    print(f"Wrote report: {report_path}")


if __name__ == "__main__":
    asyncio.run(main())
