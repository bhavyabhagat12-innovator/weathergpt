"""
Open-Meteo live observation and forecast connector.
Retrieves high-resolution hourly and 7-day daily forecasts including soil moisture for agriculture.
"""

from datetime import datetime, date
import logging
from typing import Tuple, Optional, Dict, Any

from app.config import settings
from app.data_ingestion.base import BaseConnector
from app.schemas.observation import ObservationSnapshot
from app.schemas.forecast import HourlyForecastItem, DailyForecastItem, ForecastPackage

logger = logging.getLogger("weathergpt.open_meteo")

WMO_WEATHER_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    62: "Moderate rain",
    63: "Moderate continuous rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm: slight or moderate",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


def decode_wmo_code(code: int) -> str:
    return WMO_WEATHER_MAP.get(code, "Variable weather")


class OpenMeteoConnector(BaseConnector):
    """Fetches real-time observations and forecasts from Open-Meteo."""

    def __init__(self):
        super().__init__(name="OpenMeteo", cache_ttl_seconds=600, timeout_seconds=7.0)

    async def get_live_and_forecast(
        self, latitude: float, longitude: float, timezone: str = "Asia/Kolkata"
    ) -> Tuple[ObservationSnapshot, ForecastPackage]:
        """
        Fetches live observation snapshot and multi-day forecast package.
        """
        cache_key = f"obs_fc_{latitude:.4f}_{longitude:.4f}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "surface_pressure",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
                "cloud_cover",
                "visibility",
                "uv_index"
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
                "wind_gusts_10m",
                "soil_moisture_0_to_7cm"
            ],
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "precipitation_sum",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "uv_index_max",
                "sunrise",
                "sunset"
            ],
            "timezone": timezone,
            "forecast_days": 7
        }

        data = await self.fetch_json(url, params=params)

        # 1. Parse Current Observation
        current_data = data.get("current", {})
        curr_time_raw = current_data.get("time")
        curr_timestamp = datetime.fromisoformat(curr_time_raw) if curr_time_raw else datetime.now()
        
        # Get latest hourly soil moisture if available
        soil_moisture = None
        hourly_data = data.get("hourly", {})
        if "soil_moisture_0_to_7cm" in hourly_data and hourly_data["soil_moisture_0_to_7cm"]:
            soil_moisture = hourly_data["soil_moisture_0_to_7cm"][0]

        weather_code = current_data.get("weather_code", 0)
        obs = ObservationSnapshot(
            timestamp=curr_timestamp,
            temperature_c=float(current_data.get("temperature_2m", 0.0)),
            apparent_temperature_c=float(current_data.get("apparent_temperature", 0.0)),
            relative_humidity_pct=float(current_data.get("relative_humidity_2m", 0.0)),
            surface_pressure_hpa=float(current_data.get("surface_pressure", 1013.25)),
            wind_speed_kmh=float(current_data.get("wind_speed_10m", 0.0)),
            wind_direction_deg=float(current_data.get("wind_direction_10m", 0.0)),
            wind_gust_kmh=float(current_data.get("wind_gusts_10m", 0.0)),
            precipitation_mm=float(current_data.get("precipitation", 0.0)),
            cloud_cover_pct=float(current_data.get("cloud_cover", 0.0)),
            visibility_km=float(current_data.get("visibility", 10000.0) / 1000.0) if current_data.get("visibility") else None,
            uv_index=float(current_data.get("uv_index", 0.0)) if current_data.get("uv_index") is not None else None,
            soil_moisture_0_7cm=float(soil_moisture) if soil_moisture is not None else None,
            weather_code=weather_code,
            condition_text=decode_wmo_code(weather_code),
            source="Open-Meteo High-Resolution (India Domain)"
        )

        # 2. Parse Hourly Forecast (first 48 hours)
        hourly_items = []
        times = hourly_data.get("time", [])
        temps = hourly_data.get("temperature_2m", [])
        humidities = hourly_data.get("relative_humidity_2m", [])
        precip_probs = hourly_data.get("precipitation_probability", [])
        precips = hourly_data.get("precipitation", [])
        w_codes = hourly_data.get("weather_code", [])
        winds = hourly_data.get("wind_speed_10m", [])
        gusts = hourly_data.get("wind_gusts_10m", [])

        limit = min(48, len(times))
        for i in range(limit):
            h_time = datetime.fromisoformat(times[i])
            w_code = w_codes[i] if i < len(w_codes) else 0
            hourly_items.append(
                HourlyForecastItem(
                    timestamp=h_time,
                    temperature_c=float(temps[i]),
                    relative_humidity_pct=float(humidities[i]),
                    precipitation_probability_pct=float(precip_probs[i]) if i < len(precip_probs) and precip_probs[i] is not None else 0.0,
                    precipitation_mm=float(precips[i]) if i < len(precips) and precips[i] is not None else 0.0,
                    wind_speed_kmh=float(winds[i]) if i < len(winds) and winds[i] is not None else 0.0,
                    wind_gust_kmh=float(gusts[i]) if i < len(gusts) and gusts[i] is not None else None,
                    weather_code=w_code,
                    condition_text=decode_wmo_code(w_code)
                )
            )

        # 3. Parse Daily Forecast (7 days)
        daily_items = []
        daily_data = data.get("daily", {})
        d_times = daily_data.get("time", [])
        d_min_temps = daily_data.get("temperature_2m_min", [])
        d_max_temps = daily_data.get("temperature_2m_max", [])
        d_precip_sums = daily_data.get("precipitation_sum", [])
        d_precip_probs = daily_data.get("precipitation_probability_max", [])
        d_winds = daily_data.get("wind_speed_10m_max", [])
        d_gusts = daily_data.get("wind_gusts_10m_max", [])
        d_codes = daily_data.get("weather_code", [])
        d_uvs = daily_data.get("uv_index_max", [])
        sunrises = daily_data.get("sunrise", [])
        sunsets = daily_data.get("sunset", [])

        for i in range(len(d_times)):
            f_date = date.fromisoformat(d_times[i])
            w_code = d_codes[i] if i < len(d_codes) else 0
            sr = datetime.fromisoformat(sunrises[i]) if i < len(sunrises) and sunrises[i] else None
            ss = datetime.fromisoformat(sunsets[i]) if i < len(sunsets) and sunsets[i] else None

            daily_items.append(
                DailyForecastItem(
                    forecast_date=f_date,
                    temperature_min_c=float(d_min_temps[i]),
                    temperature_max_c=float(d_max_temps[i]),
                    precipitation_sum_mm=float(d_precip_sums[i]) if i < len(d_precip_sums) and d_precip_sums[i] is not None else 0.0,
                    precipitation_probability_max_pct=float(d_precip_probs[i]) if i < len(d_precip_probs) and d_precip_probs[i] is not None else 0.0,
                    wind_speed_max_kmh=float(d_winds[i]) if i < len(d_winds) and d_winds[i] is not None else 0.0,
                    wind_gusts_max_kmh=float(d_gusts[i]) if i < len(d_gusts) and d_gusts[i] is not None else None,
                    dominant_weather_code=w_code,
                    condition_text=decode_wmo_code(w_code),
                    uv_index_max=float(d_uvs[i]) if i < len(d_uvs) and d_uvs[i] is not None else None,
                    sunrise=sr,
                    sunset=ss
                )
            )

        forecast_pkg = ForecastPackage(
            hourly=hourly_items,
            daily=daily_items,
            source="Open-Meteo High-Resolution (7-Day Multi-Variable)"
        )

        result = (obs, forecast_pkg)
        self._set_in_cache(cache_key, result)
        return result
