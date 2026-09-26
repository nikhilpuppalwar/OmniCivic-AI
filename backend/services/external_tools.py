"""
OmniCivic AI -- External & Internal Analytical Tools

Implements keyless external API tools (Open-Meteo & OSM Overpass)
and internal state query tools for the Agentic Reasoning loop.
"""

import json
import os
import math
import logging
from typing import Dict, Any, List
import httpx

logger = logging.getLogger(__name__)

# In-memory cache for Overpass API queries to honor rate limits
_SENSITIVE_SITES_CACHE: Dict[str, Dict[str, Any]] = {}

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Haversine distance between two points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


async def get_weather_forecast(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get precipitation forecast for a location over the next 48 hours via Open-Meteo.
    Returns rain_risk_pct, max_precipitation_mm, and availability status.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=precipitation_probability,precipitation&forecast_days=2"
    
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return {"available": False, "reason": f"HTTP {resp.status_code}"}
            
            data = resp.json()
            hourly = data.get("hourly", {})
            probs = hourly.get("precipitation_probability", [])[:24]
            precip = hourly.get("precipitation", [])[:24]
            
            max_prob = max(probs) if probs else 0
            max_precip = max(precip) if precip else 0.0
            
            return {
                "available": True,
                "rain_risk_pct": max_prob,
                "max_precipitation_mm": max_precip,
                "heavy_rain_expected": max_prob > 60 or max_precip > 5.0,
                "forecast_hours_checked": len(probs),
                "summary": f"Next 24h max rain risk: {max_prob}% ({max_precip}mm)",
            }
    except Exception as e:
        logger.warning(f"Open-Meteo weather fetch failed: {e}")
        return {"available": False, "reason": str(e)}


async def find_nearby_sensitive_sites(
    latitude: float, longitude: float, radius_m: int = 250
) -> Dict[str, Any]:
    """
    Find schools, hospitals, clinics, kindergartens near lat/lon via OSM Overpass API.
    Caches results in memory to respect rate limits.
    """
    cache_key = f"{round(latitude, 4)}_{round(longitude, 4)}_{radius_m}"
    if cache_key in _SENSITIVE_SITES_CACHE:
        return _SENSITIVE_SITES_CACHE[cache_key]

    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""[out:json][timeout:8];
(
  node["amenity"~"school|hospital|clinic|kindergarten"](around:{radius_m},{latitude},{longitude});
  way["amenity"~"school|hospital|clinic|kindergarten"](around:{radius_m},{latitude},{longitude});
);
out center;"""

    headers = {"User-Agent": "OmniCivicAI/1.0 (municipal-incident-intelligence)"}

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.post(overpass_url, data={"data": query}, headers=headers)
            if resp.status_code != 200:
                result = {"available": False, "sites": [], "reason": f"HTTP {resp.status_code}"}
                _SENSITIVE_SITES_CACHE[cache_key] = result
                return result

            data = resp.json()
            elements = data.get("elements", [])
            sites = []
            
            for elem in elements:
                tags = elem.get("tags", {})
                name = tags.get("name", tags.get("amenity", "Sensitive Facility").title())
                amenity_type = tags.get("amenity", "sensitive_facility")
                elem_lat = elem.get("lat") or elem.get("center", {}).get("lat", latitude)
                elem_lon = elem.get("lon") or elem.get("center", {}).get("lon", longitude)
                dist = haversine_distance(latitude, longitude, elem_lat, elem_lon)
                
                sites.append({
                    "id": str(elem.get("id", f"site_{len(sites)+1}")),
                    "name": name,
                    "type": amenity_type,
                    "latitude": elem_lat,
                    "longitude": elem_lon,
                    "distance_m": round(dist, 1),
                })


            sites.sort(key=lambda s: s["distance_m"])
            result = {
                "available": True,
                "sites": sites,
                "total_found": len(sites),
                "closest_site": sites[0] if sites else None,
                "summary": f"Found {len(sites)} sensitive site(s) within {radius_m}m",
            }
            _SENSITIVE_SITES_CACHE[cache_key] = result
            return result
    except Exception as e:
        logger.warning(f"OSM Overpass query failed: {e}")
        fallback_result = {"available": False, "sites": [], "reason": str(e)}
        _SENSITIVE_SITES_CACHE[cache_key] = fallback_result
        return fallback_result


def query_dependency_graph(issue_type: str) -> Dict[str, Any]:
    """Look up known causal relationships from civic_dependencies.json."""
    dep_path = os.path.join(DATA_DIR, "civic_dependencies.json")
    if not os.path.exists(dep_path):
        return {"available": False, "dependencies": []}

    try:
        with open(dep_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        deps = data.get("dependencies", {})
        norm_type = issue_type.upper().replace(" ", "_")
        
        info = deps.get(norm_type, {})
        return {
            "available": True,
            "issue_type": norm_type,
            "caused_by": info.get("caused_by", []),
            "leads_to": info.get("leads_to", []),
            "primary_department": info.get("primary_department", ""),
            "secondary_departments": info.get("secondary_departments", []),
            "typical_cascade": info.get("typical_cascade", []),
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


def get_historical_incidents(latitude: float, longitude: float, radius_m: int = 180) -> Dict[str, Any]:
    """Check prior incidents within radius from incidents.json state store."""
    incidents_path = os.path.join(DATA_DIR, "incidents.json")
    if not os.path.exists(incidents_path):
        return {"available": True, "prior_incidents": [], "has_repeats": False}

    try:
        with open(incidents_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        incidents = data.get("incidents", [])
        nearby = []

        for inc in incidents:
            loc = inc.get("location", {})
            inc_lat = loc.get("latitude")
            inc_lon = loc.get("longitude")
            if inc_lat is None or inc_lon is None:
                continue

            dist = haversine_distance(latitude, longitude, inc_lat, inc_lon)
            if dist <= radius_m:
                nearby.append({
                    "incident_id": inc.get("incident_id"),
                    "category": inc.get("category"),
                    "status": inc.get("status"),
                    "distance_m": round(dist, 1),
                    "created_at": inc.get("created_at"),
                })

        return {
            "available": True,
            "prior_incidents": nearby,
            "total_nearby": len(nearby),
            "has_repeats": len(nearby) > 0,
            "summary": f"Found {len(nearby)} prior incident(s) within {radius_m}m",
        }
    except Exception as e:
        return {"available": False, "error": str(e), "prior_incidents": []}


def compute_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, Any]:
    """Expose Haversine distance calculation as a tool."""
    dist = haversine_distance(lat1, lon1, lat2, lon2)
    return {
        "distance_m": round(dist, 2),
        "distance_km": round(dist / 1000.0, 3),
        "within_180m_cluster": dist <= 180.0,
    }
