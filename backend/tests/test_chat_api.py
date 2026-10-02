"""
Integration tests for the conversational Chat API endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.api.main import app
from app.schemas.common import DomainRole


@pytest.mark.asyncio
async def test_chat_message_agriculture_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Can I harvest onions in Nashik today or will it rain?",
            "session_id": "test-session-agri",
            "role": "agriculture"
        }
        response = await client.post("/api/v1/chat/message", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert "answer" in data
        assert "Nashik" in data["answer"]
        assert data["role"] == DomainRole.AGRICULTURE.value
        assert "grounded_facts" in data
        assert data["grounded_facts"]["query_location"] == "Nashik"
        assert len(data["citations"]) > 0
        assert data["latency_ms"] > 0


@pytest.mark.asyncio
async def test_chat_message_marine_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "Are conditions safe for fishing boats off Visakhapatnam?",
            "session_id": "test-session-marine",
            "role": "marine"
        }
        response = await client.post("/api/v1/chat/message", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert "Visakhapatnam" in data["answer"]
        assert data["role"] == DomainRole.MARINE.value
        # Check that cyclone alert or wind data is captured
        assert "wind_speed_kmh" in data["grounded_facts"]


@pytest.mark.asyncio
async def test_ui_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Check root serving index.html
        res = await client.get("/")
        assert res.status_code == 200
        assert "WeatherGPT" in res.text

        # Check static style.css
        res_css = await client.get("/static/style.css")
        assert res_css.status_code == 200
        assert "--bg-primary" in res_css.text

        # Check static app.js
        res_js = await client.get("/static/app.js")
        assert res_js.status_code == 200
        assert "addEventListener" in res_js.text
