"""
WebSocket Alert Connection Manager & Topic Dispatcher.
Maintains live subscriber connections and pushes proactive weather warnings in real time.
"""

import json
import logging
from typing import Dict, List, Set, Optional, Any
from fastapi import WebSocket


from app.schemas.alerts import WeatherAlertItem

logger = logging.getLogger("weathergpt.alerts.dispatcher")


class AlertDispatcher:
    """Manages active WebSockets and dispatches alerts to subscribers."""

    def __init__(self):
        # Maps websocket to subscription filters (districts, states, roles)
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, filters: Optional[Dict[str, Any]] = None):
        """Accepts WebSocket connection and records subscription preferences."""
        await websocket.accept()
        self.active_connections[websocket] = filters or {
            "districts": [],
            "states": [],
            "roles": []
        }
        logger.info(f"WebSocket client connected. Active subscribers: {len(self.active_connections)}")

    def update_subscription(self, websocket: WebSocket, filters: Dict[str, Any]):
        """Updates subscription filters for a client."""
        if websocket in self.active_connections:
            self.active_connections[websocket] = filters

    def disconnect(self, websocket: WebSocket):
        """Removes disconnected WebSocket client."""
        if websocket in self.active_connections:
            del self.active_connections[websocket]
            logger.info(f"WebSocket client disconnected. Active subscribers: {len(self.active_connections)}")

    async def broadcast_alert(self, alert: WeatherAlertItem) -> int:
        """
        Dispatches an alert to all matching connected clients.
        Returns the number of clients that received the alert.
        """
        if not self.active_connections:
            logger.info("No active WebSocket subscribers to receive broadcast.")
            return 0

        payload = {
            "type": "weather_alert",
            "alert": alert.model_dump(mode="json"),
            "broadcast_timestamp": alert.effective_from.isoformat()
        }
        text_payload = json.dumps(payload)

        delivered = 0
        dead_connections = []

        for ws, filters in list(self.active_connections.items()):
            try:
                # Check subscription filters
                should_send = self._matches_filter(alert, filters)
                if should_send:
                    await ws.send_text(text_payload)
                    delivered += 1
            except Exception as e:
                logger.warning(f"Error sending alert to WebSocket client: {e}")
                dead_connections.append(ws)

        for ws in dead_connections:
            self.disconnect(ws)

        logger.info(f"Dispatched alert '{alert.alert_id}' to {delivered} subscribers.")
        return delivered

    def _matches_filter(self, alert: WeatherAlertItem, filters: Dict[str, Any]) -> bool:
        """Evaluates whether an alert matches a client's subscription filters."""
        # If no specific filters, deliver all alerts
        districts = [d.lower() for d in filters.get("districts", [])]
        states = [s.lower() for s in filters.get("states", [])]

        if not districts and not states:
            return True

        alert_districts = [d.lower() for d in alert.affected_districts]
        alert_states = [s.lower() for s in alert.affected_states]

        # Match district or state
        if any(d in alert_districts for d in districts):
            return True
        if any(s in alert_states for s in states):
            return True

        return False


# Global dispatcher singleton
alert_dispatcher = AlertDispatcher()
