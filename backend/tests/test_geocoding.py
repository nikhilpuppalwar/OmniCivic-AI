"""
Unit tests for free OSM Nominatim geocoding proxy and caching.
"""

import pytest
import pytest_asyncio
from services.external_tools import geocode_address, _GEOCODE_CACHE


@pytest.mark.asyncio
async def test_geocode_short_query():
    """Single letter or empty queries should return empty list."""
    res = await geocode_address("")
    assert res == []
    res2 = await geocode_address("a")
    assert res2 == []


@pytest.mark.asyncio
async def test_geocode_caching():
    """Verify that repeated queries hit the in-memory cache."""
    # Pre-populate cache
    _GEOCODE_CACHE["test_mumbai_query"] = {
        "timestamp": 9999999999.0,
        "results": [{"display_name": "Test Location, Mumbai", "latitude": 19.0, "longitude": 72.8, "type": "city", "importance": 0.9}]
    }
    res = await geocode_address("test_mumbai_query")
    assert len(res) == 1
    assert res[0]["display_name"] == "Test Location, Mumbai"


@pytest.mark.asyncio
async def test_geocode_offline_fallback():
    """Verify that if query matches known municipal landmark, fallback returns structured items."""
    # Query something matching local fallbacks like 'Kurla'
    res = await geocode_address("Kurla West Railway Station")
    assert len(res) > 0
    assert any("Kurla" in r["display_name"] for r in res)
    assert "latitude" in res[0]
    assert "longitude" in res[0]
