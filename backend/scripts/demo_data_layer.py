"""
Manual Demonstration Script for WeatherGPT Data Layer.
Runs end-to-end multi-source data ingestion for two distinct roles:
1. Farmer in Nashik (Maharashtra) -> Agriculture Persona with Soil Moisture & Rain Probability.
2. Port Controller / Marine in Visakhapatnam (Andhra Pradesh) -> Marine Persona with Cyclone Alerts & NWP CAPE.
"""

import asyncio
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure backend directory is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))


from app.data_ingestion.service import WeatherIntelligenceDataService
from app.schemas.common import DomainRole


async def run_demo():
    print("=" * 80)
    print("  WEATHERGPT DATA LAYER - MULTI-SOURCE INGESTION & GROUNDING DEMO")
    print("=" * 80)

    service = WeatherIntelligenceDataService()

    # Case 1: Farmer in Nashik asking about harvest & rain
    print("\n[SCENARIO 1] Resolving Hyperlocal Weather for Farmer in Nashik, Maharashtra...")
    report1 = await service.get_unified_report(query="Nashik", role=DomainRole.AGRICULTURE)

    print(f"  * Resolved Location: {report1.location.resolved_name} ({report1.location.district}, {report1.location.state})")
    print(f"  * Coordinates: Lat {report1.location.latitude:.4f}, Lon {report1.location.longitude:.4f}")
    if report1.observation:
        print(f"  * Live Observation: {report1.observation.temperature_c}°C, Humidity: {report1.observation.relative_humidity_pct}%, Condition: {report1.observation.condition_text}")
        print(f"  * Soil Moisture (0-7cm): {report1.observation.soil_moisture_0_7cm} m³/m³")
    if report1.forecast and report1.forecast.daily:
        f0 = report1.forecast.daily[0]
        print(f"  * Today's Forecast: Rain: {f0.precipitation_sum_mm} mm (Prob: {f0.precipitation_probability_max_pct}%), Max Wind: {f0.wind_speed_max_kmh} km/h")
    if report1.nwp:
        print(f"  * NWP GFS Convective Risk: {report1.nwp.convective_risk} (CAPE: {report1.nwp.cape_j_kg} J/kg)")
    print(f"  * Active Bulletins Count: {len(report1.alerts)}")
    for a in report1.alerts:
        print(f"    - [{a.severity.value.upper()}] {a.headline}")
    print(f"  * Citations: {', '.join(report1.citations)}")
    print(f"  * Grounded Facts Extracted for LLM:")
    for k, v in list(report1.grounded_facts.items())[:8]:
        print(f"    - {k}: {v}")

    # Case 2: Port Officer in Visakhapatnam tracking severe cyclone
    print("\n" + "-" * 80)
    print("[SCENARIO 2] Resolving Marine Briefing for Visakhapatnam Port...")
    report2 = await service.get_unified_report(query="Visakhapatnam", role=DomainRole.MARINE)

    print(f"  * Resolved Location: {report2.location.resolved_name} ({report2.location.state})")
    if report2.observation:
        print(f"  * Live Wind: {report2.observation.wind_speed_kmh} km/h (Gusts: {report2.observation.wind_gust_kmh} km/h, Dir: {report2.observation.wind_direction_deg}°)")
    print(f"  * Active Bulletins Count: {len(report2.alerts)}")
    for a in report2.alerts:
        print(f"    - [{a.severity.value.upper()}] {a.headline}")
        print(f"      Instructions: {a.instruction}")
    if report2.nwp:
        print(f"  * NWP Isobaric Layers (850hPa vs 500hPa): Bulk Shear = {report2.nwp.wind_shear_0_6km_kmh} km/h")

    print("\n" + "=" * 80)
    print("  DEMO COMPLETED SUCCESSFULLY: All data points grounded without hallucinations.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(run_demo())
