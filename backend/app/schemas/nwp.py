"""
NWP (Numerical Weather Prediction) gridded model schema.
Captures atmospheric stability, isobaric data, and severe weather triggers (GFS / WRF / NCMRWF).
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class NWPIsobaricLevel(BaseModel):
    level_hpa: int = Field(..., description="Pressure level (e.g. 850, 700, 500, 200 hPa)")
    geopotential_height_m: Optional[float] = None
    temperature_c: Optional[float] = None
    wind_speed_kmh: Optional[float] = None
    wind_direction_deg: Optional[float] = None
    relative_humidity_pct: Optional[float] = None


class NWPDiagnostics(BaseModel):
    model_name: str = Field(..., description="e.g. GFS 0.25°, WRF-India 3km, NCMRWF")
    run_cycle: str = Field(..., description="e.g. 00Z, 06Z, 12Z, 18Z")
    run_timestamp: datetime
    valid_timestamp: datetime
    
    # Severe Weather & Convective Dynamics
    cape_j_kg: float = Field(default=0.0, description="Convective Available Potential Energy (J/kg)")
    lifted_index_c: Optional[float] = Field(None, description="Lifted Index in Celsius")
    precipitable_water_mm: Optional[float] = Field(None, description="Total column precipitable water (mm)")
    surface_pressure_hpa: Optional[float] = Field(None, description="Model surface pressure in hPa")
    wind_shear_0_6km_kmh: Optional[float] = Field(None, description="Deep layer bulk wind shear (km/h)")
    
    # Stability categorization
    convective_risk: str = Field(
        default="Low", 
        description="Low (CAPE < 1000), Moderate (1000-2500), Severe (2500-4000), Extreme (>4000)"
    )
    
    # Atmospheric profile
    levels: List[NWPIsobaricLevel] = Field(default_factory=list)
    raw_source: str = "NOAA GFS / NCMRWF Gridded Ingest"
