"""
Demo script: Real-time Cyclone Bulletin Simulation & WebSocket Push Dispatch.
Simulates an incoming IMD Special Tropical Cyclone Bulletin for the Bay of Bengal
and verifies instant proactive push notification delivery to a connected client.
"""

import asyncio
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend directory is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from starlette.testclient import TestClient
from app.api.main import app


def run_cyclone_simulation_demo():
    print("=" * 85)
    print("  WEATHERGPT REAL-TIME CYCLONE BULLETIN SIMULATION & WEBSOCKET DISPATCH")
    print("=" * 85)

    client = TestClient(app)

    print("\n[STEP 1] Establishing WebSocket Client Connection to /ws/alerts...")
    with client.websocket_connect("/ws/alerts") as ws:
        ack_data = json.loads(ws.receive_text())
        print(f"  --> Client Connected! Handshake ACK: {ack_data.get('message')}")

        print("\n[STEP 2] Subscribing Client to Maritime & Coastal District Topics...")
        ws.send_text(json.dumps({
            "action": "subscribe",
            "filters": {
                "districts": ["Visakhapatnam", "Puri", "Srikakulam"],
                "roles": ["marine", "disaster_management"]
            }
        }))
        sub_ack = json.loads(ws.receive_text())
        print(f"  --> Subscription Confirmed for Districts: {sub_ack.get('filters', {}).get('districts')}")

        print("\n[STEP 3] Ingesting Simulated IMD Severe Tropical Cyclone Bulletin...")
        bulletin_text = (
            "IMD CYCLONE BULLETIN NO. 14: Very Severe Cyclonic Storm 'MOCHA' over West-Central Bay of Bengal. "
            "Moving north-northeastwards with sustained surface wind speeds of 135 kmph gusting to 155 kmph. "
            "Landfall expected near north Andhra and south Odisha coasts within next 18 hours. "
            "RED ALERT ISSUED: Total suspension of fishing operations, storm surge inundation of lowlands expected."
        )
        print("  Raw Bulletin Incoming:")
        print(f"  \"{bulletin_text}\"")

        # Post simulation via REST
        sim_response = client.post("/api/v1/alerts/simulate", json={
            "raw_text": bulletin_text,
            "source": "IMD Cyclone Warning Division, New Delhi",
            "affected_states": ["Andhra Pradesh", "Odisha"],
            "affected_districts": ["Visakhapatnam", "Vizianagaram", "Srikakulam", "Puri", "Ganjam"]
        })

        if sim_response.status_code == 200:
            classified = sim_response.json()
            print(f"\n[STEP 4] Severity Classifier Output:")
            print(f"  - Alert ID: {classified['alert_id']}")
            print(f"  - Classified Severity: [{classified['severity'].upper()}]")
            print(f"  - Event Type: {classified['event_type']}")
            print(f"  - Affected Districts: {', '.join(classified['affected_districts'])}")
            print(f"  - Directive: {classified['instruction']}")

        print("\n[STEP 5] Checking Real-time WebSocket Push Notification Reception...")
        pushed_raw = ws.receive_text()
        pushed_event = json.loads(pushed_raw)
        print("  --> Alert Received by Subscriber over WebSocket!")
        print(f"      Event Type: {pushed_event['type']}")
        print(f"      Pushed Headline: {pushed_event['alert']['headline']}")
        print(f"      Broadcast Time: {pushed_event['broadcast_timestamp']}")

    print("\n" + "=" * 85)
    print("  CYCLONE BULLETIN SIMULATION & REAL-TIME DISPATCH COMPLETED SUCCESSFULLY")
    print("=" * 85)


if __name__ == "__main__":
    run_cyclone_simulation_demo()
