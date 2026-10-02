# WeatherGPT System Architecture

WeatherGPT is an open, modular weather intelligence platform tailored for Indian agro-climatic zones, maritime logistics, aviation, urban disaster management, and climate research.

```mermaid
graph TD
    User([User: Farmer / Pilot / Port Officer / Disaster Manager]) --> UI[Mobile & Web Interface]
    UI --> API[FastAPI Gateway / Async API]
    
    subgraph "Core Data Ingestion Layer"
        API --> SVC[WeatherIntelligenceDataService]
        SVC --> GEO[India Geocoding Connector]
        SVC --> METEO[Open-Meteo Observations & 7-Day Forecast]
        SVC --> NWP[GFS 0.25° & WRF NWP Gridded Ingestor]
        SVC --> IMD[IMD / CAP National Bulletins Parser]
        SVC --> CLIM[ERA5 Climate Historical Archive]
    end

    subgraph "Grounding & Normalization"
        METEO --> NORM[Unified Weather Schema & Facts Compiler]
        NWP --> NORM
        IMD --> NORM
        CLIM --> NORM
        NORM --> UWR[UnifiedWeatherReport]
    end

    subgraph "LLM & Advisory Engine (Phase 2+)"
        UWR --> RAG[RAG Prompt Grounder - Zero Hallucinations]
        RAG --> LLM[Swappable LLM: Gemini / OpenAI / Local Ollama]
        LLM --> TRANS[Multilingual Translation Engine: Hindi, Tamil, Telugu, Marathi]
    end

    subgraph "Storage & Realtime Delivery"
        API --> PG[(PostgreSQL + PostGIS)]
        API --> MONGO[(MongoDB Unstructured Bulletins)]
        API --> WS[WebSocket / MQTT Dispatcher]
    end
```

## Non-Negotiable Guarantees

1. **Zero-Hallucination Numbers**: LLM never receives raw unrestricted queries. Every meteorological metric is resolved into `UnifiedWeatherReport.grounded_facts` with exact source citations.
2. **Graceful Degradation**: If an upstream provider times out, fallback algorithms (such as offline Indian location catalogs and regional NCMRWF stability approximations) ensure the service never crashes.
3. **Multi-Persona Decision Support**: Specialized prompts and data extraction for Agriculture (soil moisture, rain probability), Marine (wind gusts, swell, cyclone tiers), Aviation (CAPE, visibility, isobaric wind shear), and Disaster Management (IMD Red/Orange alerts, CAP warnings).
