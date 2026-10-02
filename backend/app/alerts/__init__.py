"""
Alerts module exports.
"""

from app.alerts.classifier import AlertClassifier
from app.alerts.dispatcher import AlertDispatcher, alert_dispatcher
from app.alerts.router import router as alerts_router

__all__ = ["AlertClassifier", "AlertDispatcher", "alert_dispatcher", "alerts_router"]
