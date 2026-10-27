from services import openstreetmap_facilities as osm


def test_live_lookup_geocodes_manual_city_and_maps_places_to_safe_cards(monkeypatch):
    monkeypatch.setattr(osm, "_geocode_locality", lambda locality: (19.076, 72.8777))
    monkeypatch.setattr(
        osm,
        "_query_overpass",
        lambda latitude, longitude, radius: (
            {
                "type": "node",
                "id": 123,
                "lat": 19.0762,
                "lon": 72.878,
                "tags": {
                    "amenity": "pharmacy",
                    "name": "Community Pharmacy",
                    "addr:street": "Example Road",
                    "opening_hours": "Mo-Sa 09:00-21:00",
                },
            },
            {
                "type": "node",
                "id": 456,
                "lat": 19.5,
                "lon": 73.2,
                "tags": {"amenity": "pharmacy", "name": "Too Far"},
            },
        ),
    )

    result = osm.OpenStreetMapFacilityService.search(
        locality="Mumbai",
        latitude=None,
        longitude=None,
        max_radius_miles=10,
    )

    assert (result["latitude"], result["longitude"]) == (19.076, 72.8777)
    assert result["status"] == "live_openstreetmap"
    assert len(result["facilities"]) == 1
    pharmacy = result["facilities"][0]
    assert pharmacy["name_en"] == "Community Pharmacy"
    assert pharmacy["category"] == "chemist"
    assert pharmacy["phone"] is None
    assert "tel_url" not in pharmacy
    assert pharmacy["source_url"] == "https://www.openstreetmap.org/node/123"
    assert pharmacy["distance_miles"] <= 10


def test_live_lookup_applies_category_filter(monkeypatch):
    monkeypatch.setattr(
        osm,
        "_query_overpass",
        lambda latitude, longitude, radius: (
            {
                "type": "node",
                "id": 1,
                "lat": 27.99,
                "lon": 76.39,
                "tags": {"amenity": "pharmacy", "name": "Pharmacy"},
            },
            {
                "type": "node",
                "id": 2,
                "lat": 27.99,
                "lon": 76.39,
                "tags": {"amenity": "hospital", "name": "Hospital"},
            },
        ),
    )

    result = osm.OpenStreetMapFacilityService.search(
        locality="Near Neemrana",
        latitude=27.989,
        longitude=76.388,
        max_radius_miles=10,
        category="chemist",
    )

    assert [facility["name_en"] for facility in result["facilities"]] == ["Pharmacy"]
