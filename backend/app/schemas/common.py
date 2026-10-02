"""
Common schemas, enums, and types for WeatherGPT.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DomainRole(str, Enum):
    AGRICULTURE = "agriculture"
    AVIATION = "aviation"
    MARINE = "marine"
    URBAN_PLANNING = "urban_planning"
    DISASTER_MANAGEMENT = "disaster_management"
    GENERAL = "general"


class AlertSeverity(str, Enum):
    RED = "red"          # Warning: Take Action (Severe danger)
    ORANGE = "orange"    # Alert: Be Prepared (Considerable danger)
    YELLOW = "yellow"    # Watch: Be Updated (Moderate danger)
    GREEN = "green"      # No Warning: Normal conditions


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class LocationContext(BaseModel):
    query: str
    resolved_name: str
    latitude: float
    longitude: float
    country: str = "India"
    state: Optional[str] = None
    district: Optional[str] = None
    elevation_m: Optional[float] = None
    timezone: str = "Asia/Kolkata"
    role: DomainRole = DomainRole.GENERAL
