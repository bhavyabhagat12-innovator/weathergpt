"""
Unified Weather Intelligence Data Ingestion Service.
Orchestrates geocoding, live obs, forecasts, NWP grids, alerts, and climate data concurrently.
Assembles the UnifiedWeatherReport with strict ground-truth facts for LLM reasoning.
"""

import asyncio
from datetime import datetime
import logging
import uuid
from typing import Optional, List, Dict, Any

from app.schemas.common import LocationContext, DomainRole
from app.schemas.unified import UnifiedWeatherReport
from app.data_ingestion.geocoding import IndiaGeocodingConnector
from app.data_ingestion.open_meteo import OpenMeteoConnector
from app.data_ingestion.nwp_gfs import NWPModelConnector
from app.data_ingestion.imd_bulletins import IMDBulletinConnector
from app.data_ingestion.climate_archive import ClimateArchiveConnector

logger = logging.getLogger("weathergpt.service")


class WeatherIntelligenceDataService:
    """Orchestrator for all weather intelligence data pipelines."""

    def __init__(self):
        self.geocoder = IndiaGeocodingConnector()
        self.meteo = OpenMeteoConnector()
        self.nwp = NWPModelConnector()
        self.bulletins = IMDBulletinConnector()
        self.climate = ClimateArchiveConnector()

    async def get_unified_report(
        self,
        query: str,
        role: DomainRole = DomainRole.GENERAL,
        include_climate: bool = True
    ) -> UnifiedWeatherReport:
        """
        Main entry point: Geocodes location, then asynchronously fetches
        live observations, forecasts, NWP stability fields, active alerts, and climate context.
        """
        report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
        citations: List[str] = []
        degraded: List[str] = []

        # 1. Geocode location
        try:
            location = await self.geocoder.resolve_location(query, role=role)
            citations.append("Open-Meteo Geocoding / Survey of India Catalog")
        except Exception as e:
            logger.error(f"Geocoding failed for {query}: {e}")
            raise RuntimeError(f"Unable to resolve location for query '{query}'")

        lat = location.latitude
        lon = location.longitude

        # 2. Concurrently fetch all weather subsystems
        tasks = [
            self._safe_fetch_obs_forecast(lat, lon, location.timezone),
            self._safe_fetch_nwp(lat, lon),
            self._safe_fetch_alerts(location),
        ]
        if include_climate:
            tasks.append(self._safe_fetch_climate(lat, lon))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Unpack observations & forecast
        obs_res = results[0]
        obs, forecast = None, None
        if isinstance(obs_res, tuple):
            obs, forecast = obs_res
            citations.append(obs.source)
            citations.append(forecast.source)
        else:
            degraded.append("Live Observations & Forecast Service")

        # Unpack NWP
        nwp_res = results[1]
        nwp = None
        if hasattr(nwp_res, "model_name"):
            nwp = nwp_res
            citations.append(nwp.model_name)
        else:
            degraded.append("NWP Atmospheric Stability Grid")

        # Unpack Alerts
        alerts_res = results[2]
        alerts = []
        if isinstance(alerts_res, list):
            alerts = alerts_res
            citations.append("India Meteorological Department (IMD) Severe Weather Feed")
        else:
            degraded.append("IMD Alert Bulletin Feed")

        # Unpack Climate
        climate = None
        if include_climate and len(results) > 3:
            climate_res = results[3]
            if hasattr(climate_res, "historical_avg_temp_c"):
                climate = climate_res
                citations.append("Open-Meteo ERA5 Climate Reanalysis")
            else:
                degraded.append("Historical Climate Archive")

        # 3. Compile ground-truth facts table for zero-hallucination LLM grounding
        grounded_facts: Dict[str, Any] = {
            "query_location": location.resolved_name,
            "district": location.district,
            "state": location.state,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "role": role.value,
        }

        if obs:
            grounded_facts.update({
                "current_temperature_c": obs.temperature_c,
                "current_feels_like_c": obs.apparent_temperature_c,
                "relative_humidity_pct": obs.relative_humidity_pct,
                "wind_speed_kmh": obs.wind_speed_kmh,
                "wind_gust_kmh": obs.wind_gust_kmh,
                "wind_direction_deg": obs.wind_direction_deg,
                "current_precipitation_mm": obs.precipitation_mm,
                "soil_moisture_0_7cm": obs.soil_moisture_0_7cm,
                "uv_index": obs.uv_index,
                "visibility_km": obs.visibility_km,
                "weather_condition": obs.condition_text
            })

        if forecast and forecast.daily:
            today_fc = forecast.daily[0]
            grounded_facts.update({
                "forecast_today_min_temp_c": today_fc.temperature_min_c,
                "forecast_today_max_temp_c": today_fc.temperature_max_c,
                "forecast_today_rain_sum_mm": today_fc.precipitation_sum_mm,
                "forecast_today_rain_probability_pct": today_fc.precipitation_probability_max_pct,
                "forecast_today_max_wind_kmh": today_fc.wind_speed_max_kmh
            })

        if nwp:
            grounded_facts.update({
                "nwp_cape_j_kg": nwp.cape_j_kg,
                "nwp_lifted_index": nwp.lifted_index_c,
                "convective_storm_risk": nwp.convective_risk
            })

        grounded_facts["active_alerts_count"] = len(alerts)
        if alerts:
            grounded_facts["highest_alert_severity"] = max(a.severity.value for a in alerts)
            grounded_facts["active_alert_headlines"] = [a.headline for a in alerts]

        return UnifiedWeatherReport(
            report_id=report_id,
            generated_at=datetime.now(),
            location=location,
            role=role,
            observation=obs,
            forecast=forecast,
            nwp=nwp,
            alerts=alerts,
            climate=climate,
            grounded_facts=grounded_facts,
            citations=list(set(citations)),
            degraded_sources=degraded,
            is_live_data=len(degraded) == 0
        )

    async def _safe_fetch_obs_forecast(self, lat: float, lon: float, tz: str):
        try:
            return await self.meteo.get_live_and_forecast(lat, lon, tz)
        except Exception as e:
            logger.error(f"Error fetching obs & forecast: {e}")
            return None

    async def _safe_fetch_nwp(self, lat: float, lon: float):
        try:
            return await self.nwp.get_gfs_diagnostics(lat, lon)
        except Exception as e:
            logger.error(f"Error fetching NWP: {e}")
            return None

    async def _safe_fetch_alerts(self, location: LocationContext):
        try:
            return await self.bulletins.get_active_bulletins(location)
        except Exception as e:
            logger.error(f"Error fetching bulletins: {e}")
            return []

    async def _safe_fetch_climate(self, lat: float, lon: float):
        try:
            return await self.climate.get_climate_context(lat, lon)
        except Exception as e:
            logger.error(f"Error fetching climate context: {e}")
            return None
