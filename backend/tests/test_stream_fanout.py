def test_websocket_ingest_fanout(client):
    with client.websocket_connect("/stream/live") as live_ws:
        connected_event = live_ws.receive_json()
        assert connected_event["type"] == "connected"

        with client.websocket_connect("/stream/positions") as ingest_ws:
            ingest_ws.send_json(
                {
                    "external_id": "VEH-999",
                    "entity_type": "vehicle",
                    "status": "active",
                    "event_time": "2026-04-20T10:10:00Z",
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    "speed": 24.0,
                    "heading": 45,
                }
            )

            ack = ingest_ws.receive_json()
            assert ack["status"] == "ok"
            assert "event_id" in ack

        fanout_message = live_ws.receive_json()
        assert fanout_message["type"] == "position_update"
        assert fanout_message["external_id"] == "VEH-999"
        assert fanout_message["latitude"] == 37.7749
