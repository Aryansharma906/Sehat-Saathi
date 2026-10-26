"""
Unit tests for local profile models and ClinicalDatabaseService.
Verifies that sign-in fails closed, relational schema creation,
patient data ingestion, doctor/staff clinical triage note logging, and ABDM clinical summary export.
"""

import pytest
import tempfile
from pathlib import Path
from services.auth_service import AuthService, User
from services.clinical_db_service import ClinicalDatabaseService


@pytest.fixture
def temp_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_clinical.db"
        service = ClinicalDatabaseService(db_path=db_path)
        yield service


def test_google_signin_fails_closed_without_an_oauth_flow():
    with pytest.raises(RuntimeError, match="Google sign-in is not implemented"):
        AuthService.get_google_auth_url(redirect_uri="http://localhost:8501")


def test_auth_service_roles():
    doc = AuthService.create_google_demo_user(role="doctor")
    assert doc.role == "doctor"
    assert "डॉ." in doc.name or "Dr." in doc.name
    assert doc.profile_pic == "👨‍⚕️"

    staff = AuthService.create_google_demo_user(role="staff")
    assert staff.role == "staff"
    assert staff.profile_pic == "🏥"

    patient = AuthService.create_google_demo_user(role="patient")
    assert patient.role == "patient"
    assert patient.abha_id is not None


def test_clinical_db_patient_workflow(temp_db):
    user_id = temp_db.upsert_user({
        "id": "u_test_1",
        "name": "Ramesh Kumar",
        "email": "ramesh@example.com",
        "role": "patient",
        "abha_id": "91-1234-5678-9012"
    })
    assert user_id == "u_test_1"

    pat_id = temp_db.upsert_patient({
        "id": "p_test_1",
        "user_id": user_id,
        "name": "Ramesh Kumar",
        "age": 58,
        "gender": "Male",
        "blood_group": "B+",
        "consent_shared_treatment": 1
    })
    assert pat_id == "p_test_1"

    pat = temp_db.get_patient("p_test_1")
    assert pat["name"] == "Ramesh Kumar"
    assert pat["age"] == 58
    assert pat["consent_shared_treatment"] == 1


def test_clinical_db_prescriptions_and_vitals(temp_db):
    pat_id = temp_db.upsert_patient({"id": "pat_123", "name": "Geeta Devi"})

    # Save prescription
    presc_id = temp_db.save_prescription(
        patient_id=pat_id,
        doctor_name="Dr. Aditi Sharma",
        clinic_name="Behror PHC",
        prescription_date="2026-10-26",
        raw_text="Tab Dolo 650 BD pc",
        verified_medicines=[{
            "name": "Dolo 650",
            "dose": "1 tablet",
            "timing": "After meals"
        }]
    )
    assert presc_id is not None

    prescs = temp_db.get_patient_prescriptions(pat_id)
    assert len(prescs) == 1
    assert prescs[0]["doctor_name"] == "Dr. Aditi Sharma"
    assert len(prescs[0]["verified_medicines"]) == 1

    # Save Vitals
    v_id = temp_db.save_vital(
        patient_id=pat_id,
        device_type="BP Monitor",
        metric_name="Blood Pressure",
        value="135/88",
        unit="mmHg",
        status_flag="High BP Warning"
    )
    assert v_id is not None
    vitals = temp_db.get_patient_vitals(pat_id)
    assert len(vitals) == 1
    assert vitals[0]["value"] == "135/88"


def test_clinical_db_staff_treatment_notes(temp_db):
    pat_id = temp_db.upsert_patient({"id": "pat_notes_1", "name": "Sita Ram"})

    # Doctor adds clinical note
    note_id = temp_db.add_staff_clinical_note(
        patient_id=pat_id,
        staff_id="doc_aiims_001",
        staff_name="Dr. Aditi Sharma, MD",
        staff_role="Doctor (Physician)",
        observation_notes="Patient blood pressure moderately elevated. Advised low salt diet and follow up in 7 days.",
        triage_status="Follow-up Required",
        recommended_action="Continue Amlodipine 5mg OD"
    )
    assert note_id is not None

    notes = temp_db.get_staff_clinical_notes(pat_id)
    assert len(notes) == 1
    assert notes[0]["staff_role"] == "Doctor (Physician)"
    assert notes[0]["triage_status"] == "Follow-up Required"


