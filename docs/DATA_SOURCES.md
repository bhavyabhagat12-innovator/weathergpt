# WeatherGPT Data Sources Contract & Operational Guide

| Data Layer | Primary Operational Provider | Format / Protocol | Fallback Mechanism | Update Frequency |
|---|---|---|---|---|
| **Live Observations** | Open-Meteo High-Resolution (India Domain) | JSON REST API | Local Station Cache | Every 10 mins |
| **Hourly & Daily Forecast** | Open-Meteo Multi-Model Ensemble | JSON REST API | 12-hour Rolling Cache | Hourly |
| **Gridded NWP Output** | NOAA GFS 0.25° Global Model | GFS GRIB2 / JSON API | NCMRWF India 4km Grid Fallback | Every 3 to 6 hours |
| **Severe Weather Warnings** | India Meteorological Department (IMD) / CAP / GDACS | CAP XML / RSS / JSON | Regional Agro-met Bulletins | Every 15 mins |
| **Indian Geocoding** | Open-Meteo Geocoding Service | JSON REST API | Embedded Indian District Catalog | Static / 24h Cache |
| **Historical Climate Trends** | ECMWF ERA5 Reanalysis / Open-Meteo Archive | JSON REST API | Climatological Normals Benchmark | Daily |

## Grounded Metrics Schema

All external feeds map to `UnifiedWeatherReport`:
- `current_temperature_c`: Air temperature at 2 meters above ground.
- `relative_humidity_pct`: Relative humidity percentage.
- `wind_speed_kmh`, `wind_gust_kmh`: Surface wind velocities.
- `soil_moisture_0_7cm`: Volumetric water content in topsoil for agriculture.
- `nwp_cape_j_kg`: Atmospheric Convective Available Potential Energy for severe storm forecasting.
- `highest_alert_severity`: Highest active national bulletin tier (`RED`, `ORANGE`, `YELLOW`, `GREEN`).
