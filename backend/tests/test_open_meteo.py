"""
Tests for Open-Meteo observation and forecast connector.
"""

import pytest
from app.data_ingestion.open_meteo import OpenMeteoConnector, decode_wmo_code


def test_decode_wmo_code():
    assert "Clear" in decode_wmo_code(0)
    assert "Thunderstorm" in decode_wmo_code(95)
    assert "rain" in decode_wmo_code(65).lower()


@pytest.mark.asyncio
async def test_live_and_forecast_fetch():
    connector = OpenMeteoConnector()
    # Nashik coordinates
    lat, lon = 19.9975, 73.7898
    obs, forecast = await connector.get_live_and_forecast(lat, lon)

    # Validate observation
    assert obs is not None
    assert isinstance(obs.temperature_c, float)
    assert 0 <= obs.relative_humidity_pct <= 100
    assert obs.wind_speed_kmh >= 0
    assert obs.condition_text is not None

    # Validate forecast package
    assert forecast is not None
    assert len(forecast.daily) > 0
    assert len(forecast.hourly) > 0
    assert forecast.daily[0].temperature_max_c >= forecast.daily[0].temperature_min_c
