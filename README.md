# WeatherGPT — Conversational Weather Intelligence Platform for India

WeatherGPT is a ChatGPT-style conversational assistant that unifies scattered weather data — live observations, NWP model output (GFS/WRF), satellite products, and disaster-warning feeds — into one natural-language interface.

## Monorepo Structure

```
weathergpt/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI application with latency tracking
│   │   ├── schemas/          # Unified weather schemas & data contracts
│   │   ├── data_ingestion/   # Connectors (Open-Meteo, GFS NWP, IMD Bulletins, Climate)
│   │   ├── db/               # PostgreSQL / PostGIS + SQLite dual-mode
│   │   └── config.py         # Settings & environment validation
│   ├── scripts/              # Verification & demo scripts
│   ├── tests/                # Automated connector & orchestration test suite
│   └── pyproject.toml
├── infra/                    # Docker Compose & Kubernetes manifests
└── docs/                     # Architecture & data source documentation
```

## Core Tenets

- **Grounded Intelligence**: Strict RAG pattern preventing fabricated numbers.
- **Fail Gracefully**: Multi-tier fallbacks with offline catalogs and regional climatological baselines.
- **Role-Aware Support**: Tailored for Agriculture, Aviation, Marine, Urban Planning, and Disaster Management.
