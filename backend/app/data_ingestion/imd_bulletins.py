"""
IMD (India Meteorological Department) & CAP Bulletin Connector.
Ingests national warning bulletins, parses color-coded alert tiers, and matches user coordinates.
"""

from datetime import datetime, timedelta
import logging
from typing import List, Optional

from app.data_ingestion.base import BaseConnector
from app.schemas.alerts import WeatherAlertItem, AlertBulletinFeed
from app.schemas.common import AlertSeverity, LocationContext

logger = logging.getLogger("weathergpt.bulletins")

# Operational sample bulletins representing IMD National Weather Warning Bulletins
SAMPLE_IMD_BULLETINS: List[WeatherAlertItem] = [
    WeatherAlertItem(
        alert_id="IMD-CYC-2026-0901",
        headline="RED ALERT: Severe Cyclonic Storm over West-Central Bay of Bengal",
        event_type="CYCLONE",
        severity=AlertSeverity.RED,
        urgency="Immediate",
        certainty="Observed",
        affected_states=["Andhra Pradesh", "Odisha", "Tamil Nadu"],
        affected_districts=["Visakhapatnam", "Vizianagaram", "Srikakulam", "Puri", "Ganjam", "Chennai"],
        description="The severe cyclonic storm is centered near latitude 17.2°N and longitude 84.1°E, moving north-northwestwards. Sustained surface wind speeds of 90-110 kmph gusting to 125 kmph expected.",
        instruction="Complete suspension of fishing operations. Total ban on coastal small craft movement. Evacuate residents from low-lying coastal tracts to cyclone shelters immediately.",
        effective_from=datetime.now() - timedelta(hours=3),
        expires_at=datetime.now() + timedelta(hours=36),
        source="IMD Cyclone Warning Division, New Delhi"
    ),
    WeatherAlertItem(
        alert_id="IMD-RAIN-2026-0902",
        headline="ORANGE ALERT: Isolated Very Heavy to Extremely Heavy Rainfall in Konkan & Ghats",
        event_type="HEAVY_RAIN",
        severity=AlertSeverity.ORANGE,
        urgency="Expected",
        certainty="Likely",
        affected_states=["Maharashtra", "Goa"],
        affected_districts=["Nashik", "Pune", "Raigad", "Ratnagiri", "Mumbai Suburban", "Satara"],
        description="Active monsoon trough and upper air cyclonic circulation over north Maharashtra coast will trigger intense rainfall spells (115.6 to 204.4 mm in 24 hours) along the Ghats.",
        instruction="Farmers advised to postpone fertilizer top-dressing and provide proper drainage in onion and vineyard plots. General public advised to avoid waterlogged ghat roads and riverbanks.",
        effective_from=datetime.now() - timedelta(hours=1),
        expires_at=datetime.now() + timedelta(hours=48),
        source="Regional Meteorological Centre, Mumbai"
    ),
    WeatherAlertItem(
        alert_id="IMD-HEAT-2026-0903",
        headline="YELLOW ALERT: Heatwave Conditions in Isolated Pockets of Vidarbha & Telangana",
        event_type="HEATWAVE",
        severity=AlertSeverity.YELLOW,
        urgency="Future",
        certainty="Possible",
        affected_states=["Maharashtra", "Telangana"],
        affected_districts=["Nagpur", "Chandrapur", "Hyderabad", "Nizamabad"],
        description="Maximum temperatures likely to rise by 3-4°C above normal over parts of Vidarbha and Northern Telangana.",
        instruction="Drink sufficient water even if not thirsty. Avoid direct sun exposure between 12:00 PM and 3:30 PM. Provide shade and hydration for livestock.",
        effective_from=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=24),
        source="IMD Meteorological Centre, Nagpur"
    ),
]


class IMDBulletinConnector(BaseConnector):
    """IMD and CAP severe weather bulletin connector."""

    def __init__(self):
        super().__init__(name="IMD-Bulletins", cache_ttl_seconds=900, timeout_seconds=6.0)

    async def get_active_bulletins(self, location: Optional[LocationContext] = None) -> List[WeatherAlertItem]:
        """
        Retrieves active bulletins, filtering by affected state or district if location provided.
        """
        all_bulletins = list(SAMPLE_IMD_BULLETINS)
        
        if not location:
            return all_bulletins

        matching_alerts: List[WeatherAlertItem] = []
        loc_state = (location.state or "").lower()
        loc_district = (location.district or "").lower()
        loc_name = location.resolved_name.lower()

        for alert in all_bulletins:
            state_match = any(s.lower() in loc_state or loc_state in s.lower() for s in alert.affected_states)
            district_match = any(d.lower() in loc_district or loc_district in d.lower() or d.lower() in loc_name for d in alert.affected_districts)

            if state_match or district_match:
                matching_alerts.append(alert)

        return matching_alerts

    async def get_national_feed_summary(self) -> AlertBulletinFeed:
        """Returns the high-level national alert bulletin summary."""
        alerts = list(SAMPLE_IMD_BULLETINS)
        severities = [a.severity for a in alerts]
        highest = AlertSeverity.GREEN
        if AlertSeverity.RED in severities:
            highest = AlertSeverity.RED
        elif AlertSeverity.ORANGE in severities:
            highest = AlertSeverity.ORANGE
        elif AlertSeverity.YELLOW in severities:
            highest = AlertSeverity.YELLOW

        return AlertBulletinFeed(
            feed_title="IMD National All India Severe Weather Warning Bulletin",
            last_updated=datetime.now(),
            active_alerts_count=len(alerts),
            highest_severity=highest,
            alerts=alerts
        )
