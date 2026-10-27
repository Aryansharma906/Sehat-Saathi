"""Best-effort live nearby-care lookup using OpenStreetMap data."""

from functools import lru_cache
import threading
import time
from typing import Any

import requests

from services.proximity_service import (
    ProximityLocationService,
    haversine_distance_miles,
)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "SehatSaathiResearchPrototype/1.0"
MAX_LIVE_RADIUS_MILES = 20.0
REQUEST_TIMEOUT_SECONDS = 12

_nominatim_lock = threading.Lock()
_last_nominatim_request = 0.0


def _headers() -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }


@lru_cache(maxsize=128)
def _geocode_locality(locality: str) -> tuple[float, float] | None:
    """Resolve a city using Nominatim, caching results and pacing public requests."""
    global _last_nominatim_request
    with _nominatim_lock:
        delay = 1.0 - (time.monotonic() - _last_nominatim_request)
        if delay > 0:
            time.sleep(delay)
        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": locality,
                "country": "India",
                "countrycodes": "in",
                "format": "jsonv2",
                "limit": 1,
            },
            headers=_headers(),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        _last_nominatim_request = time.monotonic()
    response.raise_for_status()
    matches = response.json()
    if not isinstance(matches, list) or not matches:
        return None
    try:
        latitude = float(matches[0]["lat"])
        longitude = float(matches[0]["lon"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("OpenStreetMap returned invalid coordinates for this location.") from exc
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("OpenStreetMap returned invalid coordinates for this location.")
    return latitude, longitude


@lru_cache(maxsize=256)
def _query_overpass(latitude: float, longitude: float, radius_miles: float) -> tuple[dict[str, Any], ...]:
    radius_meters = int(min(radius_miles, MAX_LIVE_RADIUS_MILES) * 1609.34)
    query = (
        f'[out:json][timeout:10];('
        f'nwr["amenity"~"^(hospital|clinic|doctors|pharmacy)$"]'
        f'(around:{radius_meters},{latitude:.6f},{longitude:.6f});'
        f'nwr["healthcare"~"^(hospital|clinic|doctor|pharmacy)$"]'
        f'(around:{radius_meters},{latitude:.6f},{longitude:.6f});'
        f');out center tags 60;'
    )
    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers=_headers(),
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    elements = payload.get("elements", [])
    if not isinstance(elements, list):
        raise ValueError("OpenStreetMap returned an invalid facility list.")
    return tuple(element for element in elements if isinstance(element, dict))


def _facility_from_element(
    element: dict[str, Any],
    user_latitude: float,
    user_longitude: float,
    locality: str,
    max_radius_miles: float,
    category: str | None,
) -> dict[str, Any] | None:
    tags = element.get("tags")
    if not isinstance(tags, dict):
        return None

    amenity = str(tags.get("amenity", "")).lower()
    healthcare = str(tags.get("healthcare", "")).lower()
    facility_type = amenity or healthcare
    if facility_type in {"pharmacy"}:
        facility_category = "chemist"
        category_label = "PHARMACY"
    elif facility_type in {"doctors", "doctor"}:
        facility_category = "doctor"
        category_label = "DOCTOR / CLINIC"
    elif facility_type in {"hospital", "clinic"}:
        facility_category = "clinic"
        category_label = "HEALTH CENTRE"
    else:
        return None
    if category and category != "all" and facility_category != category:
        return None

    center = element.get("center", {})
    try:
        latitude = float(element.get("lat", center.get("lat")))
        longitude = float(element.get("lon", center.get("lon")))
    except (TypeError, ValueError):
        return None
    distance = haversine_distance_miles(user_latitude, user_longitude, latitude, longitude)
    if distance > max_radius_miles:
        return None

    name = str(tags.get("name") or tags.get("name:en") or tags.get("name:hi") or "Unnamed medical facility")
    address_parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:suburb"),
        tags.get("addr:city"),
        tags.get("addr:state"),
    ]
    address = ", ".join(str(part) for part in address_parts if part) or locality
    element_type = str(element.get("type", "node"))
    element_id = element.get("id")
    if element_type not in {"node", "way", "relation"} or not isinstance(element_id, int):
        return None

    services = []
    specialty = tags.get("healthcare:speciality") or tags.get("healthcare:specialty")
    if specialty:
        services.append(str(specialty))
    opening_hours = str(tags.get("opening_hours") or "Hours not listed")
    phone = str(tags.get("phone") or tags.get("contact:phone") or "").strip()
    directions_url = ProximityLocationService.build_directions_url(latitude, longitude, name)
    facility = {
        "id": f"osm_{element_type}_{element_id}",
        "name_hindi": str(tags.get("name:hi") or name),
        "name_en": name,
        "category": facility_category,
        "category_label": category_label,
        "locality": locality,
        "address": address,
        "latitude": latitude,
        "longitude": longitude,
        "phone": phone or None,
        "timing": opening_hours,
        "support_available": False,
        "services": services,
        "is_24x7": opening_hours.lower() in {"24/7", "24 hours", "24/7 open"},
        "distance_miles": distance,
        "distance_km": round(distance * 1.60934, 2),
        "directions_url": directions_url,
        "source": "OpenStreetMap",
        "source_url": f"https://www.openstreetmap.org/{element_type}/{element_id}",
    }
    if phone:
        facility["tel_url"] = f"tel:{phone}"
    return facility


class OpenStreetMapFacilityService:
    """Geocode manual Indian cities and fetch nearby community-mapped care locations."""

    @classmethod
    def search(
        cls,
        locality: str,
        latitude: float | None,
        longitude: float | None,
        max_radius_miles: float,
        category: str | None = None,
    ) -> dict[str, Any]:
        if latitude is None or longitude is None:
            cleaned_locality = locality.strip()
            if not cleaned_locality or len(cleaned_locality) > 120:
                raise ValueError("Enter a town or city name no longer than 120 characters.")
            coordinates = _geocode_locality(cleaned_locality)
            if coordinates is None:
                return {
                    "latitude": None,
                    "longitude": None,
                    "facilities": [],
                    "status": "location_not_found",
                    "notice": "OpenStreetMap could not find this town or city in India.",
                }
            latitude, longitude = coordinates

        lookup_radius = min(max_radius_miles, MAX_LIVE_RADIUS_MILES)
        elements = _query_overpass(round(latitude, 5), round(longitude, 5), round(lookup_radius, 2))
        facilities = [
            item
            for element in elements
            if (item := _facility_from_element(
                element, latitude, longitude, locality, max_radius_miles, category
            ))
        ]
        facilities.sort(key=lambda item: item["distance_miles"])
        return {
            "latitude": latitude,
            "longitude": longitude,
            "facilities": facilities,
            "status": "live_openstreetmap" if facilities else "live_openstreetmap_empty",
            "notice": (
                "Community-mapped OpenStreetMap listings; details may be incomplete or out of date. Please confirm before travelling."
                if facilities
                else "No nearby medical places were found in OpenStreetMap data."
            ),
        }
