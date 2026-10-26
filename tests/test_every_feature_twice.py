"""
Comprehensive Automated Test Suite: Testing Every Option and Feature Twice.
Verifies that all options and features across the app produce the desired output
consistently across multiple runs and state transitions.
"""

from pathlib import Path
import os
import pytest
from streamlit.testing.v1 import AppTest

from services.auth_service import AuthService
from services.clinical_db_service import ClinicalDatabaseService
from services.device_data_service import DeviceDataService
from services.reminder_service import ReminderService
from storage.persistence import LocalStorageAdapter
from services.health_issue_service import HealthIssueService
from services.progress_tracker_service import ProgressTrackerService
from services.mental_health_service import MentalHealthService
from services.prevention_and_facilities import PreventionAndFacilitiesService
from services.prescription_extractor import MockPrescriptionExtractor
from services.complication_prediction_service import (
    ComplicationPredictionService,
    ComplicationPredictionInput,
    RiskTier
)
from services.chat_service import PrescriptionChatService

MAIN_APP_PATH = Path(__file__).resolve().parent.parent / "app" / "main.py"


@pytest.fixture
def fresh_app():
    at = AppTest.from_file(str(MAIN_APP_PATH), default_timeout=25)
    at.run(timeout=25)
    return at


# =====================================================================
# 1. LANGUAGE SWITCHING (TESTED TWICE)
# =====================================================================
def test_language_switching_twice(fresh_app):
    # Pass 1: Switch to English
    fresh_app.selectbox(key="lang_selector_widget").select("🇬🇧 English")
    fresh_app.run(timeout=20)
    assert len(fresh_app.exception) == 0
    assert fresh_app.session_state.app_lang == "en"
    # Desired output: Verify English header and hub text
    hub_scan_btn = [b for b in fresh_app.button if b.key == "hub_btn_scan"][0]
    assert "Scan" in hub_scan_btn.label

    # Pass 2: Switch to Hinglish
    fresh_app.selectbox(key="lang_selector_widget").select("🌾 Hinglish")
    fresh_app.run(timeout=20)
    assert len(fresh_app.exception) == 0
    assert fresh_app.session_state.app_lang == "hinglish"
    # Desired output: Verify Hinglish header and hub text
    hub_scan_btn = [b for b in fresh_app.button if b.key == "hub_btn_scan"][0]
    assert "Parchi" in hub_scan_btn.label or "Scan" in hub_scan_btn.label

    # Reset back to Hindi
    fresh_app.selectbox(key="lang_selector_widget").select("🇮🇳 हिन्दी")
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.app_lang == "hi"


# =====================================================================
# 2. ROLE SWITCHING & PROFILE CUSTOMIZATION (TESTED TWICE)
# =====================================================================
def test_role_switching_and_profile_twice(fresh_app):
    # Pass 1: Switch to Doctor
    btn_doc = [b for b in fresh_app.button if b.key == "btn_role_doc"][0]
    btn_doc.click()
    fresh_app.run(timeout=20)
    assert len(fresh_app.exception) == 0
    assert fresh_app.session_state.current_user.role == "doctor"

    # Pass 2: Switch to Healthcare Staff
    btn_staff = [b for b in fresh_app.button if b.key == "btn_role_staff"][0]
    btn_staff.click()
    fresh_app.run(timeout=20)
    assert len(fresh_app.exception) == 0
    assert fresh_app.session_state.current_user.role == "staff"

    # Reset back to Patient
    btn_pat = [b for b in fresh_app.button if b.key == "btn_role_pat"][0]
    btn_pat.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.current_user.role == "patient"


