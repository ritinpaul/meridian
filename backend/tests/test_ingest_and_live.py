def test_batch_ingest_and_live_snapshot(client):
    payload = {
        "records": [
            {
                "external_id": "TRK-100",
                "entity_type": "truck",
                "status": "active",
                "event_time": "2026-04-20T10:00:00Z",
                "latitude": 40.7128,
                "longitude": -74.006,
                "speed": 18.5,
                "heading": 90,
            },
            {
                "external_id": "TRK-101",
                "entity_type": "truck",
                "status": "warning",
                "event_time": "2026-04-20T10:00:02Z",
                "latitude": 40.7138,
                "longitude": -74.004,
                "speed": 8.5,
                "heading": 70,
            },
        ]
    }

    batch_response = client.post("/entities/positions/batch", json=payload)
    assert batch_response.status_code == 200
    body = batch_response.json()
    assert body["accepted"] == 2
    assert body["rejected"] == 0

    live_response = client.get("/entities/live")
    assert live_response.status_code == 200
    entities = live_response.json()["entities"]
    assert len(entities) == 2
    assert {item["external_id"] for item in entities} == {"TRK-100", "TRK-101"}
