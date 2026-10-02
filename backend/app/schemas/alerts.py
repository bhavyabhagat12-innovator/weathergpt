"""
Alerts & Bulletin schemas (IMD, NDMA, GDACS Common Alerting Protocol).
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.common import AlertSeverity


class WeatherAlertItem(BaseModel):
    alert_id: str
    headline: str
    event_type: str = Field(..., description="e.g. CYCLONE, HEAVY_RAIN, HEATWAVE, THUNDERSTORM")
    severity: AlertSeverity = AlertSeverity.GREEN
    urgency: str = Field(default="Immediate", description="Immediate, Expected, Future, Past")
    certainty: str = Field(default="Observed", description="Observed, Likely, Possible, Unlikely")
    affected_states: List[str] = Field(default_factory=list)
    affected_districts: List[str] = Field(default_factory=list)
    description: str
    instruction: Optional[str] = None
    effective_from: datetime
    expires_at: datetime
    source: str = Field(default="India Meteorological Department (IMD)")
    is_active: bool = True


class AlertBulletinFeed(BaseModel):
    feed_title: str = "IMD National Severe Weather Bulletin"
    last_updated: datetime
    active_alerts_count: int = 0
    highest_severity: AlertSeverity = AlertSeverity.GREEN
    alerts: List[WeatherAlertItem] = Field(default_factory=list)
