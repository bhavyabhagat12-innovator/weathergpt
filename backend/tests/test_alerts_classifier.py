"""
Tests for IMD alert severity rules engine and bulletin parsing.
"""

import pytest
from app.schemas.common import AlertSeverity
from app.alerts.classifier import AlertClassifier


def test_rainfall_classification_thresholds():
    # Extreme > 204.4 mm
    assert AlertClassifier.classify_rainfall(215.0) == AlertSeverity.RED
    # Very Heavy 115.6 - 204.4 mm
    assert AlertClassifier.classify_rainfall(145.2) == AlertSeverity.ORANGE
    # Heavy 64.5 - 115.5 mm
    assert AlertClassifier.classify_rainfall(85.0) == AlertSeverity.YELLOW
    # Normal / Moderate
    assert AlertClassifier.classify_rainfall(35.0) == AlertSeverity.GREEN


def test_cyclone_wind_thresholds():
    # Severe Cyclonic Storm >= 89 km/h
    assert AlertClassifier.classify_cyclone_wind(95.0) == AlertSeverity.RED
    # Cyclonic Storm 62 - 88 km/h
    assert AlertClassifier.classify_cyclone_wind(75.0) == AlertSeverity.ORANGE
    # Deep Depression 50 - 61 km/h
    assert AlertClassifier.classify_cyclone_wind(55.0) == AlertSeverity.YELLOW
    # Moderate breeze
    assert AlertClassifier.classify_cyclone_wind(30.0) == AlertSeverity.GREEN


def test_heatwave_thresholds():
    # Extreme heat >= 45°C
    assert AlertClassifier.classify_heatwave(46.2) == AlertSeverity.RED
    # Heatwave >= 40°C with anomaly
    assert AlertClassifier.classify_heatwave(42.0, departure_c=5.1) == AlertSeverity.ORANGE
    # Normal summer
    assert AlertClassifier.classify_heatwave(36.0, departure_c=1.0) == AlertSeverity.GREEN


def test_raw_bulletin_parsing():
    raw_text = (
        "IMD Special Bulletin: Severe cyclonic storm approaching north Andhra coast near Visakhapatnam. "
        "Gale wind speed reaching 100-110 kmph gusting to 125 kmph observed over west-central Bay of Bengal. "
        "Red Alert issued. Coastal inundation expected."
    )
    alert = AlertClassifier.parse_raw_bulletin(
        raw_text=raw_text,
        source="IMD Cyclone Warning Division",
        affected_states=["Andhra Pradesh"],
        affected_districts=["Visakhapatnam", "Srikakulam"]
    )

    assert alert.severity == AlertSeverity.RED
    assert alert.event_type == "CYCLONE"
    assert "Visakhapatnam" in alert.affected_districts
    assert "suspension of fishing" in alert.instruction.lower()
