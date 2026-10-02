"""
Tests for NWP GFS / WRF connector and atmospheric diagnostics.
"""

import pytest
from app.data_ingestion.nwp_gfs import NWPModelConnector


@pytest.mark.asyncio
async def test_nwp_diagnostics_fetch():
    connector = NWPModelConnector()
    # Visakhapatnam coordinates
    lat, lon = 17.6868, 83.2185
    diag = await connector.get_gfs_diagnostics(lat, lon)

    assert diag is not None
    assert diag.model_name != ""
    assert diag.cape_j_kg >= 0.0
    assert diag.convective_risk in [
        "Low (Atmospheric column stable / low convective potential)",
        "Moderate (Scattered thunderstorm potential)",
        "Severe (Favorable for intense thunderstorms, heavy downpours, wind gusts)",
        "Extreme (High probability of severe squall / supercell / tropical storm)",
    ] or "Low" in diag.convective_risk or "Severe" in diag.convective_risk or "Moderate" in diag.convective_risk or "Extreme" in diag.convective_risk
    assert len(diag.levels) >= 2


def test_synthetic_nwp_fallback():
    connector = NWPModelConnector()
    diag = connector.generate_synthetic_nwp_grid(17.6868, 83.2185)
    assert diag.cape_j_kg > 0
    assert diag.surface_pressure_hpa > 900
