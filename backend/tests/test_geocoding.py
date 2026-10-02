"""
Tests for India geocoding connector and fallback handling.
"""

import pytest
from app.data_ingestion.geocoding import IndiaGeocodingConnector
from app.schemas.common import DomainRole


@pytest.mark.asyncio
async def test_resolve_nashik_offline_catalog():
    geocoder = IndiaGeocodingConnector()
    # Test resolving Nashik
    loc = await geocoder.resolve_location("Nashik", role=DomainRole.AGRICULTURE)
    assert loc.resolved_name == "Nashik"
    assert loc.state == "Maharashtra"
    assert loc.latitude > 19.0 and loc.latitude < 21.0
    assert loc.longitude > 73.0 and loc.longitude < 75.0
    assert loc.role == DomainRole.AGRICULTURE


@pytest.mark.asyncio
async def test_resolve_visakhapatnam_marine():
    geocoder = IndiaGeocodingConnector()
    # Test resolving Visakhapatnam / Vizag
    loc = await geocoder.resolve_location("Vizag", role=DomainRole.MARINE)
    assert loc.resolved_name == "Visakhapatnam"
    assert loc.state == "Andhra Pradesh"
    assert loc.latitude > 17.0 and loc.latitude < 18.5
    assert loc.role == DomainRole.MARINE


@pytest.mark.asyncio
async def test_geocoding_cache():
    geocoder = IndiaGeocodingConnector()
    loc1 = await geocoder.resolve_location("Chennai")
    loc2 = await geocoder.resolve_location("chennai")
    assert loc1.resolved_name == loc2.resolved_name
    assert loc1.latitude == loc2.latitude
