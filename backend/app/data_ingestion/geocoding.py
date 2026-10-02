"""
Geocoding connector specialized for Indian locations (districts, taluks, cities, ports).
Uses Open-Meteo Geocoding API with high-accuracy offline fallback for major Indian hubs.
"""

import logging
from typing import Optional, List
import httpx

from app.config import settings
from app.data_ingestion.base import BaseConnector
from app.schemas.common import LocationContext, DomainRole

logger = logging.getLogger("weathergpt.geocoding")

# Offline fallback catalog for critical Indian agro-climatic & maritime zones
INDIAN_LOCATION_CATALOG = {
    "nashik": {
        "resolved_name": "Nashik",
        "latitude": 19.9975,
        "longitude": 73.7898,
        "state": "Maharashtra",
        "district": "Nashik",
        "elevation_m": 600.0,
    },
    "visakhapatnam": {
        "resolved_name": "Visakhapatnam",
        "latitude": 17.6868,
        "longitude": 83.2185,
        "state": "Andhra Pradesh",
        "district": "Visakhapatnam",
        "elevation_m": 45.0,
    },
    "vizag": {
        "resolved_name": "Visakhapatnam",
        "latitude": 17.6868,
        "longitude": 83.2185,
        "state": "Andhra Pradesh",
        "district": "Visakhapatnam",
        "elevation_m": 45.0,
    },
    "nagpur": {
        "resolved_name": "Nagpur",
        "latitude": 21.1458,
        "longitude": 79.0882,
        "state": "Maharashtra",
        "district": "Nagpur",
        "elevation_m": 310.0,
    },
    "chennai": {
        "resolved_name": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "state": "Tamil Nadu",
        "district": "Chennai",
        "elevation_m": 6.0,
    },
    "mumbai": {
        "resolved_name": "Mumbai",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "state": "Maharashtra",
        "district": "Mumbai Suburban",
        "elevation_m": 14.0,
    },
    "delhi": {
        "resolved_name": "New Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "state": "Delhi",
        "district": "New Delhi",
        "elevation_m": 216.0,
    },
    "bengaluru": {
        "resolved_name": "Bengaluru",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "state": "Karnataka",
        "district": "Bengaluru Urban",
        "elevation_m": 920.0,
    },
    "hyderabad": {
        "resolved_name": "Hyderabad",
        "latitude": 17.3850,
        "longitude": 78.4867,
        "state": "Telangana",
        "district": "Hyderabad",
        "elevation_m": 505.0,
    },
    "kolkata": {
        "resolved_name": "Kolkata",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "state": "West Bengal",
        "district": "Kolkata",
        "elevation_m": 9.0,
    },
    "pune": {
        "resolved_name": "Pune",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "state": "Maharashtra",
        "district": "Pune",
        "elevation_m": 560.0,
    },
    "patna": {
        "resolved_name": "Patna",
        "latitude": 25.5941,
        "longitude": 85.1376,
        "state": "Bihar",
        "district": "Patna",
        "elevation_m": 53.0,
    },
    "kochi": {
        "resolved_name": "Kochi",
        "latitude": 9.9312,
        "longitude": 76.2673,
        "state": "Kerala",
        "district": "Ernakulam",
        "elevation_m": 5.0,
    },
    "shimla": {
        "resolved_name": "Shimla",
        "latitude": 31.1048,
        "longitude": 77.1734,
        "state": "Himachal Pradesh",
        "district": "Shimla",
        "elevation_m": 2200.0,
    },
    "guwahati": {
        "resolved_name": "Guwahati",
        "latitude": 26.1445,
        "longitude": 91.7362,
        "state": "Assam",
        "district": "Kamrup Metropolitan",
        "elevation_m": 55.0,
    },
}


class IndiaGeocodingConnector(BaseConnector):
    """Geocoding service with online search & offline fallback."""

    def __init__(self):
        super().__init__(name="IndiaGeocoding", cache_ttl_seconds=86400, timeout_seconds=5.0)

    async def resolve_location(self, query: str, role: DomainRole = DomainRole.GENERAL) -> LocationContext:
        """
        Geocodes a location query into latitude, longitude, and administrative metadata.
        Falls back gracefully to offline catalog on network timeout or empty results.
        """
        clean_query = query.strip().lower()
        cache_key = f"geo_{clean_query}"
        cached = self._get_from_cache(cache_key)
        if cached:
            cached.role = role
            return cached

        # 1. Try online Open-Meteo Geocoding API
        try:
            url = f"{settings.GEOCODING_BASE_URL}/search"
            params = {
                "name": query.strip(),
                "count": 5,
                "language": "en",
                "format": "json"
            }
            data = await self.fetch_json(url, params=params)
            results = data.get("results", [])
            
            if results:
                # Prefer Indian results if multiple
                india_match = next((r for r in results if r.get("country_code") == "IN"), results[0])
                loc = LocationContext(
                    query=query,
                    resolved_name=india_match.get("name", query),
                    latitude=float(india_match.get("latitude")),
                    longitude=float(india_match.get("longitude")),
                    country=india_match.get("country", "India"),
                    state=india_match.get("admin1"),
                    district=india_match.get("admin2"),
                    elevation_m=india_match.get("elevation"),
                    timezone=india_match.get("timezone", "Asia/Kolkata"),
                    role=role
                )
                self._set_in_cache(cache_key, loc)
                return loc
        except Exception as e:
            logger.warning(f"Online geocoding for '{query}' failed ({e}). Attempting offline catalog fallback.")

        # 2. Check offline catalog
        # Exact match or substring match
        for key, info in INDIAN_LOCATION_CATALOG.items():
            if key in clean_query or clean_query in key:
                loc = LocationContext(
                    query=query,
                    resolved_name=info["resolved_name"],
                    latitude=info["latitude"],
                    longitude=info["longitude"],
                    country="India",
                    state=info["state"],
                    district=info["district"],
                    elevation_m=info["elevation_m"],
                    timezone="Asia/Kolkata",
                    role=role
                )
                self._set_in_cache(cache_key, loc)
                return loc

        # 3. Default fallback: Center of India (Nagpur) with note
        default_info = INDIAN_LOCATION_CATALOG["nagpur"]
        loc = LocationContext(
            query=query,
            resolved_name=f"{query.title()} (Estimated: Central India)",
            latitude=default_info["latitude"],
            longitude=default_info["longitude"],
            country="India",
            state=default_info["state"],
            district=default_info["district"],
            elevation_m=default_info["elevation_m"],
            timezone="Asia/Kolkata",
            role=role
        )
        return loc
