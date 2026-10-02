"""
Tests for IMD bulletin parser and district alert filtering.
"""

import pytest
from app.data_ingestion.imd_bulletins import IMDBulletinConnector
from app.data_ingestion.geocoding import IndiaGeocodingConnector
from app.schemas.common import AlertSeverity, DomainRole


@pytest.mark.asyncio
async def test_national_bulletin_feed():
    connector = IMDBulletinConnector()
    feed = await connector.get_national_feed_summary()
    assert feed.active_alerts_count > 0
    assert feed.highest_severity in [AlertSeverity.RED, AlertSeverity.ORANGE, AlertSeverity.YELLOW]


@pytest.mark.asyncio
async def test_district_filtered_alerts():
    geocoder = IndiaGeocodingConnector()
    bulletin_conn = IMDBulletinConnector()

    # Visakhapatnam should receive Cyclone Red Alert
    vizag_loc = await geocoder.resolve_location("Visakhapatnam", role=DomainRole.MARINE)
    vizag_alerts = await bulletin_conn.get_active_bulletins(vizag_loc)
    assert len(vizag_alerts) >= 1
    assert any(a.event_type == "CYCLONE" for a in vizag_alerts)

    # Nashik should receive Heavy Rain Orange Alert
    nashik_loc = await geocoder.resolve_location("Nashik", role=DomainRole.AGRICULTURE)
    nashik_alerts = await bulletin_conn.get_active_bulletins(nashik_loc)
    assert len(nashik_alerts) >= 1
    assert any(a.event_type == "HEAVY_RAIN" for a in nashik_alerts)