# =====================================================================
# 3. ACTION HUB & METRIC SUMMARY TILES (TESTED TWICE)
# =====================================================================
def test_action_hub_and_metric_tiles_twice(fresh_app):
    # --- PASS 1 ---
    # Click Scan Card
    btn_scan = [b for b in fresh_app.button if b.key == "hub_btn_scan"][0]
    btn_scan.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.nav_ctrl == 0

    # Click Reminders Card
    btn_rem = [b for b in fresh_app.button if b.key == "hub_btn_reminders"][0]
    btn_rem.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.nav_ctrl == 1

    # Click Vitals Card
    btn_vit = [b for b in fresh_app.button if b.key == "hub_btn_vitals"][0]
    btn_vit.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.nav_ctrl == 2

    # Click BP Tile
    btn_bp = [b for b in fresh_app.button if b.key == "tile_btn_bp"][0]
    btn_bp.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.nav_ctrl == 2

    # Click Adherence Tile
    btn_adh = [b for b in fresh_app.button if b.key == "tile_btn_adh"][0]
    btn_adh.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.nav_ctrl == 1

    # --- PASS 2 (Repeat all clicks to verify idempotent consistency) ---
    btn_scan = [b for b in fresh_app.button if b.key == "hub_btn_scan"][0]
    btn_scan.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.nav_ctrl == 0

    btn_vit = [b for b in fresh_app.button if b.key == "hub_btn_vitals"][0]
    btn_vit.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.nav_ctrl == 2

    btn_rem = [b for b in fresh_app.button if b.key == "hub_btn_reminders"][0]
    btn_rem.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.nav_ctrl == 1

    btn_emg = [b for b in fresh_app.button if b.key == "hub_btn_emergency"][0]
    btn_emg.click()
    fresh_app.run(timeout=20)
    assert fresh_app.session_state.open_emergency_drawer is True


# =====================================================================
# 4. PRESCRIPTION SCANNING & VERIFICATION (TESTED TWICE)
# =====================================================================
def test_prescription_extractor_scenarios_twice():
    # Pass 1: Clean Scenario
    ext_clean = MockPrescriptionExtractor(scenario="clean")
    p_clean = ext_clean.extract_from_image(b"fake_image_bytes")
    assert p_clean is not None
    assert len(p_clean.medicines) >= 2
    assert any(m.is_uncertain for m in p_clean.medicines) is False
    assert p_clean.medicines[0].candidate_medicine_name is not None

    # Pass 2: Ambiguous Scenario
    ext_ambig = MockPrescriptionExtractor(scenario="ambiguous")
    p_ambig = ext_ambig.extract_from_image(b"fake_image_bytes")
    assert p_ambig is not None
    assert any(m.is_uncertain for m in p_ambig.medicines) is True
    # Desired output: Medicine marked uncertain with reason
    uncertain_meds = [m for m in p_ambig.medicines if m.is_uncertain]
    assert len(uncertain_meds) > 0
    assert uncertain_meds[0].uncertainty_reason != ""


# =====================================================================
# 5. REMINDERS, ADHERENCE & LOGGING (TESTED TWICE)
# =====================================================================
def test_reminders_and_adherence_flow_twice(tmp_path):
    storage = LocalStorageAdapter()
    rem_service = ReminderService(storage_adapter=storage)
    prog_service = ProgressTrackerService(filepath=tmp_path / "progress.json")
    issue_service = HealthIssueService(filepath=tmp_path / "issues.json")

    # Pass 1: Create reminder and mark taken
    ext = MockPrescriptionExtractor(scenario="clean")
    presc = ext.extract_from_image(b"bytes")
    presc.medicines[0].user_confirmed = True
    created = rem_service.create_reminders_from_instruction(presc.medicines[0])
    assert len(created) > 0
    rem_id = created[0].id
    rem_service.mark_as_taken(rem_id, True)
    rems = [r for r in rem_service.get_all_reminders() if r.id == rem_id]
    assert rems[0].taken_today is True

    # Progress Checkin 1: Good Recovery
    res1 = prog_service.evaluate_checkin(
        feeling="😊 बहुत आराम है (Feeling Much Better)",
        adherence="✅ हां, सभी खुराक समय पर लीं (All Doses on Time)",
        symptoms="🟢 लक्षण लगभग खत्म हो चुके हैं (Fully Relieved)",
        lang="en"
    )
    assert res1.recovery_score >= 80
    assert not res1.doctor_visit_advised

    # Issue Log 1: Mild
    iss1 = issue_service.log_issue("Paracetamol", "Nausea", "Mild", "Mild dizziness after food")
    assert not iss1.is_severe_alert

    # Pass 2: Second checkin and Severe issue
    # Progress Checkin 2: Poor Recovery
    res2 = prog_service.evaluate_checkin(
        feeling="😣 तबीयत और खराब हुई (Feeling Worse)",
        adherence="❌ दवाइयां ठीक से नहीं ले पाए (Missed Many Doses)",
        symptoms="🔴 लक्षण वैसे ही बने हुए हैं (No Relief)",
        lang="en"
    )
    assert res2.recovery_score < 40
    assert res2.doctor_visit_advised is True

    # Issue Log 2: Severe Chest Pain
    iss2 = issue_service.log_issue("Amlodipine", "Chest Pain", "Severe", "Sharp chest pain experienced")
    assert iss2.is_severe_alert is True


