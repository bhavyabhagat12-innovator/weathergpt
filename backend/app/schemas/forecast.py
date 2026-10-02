"""
Forecast schemas for hourly and multi-day weather predictions.
"""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field


class HourlyForecastItem(BaseModel):
    timestamp: datetime
    temperature_c: float
    relative_humidity_pct: float
    precipitation_probability_pct: float = Field(default=0.0, ge=0, le=100)
    precipitation_mm: float = Field(default=0.0, ge=0)
    wind_speed_kmh: float
    wind_gust_kmh: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    cloud_cover_pct: Optional[float] = None
    weather_code: int = 0
    condition_text: str = "Clear"


class DailyForecastItem(BaseModel):
    forecast_date: date
    temperature_min_c: float
    temperature_max_c: float
    apparent_temperature_min_c: Optional[float] = None
    apparent_temperature_max_c: Optional[float] = None
    precipitation_sum_mm: float = Field(default=0.0, ge=0)
    precipitation_probability_max_pct: float = Field(default=0.0, ge=0, le=100)
    wind_speed_max_kmh: float = Field(default=0.0, ge=0)
    wind_gusts_max_kmh: Optional[float] = None
    dominant_weather_code: int = 0
    condition_text: str = "Clear"
    uv_index_max: Optional[float] = None
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None


class ForecastPackage(BaseModel):
    hourly: List[HourlyForecastItem] = Field(default_factory=list)
    daily: List[DailyForecastItem] = Field(default_factory=list)
    source: str = "Open-Meteo High-Resolution Model"
