# WeatherGPT Backend

FastAPI-powered weather intelligence backend with zero-hallucination data grounding, NWP integration, and IMD alert parsing.

## Getting Started

### 1. Environment Setup

Using `uv` (recommended):
```bash
cd backend
uv venv
uv pip install -e ".[dev]"
```

Or using standard `pip`:
```bash
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Run Tests
```bash
uv run pytest -v
```

### 3. Run Demo Script
```bash
uv run python scripts/demo_data_layer.py
```

### 4. Start Local Development Server
```bash
uv run uvicorn app.api.main:app --reload --port 8000
```
Open `http://localhost:8000/docs` in your browser for the Swagger interactive API documentation.
