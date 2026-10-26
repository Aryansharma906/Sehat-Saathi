"""
Tests for Discard & Mistake Recovery Features
Verifies that users can discard/clear draft prescriptions, unwanted extracted medicines,
inactive or all reminder schedules, logged adverse issues, and device vitals.
"""

import pytest
from pathlib import Path
from models.prescription import Prescription, MedicineInstruction
from models.reminder import Reminder
from services.reminder_service import ReminderService
from services.health_issue_service import HealthIssueService
from services.device_data_service import DeviceDataService
from services.progress_tracker_service import ProgressTrackerService
from services.mental_health_service import MentalHealthService
from storage.persistence import LocalStorageAdapter


def test_prescription_discard_individual_medicine():
    """Verify that a user can discard an unwanted or non-medicinal instruction from review."""
    med1 = MedicineInstruction(raw_medicine_name="Paracetamol 500mg")
    med2 = MedicineInstruction(raw_medicine_name="Consultation Fee Rs 500")  # Non-medicine OCR artifact
    med3 = MedicineInstruction(raw_medicine_name="Cetirizine 10mg")

    presc = Prescription(medicines=[med1, med2, med3])
    assert len(presc.medicines) == 3

    # Discard med2
    res = presc.discard_medicine(med2.id)
    assert res is True
    assert len(presc.medicines) == 2
    assert [m.raw_medicine_name for m in presc.medicines] == ["Paracetamol 500mg", "Cetirizine 10mg"]

    # Discard non-existent ID
    res_fake = presc.discard_medicine("non_existent_id")
    assert res_fake is False
    assert len(presc.medicines) == 2


def test_reminder_service_discard_inactive_and_all(tmp_path):
    """Verify discarding inactive schedules and clearing all schedules."""
    storage = LocalStorageAdapter(tmp_path / "reminders_test.json")
    service = ReminderService(storage_adapter=storage)

    r1 = Reminder(
        medicine_instruction_id="inst_1",
        medicine_name="Paracetamol",
        timing_label="सुबह",
        reminder_time="08:00",
        enabled=True,
        user_confirmed=True
    )
    r2 = Reminder(
        medicine_instruction_id="inst_2",
        medicine_name="Old Antibiotic",
        timing_label="रात",
        reminder_time="20:00",
        enabled=False,  # Inactive
        user_confirmed=True
    )
    r3 = Reminder(
        medicine_instruction_id="inst_3",
        medicine_name="Old Cough Syrup",
        timing_label="दोपहर",
        reminder_time="14:00",
        enabled=False,  # Inactive
        user_confirmed=True
    )

    storage.add_reminder(r1)
    storage.add_reminder(r2)
    storage.add_reminder(r3)

    assert len(service.get_all_reminders()) == 3

    # Discard inactive only
    discarded = service.discard_inactive_reminders()
    assert discarded == 2
    remaining = service.get_all_reminders()
    assert len(remaining) == 1
    assert remaining[0].medicine_name == "Paracetamol"

    # Delete all reminders
    service.delete_all_reminders()
    assert len(service.get_all_reminders()) == 0


def test_health_issue_discard(tmp_path):
    """Verify discarding a logged health issue."""
    issue_file = tmp_path / "issues.json"
    service = HealthIssueService(filepath=issue_file)

    log1 = service.log_issue("Paracetamol", "उल्टी या जी मिचलाना")
    log2 = service.log_issue("Amoxicillin", "त्वचा पर लाल चकत्ते")
    assert len(service.get_all_issues()) == 2

    # Delete log1
    del_res = service.delete_issue(log1.id)
    assert del_res is True
    assert len(service.get_all_issues()) == 1
    assert service.get_all_issues()[0].id == log2.id

    # Discard all issues
    service.clear_issues()
    assert len(service.get_all_issues()) == 0


def test_device_data_discard(tmp_path):
    """Verify discarding a recorded vital reading."""
    dev_file = tmp_path / "vitals.json"
    service = DeviceDataService(filepath=dev_file)

    r1 = service.record_reading("BP Monitor", "Blood Pressure", "120/80", "mmHg")
    r2 = service.record_reading("Pulse Oximeter", "SpO2", "98", "%")
    assert len(service.get_all_readings()) == 2

    # Discard r1
    del_res = service.delete_reading(r1.id)
    assert del_res is True
    assert len(service.get_all_readings()) == 1
    assert service.get_all_readings()[0].id == r2.id

    # Clear all
    service.clear_readings()
    assert len(service.get_all_readings()) == 0


def test_progress_and_mental_health_discard(tmp_path):
    """Verify discarding progress and mental health check-ins."""
    p_service = ProgressTrackerService(filepath=tmp_path / "progress.json")
    c1 = p_service.evaluate_checkin(
        "😊 बहुत आराम है (Feeling Much Better)",
        "✅ हां, सभी खुराक समय पर लीं (All Doses on Time)",
        "🟢 लक्षण लगभग खत्म हो चुके हैं (Fully Relieved)"
    )
    assert len(p_service.get_all_checkins()) == 1
    assert p_service.delete_checkin(c1.id) is True
    assert len(p_service.get_all_checkins()) == 0

    m_service = MentalHealthService(filepath=tmp_path / "mental.json")
    m1 = m_service.evaluate_mental_wellness(
        "अच्छी नींद (Good Sleep)",
        "सामान्य (Normal)",
        "प्रसन्न (Happy / Positive)"
    )
    assert len(m_service.get_all_checkins()) == 1
    assert m_service.delete_checkin(m1.id) is True
    assert len(m_service.get_all_checkins()) == 0
