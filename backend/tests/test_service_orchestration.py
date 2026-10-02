"""
Integration tests for WeatherIntelligenceDataService producing UnifiedWeatherReport.
"""

import pytest
from app.data_ingestion.service import WeatherIntelligenceDataService
from app.schemas.common import DomainRole


@pytest.mark.asyncio
async def test_unified_report_agriculture_nashik():
    service = WeatherIntelligenceDataService()
    report = await service.get_unified_report(query="Nashik", role=DomainRole.AGRICULTURE)

    assert report is not None
    assert report.location.resolved_name == "Nashik"
    assert report.role == DomainRole.AGRICULTURE
    assert report.observation is not None
    assert report.forecast is not None
    assert report.nwp is not None
    assert len(report.citations) > 0

    # Test grounded facts for zero-hallucination guarantee
    facts = report.grounded_facts
    assert "current_temperature_c" in facts
    assert "relative_humidity_pct" in facts
    assert "role" in facts
    assert facts["role"] == "agriculture"


@pytest.mark.asyncio
async def test_unified_report_marine_visakhapatnam():
    service = WeatherIntelligenceDataService()
    report = await service.get_unified_report(query="Visakhapatnam", role=DomainRole.MARINE)

    assert report.location.resolved_name == "Visakhapatnam"
    assert report.role == DomainRole.MARINE
    assert any(a.event_type == "CYCLONE" for a in report.alerts)
