"""
Unified Weather Report schema.
Aggregates observation, forecast, NWP metrics, active alerts, and citations.
Acts as the single ground-truth payload for the LLM reasoning and advisory layers.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.schemas.common import LocationContext, DomainRole
from app.schemas.observation import ObservationSnapshot
from app.schemas.forecast import ForecastPackage
from app.schemas.nwp import NWPDiagnostics
from app.schemas.alerts import WeatherAlertItem


class ClimateAnomalyContext(BaseModel):
    historical_avg_temp_c: Optional[float] = None
    temp_anomaly_c: Optional[float] = None
    historical_avg_monthly_rain_mm: Optional[float] = None
    monsoon_status: Optional[str] = None
    trend_notes: Optional[str] = None


class UnifiedWeatherReport(BaseModel):
    report_id: str
    generated_at: datetime
    location: LocationContext
    role: DomainRole = DomainRole.GENERAL
    
    # Ground-truth weather data layers
    observation: Optional[ObservationSnapshot] = None
    forecast: Optional[ForecastPackage] = None
    nwp: Optional[NWPDiagnostics] = None
    alerts: List[WeatherAlertItem] = Field(default_factory=list)
    climate: Optional[ClimateAnomalyContext] = None

    # Provenance & RAG Grounding
    grounded_facts: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured key-value pairs of verified measurements for strict LLM constraint"
    )
    citations: List[str] = Field(
        default_factory=list,
        description="Exact data sources cited for this report (e.g. Open-Meteo, GFS, IMD Bulletin)"
    )
    degraded_sources: List[str] = Field(
        default_factory=list,
        description="Any upstream sources that were unavailable or timed out"
    )
    is_live_data: bool = True
