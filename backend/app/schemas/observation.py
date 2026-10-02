"""
Observation schema for live weather conditions.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ObservationSnapshot(BaseModel):
    timestamp: datetime
    temperature_c: float = Field(..., description="Temperature in Celsius")
    apparent_temperature_c: Optional[float] = Field(None, description="Apparent / feels-like temp in C")
    relative_humidity_pct: float = Field(..., ge=0, le=100, description="Relative humidity %")
    dew_point_c: Optional[float] = Field(None, description="Dew point in Celsius")
    surface_pressure_hpa: Optional[float] = Field(None, description="Surface pressure in hPa")
    wind_speed_kmh: float = Field(..., ge=0, description="Wind speed in km/h")
    wind_direction_deg: Optional[float] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    wind_gust_kmh: Optional[float] = Field(None, description="Wind gusts in km/h")
    precipitation_mm: float = Field(default=0.0, ge=0, description="Current precipitation rate in mm/h")
    cloud_cover_pct: Optional[float] = Field(None, ge=0, le=100, description="Cloud cover percentage")
    visibility_km: Optional[float] = Field(None, description="Visibility in km")
    uv_index: Optional[float] = Field(None, description="UV Index")
    soil_moisture_0_7cm: Optional[float] = Field(None, description="Volumetric soil water at 0-7cm (m³/m³)")
    weather_code: int = Field(default=0, description="WMO weather interpretation code")
    condition_text: str = Field(default="Clear", description="Human readable condition description")
    source: str = Field(default="Open-Meteo Observations", description="Data source attribution")
