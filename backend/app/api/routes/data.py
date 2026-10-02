"""
API endpoints for weather data ingestion and report retrieval.
"""

from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends

from app.schemas.common import DomainRole
from app.schemas.unified import UnifiedWeatherReport
from app.schemas.alerts import AlertBulletinFeed
from app.data_ingestion.service import WeatherIntelligenceDataService

router = APIRouter(prefix="/api/v1/weather", tags=["weather-data"])
service = WeatherIntelligenceDataService()


@router.get("/report", response_model=UnifiedWeatherReport)
async def get_weather_report(
    location: str = Query(..., description="Indian city, district, taluk or port name (e.g. Nashik, Visakhapatnam)"),
    role: DomainRole = Query(DomainRole.GENERAL, description="Decision support persona (agriculture, aviation, marine, etc.)"),
    include_climate: bool = Query(True, description="Whether to include historical climate context")
):
    """
    Returns a UnifiedWeatherReport containing real-time observations, 7-day forecast,
    NWP stability diagnostics (GFS), active IMD severe alerts, and grounded facts for LLM reasoning.
    """
    try:
        report = await service.get_unified_report(query=location, role=role, include_climate=include_climate)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weather report: {str(e)}")


@router.get("/bulletins", response_model=AlertBulletinFeed)
async def get_bulletins():
    """
    Returns the national severe weather bulletin feed with active cyclone, rainfall, and heatwave alerts.
    """
    try:
        return await service.bulletins.get_national_feed_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bulletins: {str(e)}")


@router.get("/climate-trend")
async def get_climate_trend(
    location: str = Query(..., description="Location name"),
    years: int = Query(5, ge=2, le=20, description="Number of past years to analyze")
):
    """
    Returns multi-year historical monsoon and precipitation trends for auto-generated charts.
    """
    try:
        loc = await service.geocoder.resolve_location(location)
        trend = await service.climate.get_multi_year_monsoon_trend(loc.latitude, loc.longitude, years=years)
        return {
            "resolved_location": loc.resolved_name,
            "district": loc.district,
            "state": loc.state,
            "analysis": trend
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch climate trend: {str(e)}")


@router.get("/geocode")
async def geocode_location(query: str = Query(..., description="Search query")):
    """
    Geocodes an Indian query into resolved location coordinates and administrative metadata.
    """
    try:
        return await service.geocoder.resolve_location(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to geocode '{query}': {str(e)}")