def test_clinical_db_export_summary(temp_db):
    pat_id = temp_db.upsert_patient({"id": "pat_exp_1", "name": "Mohan Lal", "age": 62})
    temp_db.save_vital(pat_id, "Oximeter", "SpO2", "98", "%", "Normal")
    temp_db.save_complication_prediction(
        patient_id=pat_id,
        risk_score=24.5,
        risk_tier="सामान्य जोखिम (Low Risk)",
        systolic_bp=128.0,
        diastolic_bp=82.0,
        blood_sugar=115.0,
        spo2=98.0,
        adherence_pct=95.0,
        trajectory="Stable",
        model_name="EnsembleClinicalClassifier"
    )

    summary = temp_db.export_patient_clinical_summary(pat_id)
    assert summary["record_type"] == "SehatSaathi_Clinical_Treatment_Card"
    assert summary["patient_profile"]["name"] == "Mohan Lal"
    assert len(summary["recent_vitals"]) == 1
    assert summary["ai_complication_prediction"]["risk_score"] == 24.5


def test_distinct_doctor_vs_staff_profiles(temp_db):
    # Blank user starts without pre-existing fake data
    blank_doc = AuthService.create_blank_user(role="doctor")
    assert blank_doc.name == ""
    assert blank_doc.role == "doctor"
    assert blank_doc.medical_license_no is None

    blank_staff = AuthService.create_blank_user(role="staff")
    assert blank_staff.name == ""
    assert blank_staff.role == "staff"
    assert blank_staff.staff_designation is None

    # Custom Doctor Profile
    doc = AuthService.create_custom_user(
        name="Dr. Aditi Sharma",
        role="doctor",
        medical_license_no="MCI-2014-98421",
        specialization="Cardiology",
        hospital_clinic="District Hospital, Alwar",
        qualification="MBBS, MD (Cardiology)",
        phone="9876543210"
    )
    assert doc.medical_license_no == "MCI-2014-98421"
    assert doc.specialization == "Cardiology"
    assert doc.qualification == "MBBS, MD (Cardiology)"
    assert doc.staff_designation is None

    temp_db.upsert_user(doc.model_dump())
    loaded_doc = temp_db.get_user(doc.id)
    assert loaded_doc["medical_license_no"] == "MCI-2014-98421"
    assert loaded_doc["specialization"] == "Cardiology"
    assert loaded_doc["hospital_clinic"] == "District Hospital, Alwar"

    # Custom Staff Profile
    staff = AuthService.create_custom_user(
        name="Priya Verma",
        role="staff",
        staff_designation="Senior Staff Nurse",
        employee_id="EMP-PHC-8819",
        department_ward="Maternal & Child Ward",
        hospital_clinic="Neemrana CHC",
        phone="9811223344"
    )
    assert staff.staff_designation == "Senior Staff Nurse"
    assert staff.employee_id == "EMP-PHC-8819"
    assert staff.department_ward == "Maternal & Child Ward"
    assert staff.medical_license_no is None

    temp_db.upsert_user(staff.model_dump())
    loaded_staff = temp_db.get_user(staff.id)
    assert loaded_staff["staff_designation"] == "Senior Staff Nurse"
    assert loaded_staff["employee_id"] == "EMP-PHC-8819"
    assert loaded_staff["department_ward"] == "Maternal & Child Ward"


def test_clean_empty_database_and_user_data_collection(temp_db):
    # Verify no default pre-existing data exists
    assert len(temp_db.list_all_patients()) == 0
    adh = temp_db.get_patient_adherence_rate("pat_non_existent")
    assert adh["total_scheduled"] == 0
    assert adh["percentage"] == 0.0
    assert len(temp_db.get_patient_vitals("pat_non_existent")) == 0

    # User enters their actual data
    p_id = "pat_real_001"
    u_id = "user_real_001"
    temp_db.upsert_user({
        "id": u_id,
        "name": "राम अवतार (Ram Avtar)",
        "role": "patient",
        "phone": "9414012345",
        "age": 61,
        "gender": "पुरुष (Male)",
        "blood_group": "AB+",
        "emergency_contact": "9414099999",
        "address": "गाँव माजरा, नीमराना"
    })
    temp_db.upsert_patient({
        "id": p_id,
        "user_id": u_id,
        "name": "राम अवतार (Ram Avtar)",
        "age": 61,
        "gender": "पुरुष (Male)",
        "blood_group": "AB+",
        "emergency_contact": "9414099999",
        "consent_shared_treatment": 1
    })

    patients = temp_db.list_all_patients()
    assert len(patients) == 1
    assert patients[0]["name"] == "राम अवतार (Ram Avtar)"
    assert patients[0]["age"] == 61
