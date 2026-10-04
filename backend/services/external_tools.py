"""
OmniCivic AI -- External & Internal Analytical Tools

Implements keyless external API tools (Open-Meteo & OSM Overpass)
and internal state query tools for the Agentic Reasoning loop.
"""

import json
import os
import math
import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
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


def _should_simulate_failure(tool_key: str) -> bool:
    sim = os.getenv("SIMULATE_TOOL_FAILURE", "").strip().lower()
    if not sim:
        return False
    if sim in ("all", "1", "true"):
        return True
    return tool_key.lower() in [s.strip() for s in sim.split(",")]


async def get_weather_forecast(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Get precipitation forecast for a location over the next 48 hours via Open-Meteo.
    Returns rain_risk_pct, max_precipitation_mm, and availability status.
    """
    if _should_simulate_failure("weather"):
        logger.warning("[SIMULATED_FAILURE] Forcing simulated failure for get_weather_forecast")
        return {"available": False, "reason": "Simulated tool failure (SIMULATE_TOOL_FAILURE=weather)"}

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
    if _should_simulate_failure("osm") or _should_simulate_failure("sites"):
        logger.warning("[SIMULATED_FAILURE] Forcing simulated failure for find_nearby_sensitive_sites")
        return {"available": False, "sites": [], "reason": "Simulated tool failure (SIMULATE_TOOL_FAILURE=osm)"}

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


SYNONYMS = {
    "WATER_PIPE_BURST": "WATER_LEAKAGE",
    "PIPE_BURST": "WATER_LEAKAGE",
    "ROAD_CAVE_IN": "ROAD_DAMAGE",
    "CAVE_IN": "ROAD_DAMAGE",
    "STREETLIGHT": "BROKEN_STREETLIGHT",
    "STREETLIGHT_OUT": "BROKEN_STREETLIGHT",
    "WIRES": "EXPOSED_WIRES",
}


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
        canonical_type = SYNONYMS.get(norm_type, norm_type)
        
        info = deps.get(canonical_type, {})
        can_cause_targets = [c.get("target") for c in info.get("can_cause", []) if isinstance(c, dict)]
        leads_to = list(set(can_cause_targets + info.get("leads_to", [])))

        # Find typical cascade from scenario_chains if not directly present
        typical_cascade = info.get("typical_cascade", [])
        if not typical_cascade:
            for sc in data.get("scenario_chains", {}).values():
                chain = sc.get("chain", [])
                if canonical_type in chain:
                    typical_cascade = chain
                    break

        dept_map = {
            "WATER_LEAKAGE": "WATER_BOARD",
            "ROAD_DAMAGE": "ROADS_DEPT",
            "POTHOLE": "ROADS_DEPT",
            "WATERLOGGING": "STORM_WATER_DRAINAGE",
            "DRAIN_BLOCKAGE": "STORM_WATER_DRAINAGE",
            "DRAINAGE_PROBLEM": "STORM_WATER_DRAINAGE",
            "SEWAGE_OVERFLOW": "WATER_BOARD",
            "GARBAGE_OVERFLOW": "SOLID_WASTE_MGMT",
            "BROKEN_STREETLIGHT": "ELECTRICAL_DEPT",
            "EXPOSED_WIRES": "ELECTRICAL_DEPT",
        }

        primary_dept = info.get("primary_department") or dept_map.get(canonical_type, "MUNICIPAL_ADMIN")

        return {
            "available": True,
            "issue_type": canonical_type,
            "original_query": issue_type,
            "caused_by": info.get("caused_by", []),
            "leads_to": leads_to,
            "primary_department": primary_dept,
            "secondary_departments": info.get("secondary_departments", []),
            "typical_cascade": typical_cascade,
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


# ── Free Address Geocoding Proxy (OSM Nominatim) ────────────────────────────

_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}
_LAST_NOMINATIM_TIME: float = 0.0
_NOMINATIM_LOCK: Optional[asyncio.Lock] = None

# Known local fallback coordinates for municipal areas (offline & resilience support)
_LOCAL_GEOCODE_FALLBACKS: List[Dict[str, Any]] = [
    {"name": "Near Chakala Junction, Andheri East, Mumbai", "lat": 19.1190, "lon": 72.8470, "ward": "Ward 7 - Andheri East"},
    {"name": "Chakala Junction Main Road, Andheri East, Mumbai", "lat": 19.1192, "lon": 72.8472, "ward": "Ward 7 - Andheri East"},
    {"name": "Andheri Railway Station, Mumbai", "lat": 19.1197, "lon": 72.8464, "ward": "Ward 7 - Andheri East"},
    {"name": "Tilak Nagar Colony, Kurla East, Mumbai", "lat": 19.0719, "lon": 72.8558, "ward": "Ward 6 - Kurla"},
    {"name": "Tilak Nagar Market Road, Kurla, Mumbai", "lat": 19.0720, "lon": 72.8560, "ward": "Ward 6 - Kurla"},
    {"name": "Kurla West Railway Station, Mumbai", "lat": 19.0680, "lon": 72.8800, "ward": "Ward 6 - Kurla"},
    {"name": "St. Xavier's High School Gate, Marine Lines, Mumbai", "lat": 19.0760, "lon": 72.8780, "ward": "Ward 3 - Marine Lines"},
    {"name": "Marine Drive Promenade, Mumbai", "lat": 18.9430, "lon": 72.8230, "ward": "Ward 3 - Marine Lines"},
    {"name": "Hill Road, Bandra West, Mumbai", "lat": 19.0550, "lon": 72.8330, "ward": "Ward 9 - Bandra West"},
    {"name": "Bandra Kurla Complex (BKC), Mumbai", "lat": 19.0650, "lon": 72.8680, "ward": "Ward 9 - Bandra West"},
    {"name": "Dadar Station Plaza, Dadar West, Mumbai", "lat": 19.0178, "lon": 72.8428, "ward": "Ward 8 - Dadar West"},
    {"name": "Shivaji Park, Dadar, Mumbai", "lat": 19.0270, "lon": 72.8380, "ward": "Ward 8 - Dadar West"},
    {"name": "Powai Lake, Powai, Mumbai", "lat": 19.1250, "lon": 72.9050, "ward": "Ward 10 - Powai"},
    {"name": "Colaba Causeway, South Mumbai", "lat": 18.9150, "lon": 72.8250, "ward": "Ward 1 - Colaba"},
]


async def geocode_address(query: str) -> List[Dict[str, Any]]:
    """
    Geocode an address query using OpenStreetMap Nominatim with:
    - In-memory caching (1 hour TTL)
    - Rate-limiting (1 request per second as per OSM usage policy)
    - Descriptive User-Agent header
    - Offline fallback to known municipal landmarks if unreachable
    """
    global _LAST_NOMINATIM_TIME, _NOMINATIM_LOCK

    clean_q = query.strip()
    if not clean_q or len(clean_q) < 2:
        return []

    cache_key = clean_q.lower()
    now = time.time()

    # Check cache (1 hour = 3600s TTL)
    if cache_key in _GEOCODE_CACHE:
        entry = _GEOCODE_CACHE[cache_key]
        if now - entry.get("timestamp", 0) < 3600:
            return entry.get("results", [])

    if _NOMINATIM_LOCK is None:
        _NOMINATIM_LOCK = asyncio.Lock()

    results: List[Dict[str, Any]] = []

    async with _NOMINATIM_LOCK:
        # Enforce >= 1.0s spacing between external calls
        elapsed = now - _LAST_NOMINATIM_TIME
        if elapsed < 1.0:
            await asyncio.sleep(1.0 - elapsed)

        try:
            headers = {
                "User-Agent": "OmniCivic-AI/1.0 (academic-civic-intelligence-project; contact: ops@omnicivic.local)"
            }
            params = {
                "q": clean_q,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 5,
            }
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params=params,
                    headers=headers
                )
                _LAST_NOMINATIM_TIME = time.time()
                if resp.status_code == 200:
                    raw_items = resp.json()
                    for item in raw_items:
                        try:
                            results.append({
                                "display_name": item.get("display_name", ""),
                                "latitude": float(item.get("lat")),
                                "longitude": float(item.get("lon")),
                                "type": item.get("type", "location"),
                                "importance": float(item.get("importance", 0.0)),
                            })
                        except (ValueError, TypeError):
                            continue
        except Exception as e:
            logger.warning("Nominatim geocode query failed: %s. Using fallback if available.", e)

    # If network/Nominatim returned results, cache and return
    if results:
        _GEOCODE_CACHE[cache_key] = {"timestamp": time.time(), "results": results}
        return results

    # Offline / Unreachable fallback: filter known municipal landmarks matching query tokens
    q_tokens = [t.lower() for t in clean_q.split() if len(t) > 1]
    fallback_matches = []
    for loc in _LOCAL_GEOCODE_FALLBACKS:
        loc_text = loc["name"].lower()
        if any(tok in loc_text for tok in q_tokens):
            fallback_matches.append({
                "display_name": loc["name"],
                "latitude": loc["lat"],
                "longitude": loc["lon"],
                "type": "city_district",
                "importance": 0.5,
                "ward": loc["ward"]
            })

    if fallback_matches:
        _GEOCODE_CACHE[cache_key] = {"timestamp": time.time(), "results": fallback_matches}
        return fallback_matches

    return []