# =====================================================================
# 6. HEALTH DEVICES & ML COMPLICATION PREDICTION (TESTED TWICE)
# =====================================================================
def test_health_devices_and_ml_prediction_twice(tmp_path):
    dev_service = DeviceDataService(filepath=tmp_path / "vitals.json")
    mental_service = MentalHealthService(filepath=tmp_path / "mental.json")

    # Pass 1: Normal vitals & Low risk prediction
    v1 = dev_service.record_reading("Pulse Oximeter", "SpO2", "98", "%")
    assert "Normal" in v1.status_flag or "सामान्य" in v1.status_flag
    assert v1.alert_message is None

    pred1 = ComplicationPredictionService.predict_complication_risk(
        ComplicationPredictionInput(
            age=50, systolic_bp=120, diastolic_bp=80,
            blood_sugar=105, spo2=98, adherence_percentage=95,
            active_medications_count=2
        ),
        lang="en"
    )
    assert pred1.risk_tier == RiskTier.LOW
    assert pred1.risk_score_percentage < 30.0

    mental1 = mental_service.evaluate_mental_wellness(
        sleep="Good Sleep", stress="Normal", mood="Positive", lang="en"
    )
    assert mental1.wellness_score >= 80
    assert not mental1.tele_manas_recommended

    # Pass 2: Critical vitals & High risk prediction
    v2 = dev_service.record_reading("Digital BP Monitor", "Blood Pressure", "175/105", "mmHg")
    assert "BP" in v2.status_flag or "रक्तचाप" in v2.status_flag or "Alert" in v2.status_flag
    assert v2.alert_message is not None

    pred2 = ComplicationPredictionService.predict_complication_risk(
        ComplicationPredictionInput(
            age=68, systolic_bp=175, diastolic_bp=105,
            blood_sugar=255, spo2=91, adherence_percentage=35,
            active_medications_count=4
        ),
        lang="en"
    )
    assert pred2.risk_tier == RiskTier.HIGH
    assert pred2.risk_score_percentage >= 50.0

    mental2 = mental_service.evaluate_mental_wellness(
        sleep="Insomnia", stress="Extreme", mood="Low", lang="en"
    )
    assert mental2.wellness_score < 40
    assert mental2.tele_manas_recommended is True


# =====================================================================
# 7. NEARBY FACILITIES & MAPS GENERATION (TESTED TWICE)
# =====================================================================
def test_facilities_and_prevention_twice():
    # Pass 1: Neemrana locality
    url_phc1 = PreventionAndFacilitiesService.build_maps_search_url("PHC Hospital", "Neemrana")
    assert "Neemrana" in url_phc1
    assert "https://www.google.com/maps/search/?api=1" in url_phc1

    # Pass 2: Behror locality
    url_phc2 = PreventionAndFacilitiesService.build_maps_search_url("Medical Store", "Behror")
    assert "Behror" in url_phc2
    assert "https://www.google.com/maps/search/?api=1" in url_phc2


