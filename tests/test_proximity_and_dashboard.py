"""
Unit & Integration Tests for 10-Mile Proximity Radar, Nearest Clinic Suggestions,
and Menu & Dashboard Navigation (Tested Twice).
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from services.proximity_service import (
    ProximityLocationService,
    haversine_distance_miles,
    VERIFIED_MEDICAL_FACILITIES
)

MAIN_APP_PATH = Path(__file__).resolve().parent.parent / "app" / "main.py"


@pytest.fixture
def app():
    at = AppTest.from_file(str(MAIN_APP_PATH), default_timeout=25)
    at.run(timeout=25)
    return at


# =====================================================================
# 1. HAVERSINE GEODESIC CALCULATION (TESTED TWICE)
# =====================================================================
def test_haversine_distance_precision_twice():
    # Pass 1: Identical coordinates must be 0.0 miles
    dist_zero = haversine_distance_miles(27.9889, 76.3883, 27.9889, 76.3883)
    assert dist_zero == 0.0

    # Pass 2: Distance between Neemrana and Behror (~8 to 10 miles)
    dist_neem_behror = haversine_distance_miles(27.9889, 76.3883, 27.8876, 76.2818)
    assert 8.0 < dist_neem_behror < 12.0


# =====================================================================
# 2. 10-MILE PROXIMITY RADAR FILTERING (TESTED TWICE)
# =====================================================================
def test_proximity_filtering_within_10_miles_twice():
    # Pass 1: Neemrana locality with strict 10.0 mile radius
    res1 = ProximityLocationService.find_facilities_within_proximity(
        locality="Neemrana",
        max_radius_miles=10.0
    )
    assert res1["max_radius_miles"] == 10.0
    assert res1["total_found"] > 0
    # Every returned facility MUST be <= 10.0 miles
    for fac in res1["facilities"]:
        assert fac["distance_miles"] <= 10.0

    # Nearest facility must have directions and telephone URL
    nearest1 = res1["nearest_facility"]
    assert nearest1 is not None
    assert nearest1["distance_miles"] < 3.0
    assert nearest1["directions_url"].startswith("https://www.google.com/maps/dir/")
    assert nearest1["tel_url"].startswith("tel:")

    # Pass 2: Behror locality with strict 10.0 mile radius
    res2 = ProximityLocationService.find_facilities_within_proximity(
        locality="Behror",
        max_radius_miles=10.0
    )
    assert res2["total_found"] > 0
    for fac in res2["facilities"]:
        assert fac["distance_miles"] <= 10.0

    nearest2 = res2["nearest_facility"]
    assert nearest2 is not None
    assert nearest2["distance_miles"] < 3.0
    assert nearest2["tel_url"].startswith("tel:")


# =====================================================================
# 3. FACILITY CATEGORY FILTERING (TESTED TWICE)
# =====================================================================
def test_proximity_category_filters_twice():
    # Pass 1: Filter by 'clinic' only
    clinics_res = ProximityLocationService.find_facilities_within_proximity(
        locality="Neemrana",
        max_radius_miles=10.0,
        category="clinic"
    )
    for f in clinics_res["facilities"]:
        assert f["category"] == "clinic"

    # Pass 2: Filter by 'chemist' only
    chemists_res = ProximityLocationService.find_facilities_within_proximity(
        locality="Neemrana",
        max_radius_miles=10.0,
        category="chemist"
    )
    for f in chemists_res["facilities"]:
        assert f["category"] == "chemist"


# =====================================================================
# 4. MENU & DASHBOARD UI NAVIGATION WORKFLOW (TESTED TWICE)
# =====================================================================
def test_menu_and_dashboard_navigation_twice(app):
    # Pass 1: Switch to Dashboard via View Button
    dash_tab_btn = [b for b in app.button if b.key == "view_tab_dashboard"][0]
    dash_tab_btn.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.active_view == "dashboard"

    # Verify Dashboard contains the 10-mile Spotlight facility buttons
    dash_call = [l for l in app.link_button if l.key == "dash_spotlight_call"]
    assert len(dash_call) == 1
    assert dash_call[0].url.startswith("tel:")

    dash_dir = [l for l in app.link_button if l.key == "dash_spotlight_dir"]
    assert len(dash_dir) == 1
    assert "google.com/maps/dir" in dash_dir[0].url

    # Click button on Dashboard to open full Facilities screen
    dash_open_fac = [b for b in app.button if b.key == "dash_open_fac_btn"][0]
    dash_open_fac.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.active_view == "screen"
    assert app.session_state.nav_ctrl == 3

    # On Facilities screen, verify back to dashboard button exists
    ret_btn = [b for b in app.button if b.key == "btn_return_dashboard"][0]
    ret_btn.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.active_view == "dashboard"

    # Pass 2: Use Menu Popover to Navigate to Reminders and Back
    menu_rem_btn = [b for b in app.button if b.key == "menu_item_reminders"][0]
    menu_rem_btn.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.active_view == "screen"
    assert app.session_state.nav_ctrl == 1

    # Return to Dashboard via Menu item
    menu_dash_btn = [b for b in app.button if b.key == "menu_item_dash"][0]
    menu_dash_btn.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.active_view == "dashboard"
