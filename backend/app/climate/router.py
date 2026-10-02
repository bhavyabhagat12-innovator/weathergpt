"""
Climate analysis API router.
Provides historical trend and chart generation endpoints.
"""

from fastapi import APIRouter, Query, HTTPException
from app.climate.analyzer import ClimateAnalyzer, ChartSpec

router = APIRouter(prefix="/api/v1/climate", tags=["climate"])
analyzer = ClimateAnalyzer()


@router.get("/trend-chart", response_model=ChartSpec)
async def get_climate_trend_chart(
    location: str = Query(..., description="Indian city or district (e.g. Nashik, Nagpur, Chennai)"),
    years: int = Query(7, ge=3, le=15, description="Number of past years to evaluate")
):
    """
    Returns chart-ready JSON specification for multi-year monsoon rainfall trends.
    """
    try:
        return await analyzer.generate_monsoon_trend_chart(location_query=location, years=years)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Climate analysis failed: {str(e)}")
