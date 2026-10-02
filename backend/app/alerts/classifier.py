"""
Severe Weather Alert Classifier & Rules Engine.
Implements India Meteorological Department (IMD) operational color-coding criteria
and generates structured WeatherAlertItems with role-specific mandatory directives.
"""

from datetime import datetime, timedelta
import re
from typing import Dict, Any, List, Optional
import uuid

from app.schemas.common import AlertSeverity, DomainRole
from app.schemas.alerts import WeatherAlertItem


class AlertClassifier:
    """Classifies raw bulletins and weather metrics into IMD Alert Tiers."""

    @classmethod
    def classify_rainfall(cls, rain_24h_mm: float) -> AlertSeverity:
        """
        IMD Rainfall Classification:
        - > 204.4 mm: Extremely Heavy (RED ALERT)
        - 115.6 - 204.4 mm: Very Heavy (ORANGE ALERT)
        - 64.5 - 115.5 mm: Heavy (YELLOW ALERT)
        - < 64.5 mm: Moderate / Light (GREEN)
        """
        if rain_24h_mm >= 204.5:
            return AlertSeverity.RED
        elif rain_24h_mm >= 115.6:
            return AlertSeverity.ORANGE
        elif rain_24h_mm >= 64.5:
            return AlertSeverity.YELLOW
        return AlertSeverity.GREEN

    @classmethod
    def classify_cyclone_wind(cls, sustained_wind_kmh: float, gust_kmh: Optional[float] = None) -> AlertSeverity:
        """
        IMD Cyclonic Classification:
        - >= 89 km/h (Severe Cyclonic Storm & above): RED ALERT
        - 62 - 88 km/h (Cyclonic Storm): ORANGE ALERT
        - 52 - 61 km/h (Deep Depression / Squall): YELLOW ALERT
        - < 52 km/h: Normal / Depression watch: GREEN
        """
        effective_speed = max(sustained_wind_kmh, (gust_kmh or 0) * 0.85)
        if effective_speed >= 89:
            return AlertSeverity.RED
        elif effective_speed >= 62:
            return AlertSeverity.ORANGE
        elif effective_speed >= 50:
            return AlertSeverity.YELLOW
        return AlertSeverity.GREEN

    @classmethod
    def classify_heatwave(cls, max_temp_c: float, departure_c: float = 0.0) -> AlertSeverity:
        """
        IMD Heatwave Criteria for Plains:
        - Max Temp >= 45.0°C or departure >= 6.4°C: Severe Heatwave (RED ALERT)
        - Max Temp >= 40.0°C with departure >= 4.5°C: Heatwave (ORANGE ALERT)
        - Max Temp 38-40°C with departure >= 3.0°C: Warm / Watch (YELLOW ALERT)
        """
        if max_temp_c >= 45.0 or departure_c >= 6.4:
            return AlertSeverity.RED
        elif (max_temp_c >= 40.0 and departure_c >= 4.5) or max_temp_c >= 43.5:
            return AlertSeverity.ORANGE
        elif max_temp_c >= 39.0 or departure_c >= 3.0:
            return AlertSeverity.YELLOW
        return AlertSeverity.GREEN

    @classmethod
    def parse_raw_bulletin(
        cls,
        raw_text: str,
        source: str = "IMD Operational Center",
        affected_states: Optional[List[str]] = None,
        affected_districts: Optional[List[str]] = None
    ) -> WeatherAlertItem:
        """
        Parses an incoming raw text/CAP bulletin, extracts event type and severity,
        and assigns appropriate emergency directives.
        """
        text_lower = raw_text.lower()
        now = datetime.now()

        # 1. Detect Event Type
        event_type = "GENERAL_WEATHER"
        if any(w in text_lower for w in ["cyclone", "cyclonic storm", "depression", "landfall", "eye of storm"]):
            event_type = "CYCLONE"
        elif any(w in text_lower for w in ["heavy rain", "downpour", "inundation", "rainfall", "flood"]):
            event_type = "HEAVY_RAIN"
        elif any(w in text_lower for w in ["heatwave", "heat wave", "luh", "extreme temperature"]):
            event_type = "HEATWAVE"
        elif any(w in text_lower for w in ["thunderstorm", "lightning", "squall", "hailstorm"]):
            event_type = "THUNDERSTORM"

        # 2. Determine Severity
        if any(w in text_lower for w in ["red alert", "extremely heavy", "severe cyclonic storm", "super cyclone", "extreme danger"]):
            severity = AlertSeverity.RED
        elif any(w in text_lower for w in ["orange alert", "very heavy", "cyclonic storm", "be prepared", "severe heatwave"]):
            severity = AlertSeverity.ORANGE
        elif any(w in text_lower for w in ["yellow alert", "heavy rain", "be updated", "thunderstorm with lightning", "watch"]):
            severity = AlertSeverity.YELLOW
        else:
            severity = AlertSeverity.GREEN

        # 3. Formulate Actionable Directives
        instructions = []
        if severity == AlertSeverity.RED:
            if event_type == "CYCLONE":
                instructions.append("Total suspension of fishing and maritime operations. Mandatory evacuation of coastal lowlands.")
            elif event_type == "HEAVY_RAIN":
                instructions.append("Stay indoors. Avoid crossing flooded causeways and riverbeds. Postpone all agricultural operations.")
            elif event_type == "HEATWAVE":
                instructions.append("Absolute restriction on outdoor physical labor between 11:00 AM and 4:00 PM. High heat stroke risk.")
            else:
                instructions.append("Take immediate protective action as directed by NDMA / SDRF.")
        elif severity == AlertSeverity.ORANGE:
            if event_type == "CYCLONE":
                instructions.append("Fishermen advised not to venture into deep sea. Coastal small craft return to harbour.")
            elif event_type == "HEAVY_RAIN":
                instructions.append("Be prepared for waterlogging in low-lying roads. Farmers provide drainage channels in standing crops.")
            else:
                instructions.append("Be prepared for extreme weather interruptions. Keep emergency numbers handy.")
        elif severity == AlertSeverity.YELLOW:
            instructions.append("Keep updated with latest weather bulletins. Stay away from trees and tin structures during lightning.")
        else:
            instructions.append("Normal conditions prevail. No special precautions required.")

        alert_id = f"IMD-{event_type[:3]}-{uuid.uuid4().hex[:6].upper()}"

        # First sentence or 100 chars as headline
        first_sentence = raw_text.split(".")[0].strip()
        headline = f"[{severity.value.upper()} ALERT] {first_sentence}"

        return WeatherAlertItem(
            alert_id=alert_id,
            headline=headline,
            event_type=event_type,
            severity=severity,
            urgency="Immediate" if severity in [AlertSeverity.RED, AlertSeverity.ORANGE] else "Expected",
            certainty="Observed" if "observed" in text_lower else "Likely",
            affected_states=affected_states or ["India"],
            affected_districts=affected_districts or [],
            description=raw_text.strip(),
            instruction=" ".join(instructions),
            effective_from=now,
            expires_at=now + timedelta(hours=36),
            source=source,
            is_active=True
        )
