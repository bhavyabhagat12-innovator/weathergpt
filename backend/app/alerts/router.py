"""
Alerts and WebSocket API router.
Enables real-time push notification subscriptions and bulletin simulations.
"""

import json
import logging
from typing import Optional, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field

from app.schemas.alerts import WeatherAlertItem
from app.alerts.classifier import AlertClassifier
from app.alerts.dispatcher import alert_dispatcher
from app.data_ingestion.imd_bulletins import SAMPLE_IMD_BULLETINS

logger = logging.getLogger("weathergpt.alerts.router")
router = APIRouter(tags=["alerts"])

# In-memory store of active simulated alerts
ACTIVE_SIMULATED_ALERTS: List[WeatherAlertItem] = list(SAMPLE_IMD_BULLETINS)


class BulletinSimulationRequest(BaseModel):
    raw_text: str = Field(..., description="Raw text of official IMD or disaster bulletin")
    source: str = Field(default="IMD National Cyclone Warning Centre", description="Issuing meteorological center")
    affected_states: List[str] = Field(default_factory=lambda: ["Andhra Pradesh", "Odisha"], description="Affected states")
    affected_districts: List[str] = Field(default_factory=lambda: ["Visakhapatnam", "Puri"], description="Affected districts")


@router.websocket("/ws/alerts")
async def websocket_alerts_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time proactive weather warnings.
    Client can optionally send subscription preferences as JSON:
    {"districts": ["Visakhapatnam", "Nashik"], "states": ["Maharashtra"]}
    """
    await alert_dispatcher.connect(websocket)
    try:
        # Send initial confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_ack",
            "message": "Connected to WeatherGPT Real-Time Alert Dispatcher",
            "active_alerts_count": len(ACTIVE_SIMULATED_ALERTS)
        }))

        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "subscribe":
                    alert_dispatcher.update_subscription(websocket, msg.get("filters", {}))
                    await websocket.send_text(json.dumps({
                        "type": "subscription_ack",
                        "filters": msg.get("filters")
                    }))
            except Exception:
                pass
    except WebSocketDisconnect:
        alert_dispatcher.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        alert_dispatcher.disconnect(websocket)


@router.post("/api/v1/alerts/simulate", response_model=WeatherAlertItem)
async def simulate_incoming_bulletin(req: BulletinSimulationRequest):
    """
    Simulates receipt of an operational meteorological bulletin.
    Classifies severity, logs alert, and pushes it via WebSocket to active subscribers.
    """
    try:
        alert = AlertClassifier.parse_raw_bulletin(
            raw_text=req.raw_text,
            source=req.source,
            affected_states=req.affected_states,
            affected_districts=req.affected_districts
        )

        ACTIVE_SIMULATED_ALERTS.insert(0, alert)
        # Broadcast immediately to connected WebSocket clients
        delivered = await alert_dispatcher.broadcast_alert(alert)

        logger.info(f"Simulated bulletin classified as {alert.severity.value.upper()} and delivered to {delivered} subscribers.")
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process bulletin: {str(e)}")


@router.get("/api/v1/alerts/active", response_model=List[WeatherAlertItem])
async def get_active_alerts():
    """Returns all currently active severe weather alerts."""
    return ACTIVE_SIMULATED_ALERTS
