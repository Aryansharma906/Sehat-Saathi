"""
Automated UI and Options Navigation Tests using Streamlit AppTest.
Ensures that all navigation options, role switchers, device selections,
colored hub buttons, metric tiles, and language pickers operate without exceptions.
"""

from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

MAIN_APP_PATH = Path(__file__).resolve().parent.parent / "app" / "main.py"


@pytest.fixture
def app():
    at = AppTest.from_file(str(MAIN_APP_PATH), default_timeout=20)
    at.run(timeout=20)
    return at


def test_app_initial_load(app):
    assert len(app.exception) == 0
    assert len(app.button) > 0


def test_colored_action_hub_cards_clickable(app):
    # Click Colored Hub Button 2 (Reminders)
    btn_rem = [b for b in app.button if b.key == "hub_btn_reminders"][0]
    btn_rem.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.nav_ctrl == 1

    # Click Colored Hub Button 3 (Vitals)
    btn_vit = [b for b in app.button if b.key == "hub_btn_vitals"][0]
    btn_vit.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.nav_ctrl == 2

    # Click Colored Hub Button 1 (Scan)
    btn_scan = [b for b in app.button if b.key == "hub_btn_scan"][0]
    btn_scan.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.nav_ctrl == 0

    # Click Emergency Hub Button
    btn_emg = [b for b in app.button if b.key == "hub_btn_emergency"][0]
    btn_emg.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.open_emergency_drawer is True


def test_summary_metric_tiles_clickable(app):
    # Click BP metric tile -> navigates to Vitals (nav_ctrl = 2)
    btn_bp = [b for b in app.button if b.key == "tile_btn_bp"][0]
    btn_bp.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.nav_ctrl == 2

    # Click Adherence tile -> navigates to Reminders (nav_ctrl = 1)
    btn_adh = [b for b in app.button if b.key == "tile_btn_adh"][0]
    btn_adh.click()
    app.run(timeout=15)
    assert len(app.exception) == 0
    assert app.session_state.nav_ctrl == 1


def test_emergency_drawer_link_buttons(app):
    # Open drawer
    app.session_state.open_emergency_drawer = True
    app.run(timeout=15)
    assert len(app.exception) == 0

    # Verify link buttons exist and have correct tel schemes
    call_108 = [l for l in app.link_button if l.key == "emg_call_108"]
    assert len(call_108) == 1
    assert call_108[0].url == "tel:108"


def test_segmented_control_tab_switching(app):
    # Switch to Clinics & Care (Index 3)
    app.segmented_control[0].select(3)
    app.run(timeout=15)
    assert len(app.exception) == 0

    # Verify maps link buttons in Tab 4
    map_links = [l for l in app.link_button if "link_maps_" in str(l.key)]
    assert len(map_links) == 4

    # Switch to Doctor & Staff Portal (Index 5)
    app.segmented_control[0].select(5)
    app.run(timeout=15)
    assert len(app.exception) == 0

    # Switch to Settings (Index 6)
    app.segmented_control[0].select(6)
    app.run(timeout=15)
    assert len(app.exception) == 0


def test_role_and_language_switching(app):
    # Switch to Doctor
    doc_btn = [b for b in app.button if b.key == "btn_role_doc"][0]
    doc_btn.click()
    app.run(timeout=15)
    assert len(app.exception) == 0

    # Switch to English
    lang_sb = [s for s in app.selectbox if s.key == "lang_selector_widget"][0]
    lang_sb.select("🇬🇧 English")
    app.run(timeout=15)
    assert len(app.exception) == 0
