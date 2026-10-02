"""
Verification script for WeatherGPT web UI and backend APIs.
Tests that all browser user interface routes and API endpoints respond correctly.
"""

import sys
import asyncio
import httpx

from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.api.main import app

async def run_verification():
    print("=" * 70)
    print("  WEATHERGPT WEB USER INTERFACE & API VERIFICATION SUITE")
    print("=" * 70)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200, f"Health check failed: {res.status_code}"
        print(f"[✓] GET /health -> Status: {res.status_code}, Body: {res.json()}")

        # 2. UI Pages (HTML routes)
        ui_routes = ["/", "/chat", "/dashboard", "/alerts", "/climate", "/briefing"]
        for route in ui_routes:
            res = await client.get(route)
            assert res.status_code == 200, f"Failed for {route}: {res.status_code}"
            assert "WeatherGPT" in res.text, f"WeatherGPT missing in {route}"
            assert "view-chat" in res.text
            assert "view-dashboard" in res.text
            assert "view-alerts" in res.text
            assert "view-climate" in res.text
            assert "view-briefing" in res.text
            print(f"[✓] GET {route:<12} -> Status: 200 OK (Served HTML {len(res.text)} bytes)")

        # 3. Static assets
        res = await client.get("/static/style.css")
        assert res.status_code == 200, f"CSS failed: {res.status_code}"
        print(f"[✓] GET /static/style.css -> Status: 200 OK ({len(res.text)} bytes)")

        res = await client.get("/static/app.js")
        assert res.status_code == 200, f"JS failed: {res.status_code}"
        print(f"[✓] GET /static/app.js   -> Status: 200 OK ({len(res.text)} bytes)")

        # 4. Weather Report API (Dashboard backend)
        res = await client.get("/api/v1/weather/report?location=Pune&role=general")
        assert res.status_code == 200, f"Report failed: {res.status_code}"
        report = res.json()
        assert "observation" in report and "forecast" in report
        print(f"[✓] GET /api/v1/weather/report?location=Pune -> Status: 200 OK (Temp: {report['observation']['temperature_c']}°C)")

        # 5. Chat API
        res = await client.post("/api/v1/chat/message", json={
            "message": "Can I spray pesticide on crops in Nashik today?",
            "session_id": "test-session",
            "role": "agriculture",
            "language": "en"
        })
        assert res.status_code == 200, f"Chat message failed: {res.status_code}"
        chat_resp = res.json()
        assert "answer" in chat_resp and "grounded_facts" in chat_resp
        print(f"[✓] POST /api/v1/chat/message -> Status: 200 OK (Latency: {chat_resp['latency_ms']}ms)")

        # 6. Active Alerts API
        res = await client.get("/api/v1/alerts/active")
        assert res.status_code == 200
        alerts = res.json()
        print(f"[✓] GET /api/v1/alerts/active -> Status: 200 OK ({len(alerts)} active bulletins)")

        # 7. Alert Simulation API
        res = await client.post("/api/v1/alerts/simulate", json={
            "raw_text": "RED ALERT: Extremely Severe Cyclone landfall expected in coastal Odisha.",
            "source": "IMD Test Centre",
            "affected_states": ["Odisha"],
            "affected_districts": ["Puri", "Bhubaneswar"]
        })
        assert res.status_code == 200
        sim_alert = res.json()
        assert sim_alert["severity"] == "red"
        print(f"[✓] POST /api/v1/alerts/simulate -> Status: 200 OK (Classified: {sim_alert['severity'].upper()})")

        # 8. Climate Trends API
        res = await client.get("/api/v1/climate/trend-chart?location=Nashik&years=5")
        assert res.status_code == 200
        chart_spec = res.json()
        assert len(chart_spec["labels"]) >= 3
        print(f"[✓] GET /api/v1/climate/trend-chart?location=Nashik -> Status: 200 OK ({len(chart_spec['labels'])} years evaluated)")

    print("=" * 70)
    print("  ALL WEB UI AND BACKEND VERIFICATION CHECKS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_verification())