# =====================================================================
# 8. CLINICAL SAFETY PRESCRIPTION CHAT (TESTED TWICE)
# =====================================================================
def test_prescription_chat_twice():
    chat = PrescriptionChatService()
    ext = MockPrescriptionExtractor(scenario="clean")
    presc = ext.extract_from_image(b"bytes")

    # Pass 1: Timing question
    ans1 = chat.ask_question("Should I take this medicine before or after food?", presc)
    assert len(ans1.strip()) > 10

    # Pass 2: Missed dose question
    ans2 = chat.ask_question("What should I do if I miss a dose?", presc)
    assert len(ans2.strip()) > 10
    # Must enforce safety disclaimer or doctor advice
    assert "डॉक्टर" in ans2 or "doctor" in ans2.lower() or "dawai" in ans2.lower()


# =====================================================================
# 9. CLINICAL RELATIONAL DATABASE & PATIENT RECORDS (TESTED TWICE)
# =====================================================================
def test_clinical_database_patient_flow_twice(tmp_path):
    db_file = tmp_path / "test_clinical.db"
    db = ClinicalDatabaseService(db_path=db_file)

    # Pass 1: Register Patient 1
    u1 = db.upsert_user({"id": "u1", "name": "Patient One", "role": "patient", "phone": "9876543210"})
    p1 = db.upsert_patient({"id": "p1", "user_id": u1, "name": "Patient One", "age": 55, "gender": "Male", "blood_group": "B+"})
    db.save_vital(p1, "BP", "Blood Pressure", "130/80", "mmHg", "Normal")
    db.record_adherence(p1, "Med A", "1 tab", "Morning", "08:00", taken_status=True)
    db.add_staff_clinical_note(p1, "doc_1", "Dr. Sharma", "Physician", "Routine follow up", "Follow-up", "Continue meds")

    vitals1 = db.get_patient_vitals(p1)
    assert len(vitals1) == 1
    assert vitals1[0]["value"] == "130/80"

    notes1 = db.get_staff_clinical_notes(p1)
    assert len(notes1) == 1
    assert notes1[0]["staff_name"] == "Dr. Sharma"

    # Pass 2: Register Patient 2
    u2 = db.upsert_user({"id": "u2", "name": "Patient Two", "role": "patient", "phone": "9123456789"})
    p2 = db.upsert_patient({"id": "p2", "user_id": u2, "name": "Patient Two", "age": 62, "gender": "Female", "blood_group": "O+"})
    db.save_vital(p2, "Oximeter", "SpO2", "99", "%", "Normal")
    db.record_adherence(p2, "Med B", "1 tab", "Night", "21:00", taken_status=True)
    db.add_staff_clinical_note(p2, "staff_1", "Nurse Sunita", "Nurse", "Vitals stable", "Routine", "Hydration")

    vitals2 = db.get_patient_vitals(p2)
    assert len(vitals2) == 1
    assert vitals2[0]["value"] == "99"

    notes2 = db.get_staff_clinical_notes(p2)
    assert len(notes2) == 1
    assert notes2[0]["staff_name"] == "Nurse Sunita"

    # Verify patient count
    all_pats = db.list_all_patients()
    assert len(all_pats) == 2


# =====================================================================
# 10. APP INTEGRATION: COMPLETE NAVIGATION & WORKFLOW (TESTED TWICE)
# =====================================================================
def test_full_app_workflow_navigation_twice(fresh_app):
    # Pass 1: Walkthrough Tabs 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6
    for tab_idx in range(7):
        fresh_app.segmented_control[0].select(tab_idx)
        fresh_app.run(timeout=15)
        assert len(fresh_app.exception) == 0

    # Pass 2: Reverse Walkthrough Tabs 6 -> 5 -> 4 -> 3 -> 2 -> 1 -> 0
    for tab_idx in range(6, -1, -1):
        fresh_app.segmented_control[0].select(tab_idx)
        fresh_app.run(timeout=15)
        assert len(fresh_app.exception) == 0
