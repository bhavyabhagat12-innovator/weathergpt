"""
Tests for WebSocket alert dispatching and bulletin simulation.
"""

import json
import pytest
from starlette.testclient import TestClient
from app.api.main import app


def test_websocket_alerts_subscription_and_push():
    client = TestClient(app)
    with client.websocket_connect("/ws/alerts") as websocket:
        # 1. Receive initial ACK
        data = websocket.receive_text()
        msg = json.loads(data)
        assert msg["type"] == "connection_ack"

        # 2. Update subscription
        websocket.send_text(json.dumps({
            "action": "subscribe",
            "filters": {"districts": ["Visakhapatnam"]}
        }))
        ack = json.loads(websocket.receive_text())
        assert ack["type"] == "subscription_ack"

        # 3. Trigger a simulation via REST endpoint
        sim_payload = {
            "raw_text": "RED ALERT: Super Cyclonic Storm with 130 km/h winds approaching Visakhapatnam coast.",
            "source": "IMD Cyclone Center",
            "affected_states": ["Andhra Pradesh"],
            "affected_districts": ["Visakhapatnam"]
        }
        res = client.post("/api/v1/alerts/simulate", json=sim_payload)
        assert res.status_code == 200

        # 4. Receive pushed alert via WebSocket
        alert_event_raw = websocket.receive_text()
        alert_event = json.loads(alert_event_raw)
        assert alert_event["type"] == "weather_alert"
        assert alert_event["alert"]["severity"] == "red"
        assert "Visakhapatnam" in alert_event["alert"]["affected_districts"]
