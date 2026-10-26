"""
Unit Tests for Environmental Health, Disease Prevention & Facility Locator Service
"""

import pytest
from services.prevention_and_facilities import PreventionAndFacilitiesService


def test_prevention_topics_completeness():
    topics = PreventionAndFacilitiesService.get_prevention_topics()
    assert len(topics) >= 4

    ids = [t["id"] for t in topics]
    assert "mosquito" in ids
    assert "waterborne" in ids
    assert "respiratory_clean_air" in ids
    assert "hygiene" in ids

    for t in topics:
        assert "icon" in t
        assert "title_hindi" in t
        assert len(t["action_points"]) >= 3
        # Invariant: Must not offer diagnosis or prescription
        for point in t["action_points"]:
            assert "हम गारंटी देते हैं" not in point


def test_maps_url_generation():
    # 1. Default "near me" query
    url_phc = PreventionAndFacilitiesService.build_maps_search_url("Primary Health Centre")
    assert "https://www.google.com/maps/search/?api=1&query=" in url_phc
    assert "Primary%20Health%20Centre%20near%20me" in url_phc

    # 2. Location-specific query
    url_ja = PreventionAndFacilitiesService.build_maps_search_url("Jan Aushadhi Kendra", user_location="Jaipur")
    assert "Jan%20Aushadhi%20Kendra%20in%20Jaipur" in url_ja


def test_sample_facilities_coordinates():
    facilities = PreventionAndFacilitiesService.get_sample_facilities()
    assert len(facilities) >= 3

    for fac in facilities:
        assert "name" in fac
        assert "latitude" in fac
        assert "longitude" in fac
        assert -90.0 <= fac["latitude"] <= 90.0
        assert -180.0 <= fac["longitude"] <= 180.0
