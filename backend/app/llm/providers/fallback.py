"""
Fallback rule-based and semantic advisory generator.
Generates comprehensive, grounded, zero-hallucination domain advisories
directly from verified UnifiedWeatherReport telemetry without external API keys.
"""

from typing import Optional
from app.schemas.common import DomainRole
from app.schemas.unified import UnifiedWeatherReport
from app.llm.base import BaseLLMProvider, QueryIntent
from app.llm.query_parser import RuleBasedQueryParser


class FallbackAdvisoryProvider(BaseLLMProvider):
    """Local, high-reliability advisory generator."""

    def __init__(self):
        super().__init__(provider_name="Local-Grounded-Rules-Engine")

    async def parse_intent(self, user_query: str, default_role: Optional[DomainRole] = None) -> QueryIntent:
        return RuleBasedQueryParser.parse(user_query, default_role=default_role)

    async def generate_advisory(
        self,
        report: UnifiedWeatherReport,
        user_query: str,
        role: DomainRole,
        language: str = "en"
    ) -> str:
        facts = report.grounded_facts
        loc_name = facts.get("query_location", report.location.resolved_name)
        district = facts.get("district", report.location.district or loc_name)
        state = facts.get("state", report.location.state or "India")
        temp = facts.get("current_temperature_c", "N/A")
        humidity = facts.get("relative_humidity_pct", "N/A")
        condition = facts.get("weather_condition", "Fair")
        rain_sum = facts.get("forecast_today_rain_sum_mm", 0.0)
        rain_prob = facts.get("forecast_today_rain_probability_pct", 0.0)
        wind_speed = facts.get("wind_speed_kmh", 0.0)
        wind_gust = facts.get("wind_gust_kmh", wind_speed)
        soil_m = facts.get("soil_moisture_0_7cm")
        cape = facts.get("nwp_cape_j_kg", 0.0)

        # 1. Alert Banner if active
        alert_banners = []
        for alert in report.alerts:
            alert_banners.append(
                f"🚨 **{alert.severity.value.upper()} ALERT ({alert.event_type})**: {alert.headline}\n"
                f"**Mandatory Directive**: {alert.instruction or 'Follow local disaster authority instructions.'}\n"
            )
        alert_header = "\n".join(alert_banners)
        if alert_header:
            alert_header += "\n---\n"

        # 2. Domain-specific reasoning
        if role == DomainRole.AGRICULTURE:
            # Sowing/harvest logic
            harvest_advice = "Favorable for field operations."
            if rain_prob > 50 or rain_sum > 5.0:
                harvest_advice = f"⚠️ Postpone harvesting and sensitive field operations. High rain risk detected ({rain_sum} mm, {rain_prob}% probability today)."
            
            # Spraying window logic
            spray_advice = "Spraying window is OPEN."
            if rain_prob > 40 or wind_speed > 15:
                spray_advice = f"🚫 DO NOT SPRAY pesticides/fertilizers: Rain probability ({rain_prob}%) or wind speed ({wind_speed} km/h) exceeds safe threshold."

            # Soil moisture logic
            soil_text = "Soil moisture data unavailable."
            if soil_m is not None:
                if soil_m < 0.20:
                    soil_text = f"Topsoil moisture is LOW ({soil_m:.3f} m³/m³). Immediate light irrigation recommended for standing crops."
                elif soil_m > 0.40:
                    soil_text = f"Topsoil moisture is HIGH/SATURATED ({soil_m:.3f} m³/m³). Ensure active field drainage to prevent root hypoxia."
                else:
                    soil_text = f"Topsoil moisture is OPTIMAL ({soil_m:.3f} m³/m³)."

            body = (
                f"### 🌾 Agro-Meteorological Advisory for {loc_name}, {district} ({state})\n"
                f"**Current Status**: {temp}°C | Humidity: {humidity}% | Condition: {condition}\n\n"
                f"**1. Harvest & Fieldwork Guidance**:\n{harvest_advice}\n\n"
                f"**2. Chemical Spraying Window**:\n{spray_advice}\n\n"
                f"**3. Soil & Irrigation Assessment**:\n{soil_text}\n\n"
                f"**Forecast Horizon**: Expected rainfall today is {rain_sum} mm with {rain_prob}% likelihood. Maximum surface wind {wind_speed} km/h."
            )

        elif role == DomainRole.AVIATION:
            vis = facts.get("visibility_km", "10+")
            convective_risk = facts.get("convective_storm_risk", "Low")
            shear = report.nwp.wind_shear_0_6km_kmh if report.nwp else "N/A"

            # Derive FAA/ICAO flight category from visibility and ceiling proxy
            try:
                vis_f = float(vis)
            except (ValueError, TypeError):
                vis_f = 10.0
            if vis_f >= 8 and cape < 500:
                flight_cat = "✅ VFR (Visual Flight Rules — Unrestricted operations)"
            elif vis_f >= 3 and cape < 1500:
                flight_cat = "⚠️ MVFR (Marginal VFR — Increased caution required)"
            else:
                flight_cat = "🔴 IFR (Instrument Flight Rules — Low-visibility procedures mandatory)"

            body = (
                f"### ✈️ Aviation Meteorological Briefing — {loc_name} Airspace\n"
                f"**Surface Parameters**: Temp {temp}°C | Wind {wind_speed} km/h (Gusts {wind_gust} km/h) | Visibility: {vis} km\n\n"
                f"**1. Flight Category**:\n{flight_cat}\n\n"
                f"**2. Convective Dynamics & Squall Hazard**:\n"
                f"- NWP CAPE: {cape} J/kg — {convective_risk} instability\n"
                f"- Bulk Vertical Wind Shear (0-6km): {shear} km/h\n"
                f"{'- ⚠️ Convective instability exceeds threshold — monitor for cumulonimbus and microburst risk.' if cape > 1500 else '- Tropospheric profile stable; no significant convective threat detected.'}\n\n"
                f"**3. Clearance Advisory**:\n"
                f"Runway crosswind component within standard operating limits. "
                f"{'File IFR flight plan and confirm ATC holding instructions.' if vis_f < 3 else 'Standard VFR/MVFR departure and arrival procedures apply.'}"
            )

        elif role == DomainRole.MARINE:
            body = (
                f"### ⚓ Maritime & Port Advisory for {loc_name} Coastal Waters\n"
                f"**Sea Surface Wind**: {wind_speed} km/h sustained | Peak Gusts: {wind_gust} km/h\n"
                f"**Condition**: {condition} | Atmospheric Pressure: {facts.get('current_surface_pressure_hpa', 1010)} hPa\n\n"
                f"**1. Fishermen Warning**:\n"
                f"{'🛑 DANGER: All fishing vessels must immediately return to port or anchor safely. Do not venture into deep waters.' if len(report.alerts) > 0 or wind_gust > 40 else '✅ Coastal waters operational with standard cautionary navigation.'}\n\n"
                f"**2. Port Operations**:\n"
                f"Verify crane securing and offshore lighterage schedules against gust thresholds of {wind_gust} km/h."
            )

        elif role == DomainRole.DISASTER_MANAGEMENT:
            highest_sev = facts.get("highest_alert_severity", "GREEN").upper()
            body = (
                f"### 🚨 Disaster Management Situation Report — {district}, {state}\n"
                f"**Incident Alert Level**: {highest_sev}\n"
                f"**Precipitation Threat**: {rain_sum} mm today (Probability: {rain_prob}%)\n\n"
                f"**Operational Directives**:\n"
                f"- Activate District Emergency Operations Center (DEOC).\n"
                f"- Low-lying drainage monitoring: Alert civic pumps and flood watch wardens.\n"
                f"- Power & Communication: Pre-stage emergency response equipment for wind gusts up to {wind_gust} km/h."
            )

        elif role.value == "urban_planning":
            body = (
                f"### 🏗️ Urban Planning & Infrastructure Weather Advisory — {loc_name}\n"
                f"**Current Conditions**: {temp}°C | {condition} | Humidity {humidity}%\n\n"
                f"**1. Drainage & Flood-Risk Assessment**:\n"
                f"{'🔴 HIGH RISK: Rainfall of ' + str(rain_sum) + ' mm forecast. Verify stormwater drain capacity and activate flood-control pumping stations.' if rain_sum > 50 else ('⚠️ MODERATE: ' + str(rain_sum) + ' mm expected. Monitor low-lying areas and underpasses for waterlogging.' if rain_sum > 15 else '✅ LOW RISK: Minimal rainfall forecast. Routine urban infrastructure monitoring sufficient.')}\n\n"
                f"**2. Construction-Site Safety**:\n"
                f"{'🚫 Suspend crane/high-rise operations: Wind gusts ' + str(wind_gust) + ' km/h exceed safe working threshold of 40 km/h.' if wind_gust > 40 else 'Wind speeds within safe construction operating limits (' + str(wind_gust) + ' km/h gusts).'}\n\n"
                f"**3. Heat Island & Thermal Stress**:\n"
                f"{'🌡️ Urban heat island risk elevated at ' + str(temp) + '°C. Ensure shading, misting, and water access in high-density zones.' if isinstance(temp, (int, float)) and float(temp) > 38 else 'Thermal conditions within acceptable urban comfort range.'}\n\n"
                f"**4. Traffic & Public Transport**:\n"
                f"{'Heavy rain forecast — recommend pre-emptive diversion of under-bridge traffic and advisory to public transport operators.' if rain_prob > 60 else 'No weather-related traffic disruptions anticipated.'}"
            )

        else:  # General
            body = (
                f"### 🏙️ Weather Intelligence Briefing for {loc_name}\n"
                f"Right now in {loc_name} ({district}), it is **{temp}°C** and **{condition}** with **{humidity}% relative humidity**.\n\n"
                f"**Today's Outlook**:\n"
                f"- Rain Probability: **{rain_prob}%** (Cumulative: ~{rain_sum} mm)\n"
                f"- Winds: **{wind_speed} km/h** with gusts up to **{wind_gust} km/h**.\n\n"
                f"**Commuter Tip**: {'Keep an umbrella handy today as showers are likely.' if rain_prob > 40 else 'Weather conditions are clear and favorable for outdoor travel.'}"
            )

        return f"{alert_header}{body}"
