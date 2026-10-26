"""
Tests for Rural Healthcare Requirements:
- Traceability (source prescription association)
- Conflict detection between new and old prescriptions
- Non-destructive schedule preservation
"""

import pytest
import tempfile
from pathlib import Path
from models.prescription import MedicineInstruction
from services.reminder_service import ReminderService
from storage.persistence import LocalStorageAdapter


@pytest.fixture
def temp_storage():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        path = Path(tf.name)
    adapter = LocalStorageAdapter(filepath=path)
    yield adapter
    if path.exists():
        path.unlink()


def test_prescription_traceability(temp_storage):
    service = ReminderService(storage_adapter=temp_storage)

    med = MedicineInstruction(
        raw_medicine_name="Tab Dolo 650",
        candidate_medicine_name="Dolo 650",
        dose_instruction_raw="1 tablet",
        frequency_raw="OD",
        user_confirmed=True
    )

    reminders = service.create_reminders_from_instruction(
        med,
        prescription_id="presc-phc-001",
        prescription_date="2026-10-26"
    )

    assert len(reminders) == 1
    rem = reminders[0]
    assert rem.source_prescription_id == "presc-phc-001"
    assert rem.source_prescription_date == "2026-10-26"
    assert rem.source_raw_text == "Tab Dolo 650"


def test_conflict_detection_different_dosage(temp_storage):
    service = ReminderService(storage_adapter=temp_storage)

    # 1. Existing prescription had Dolo 650 1 tablet
    old_med = MedicineInstruction(
        raw_medicine_name="Tab Dolo 650",
        candidate_medicine_name="Dolo 650",
        dose_instruction_raw="1 tablet",
        frequency_raw="OD",
        user_confirmed=True
    )
    service.create_reminders_from_instruction(old_med)

    # 2. New prescription arrives with Dolo 650, but dose is "2 tablets"
    new_med = MedicineInstruction(
        raw_medicine_name="Tab Dolo 650",
        candidate_medicine_name="Dolo 650",
        dose_instruction_raw="2 tablets",
        frequency_raw="BD",
        user_confirmed=True
    )

    conflicts = service.check_potential_conflicts(new_med)
    assert len(conflicts) == 1
    assert "पहले से सहेजी गई खुराक '1 tablet' है" in conflicts[0]["reason"]


def test_non_destructive_schedule_merge(temp_storage):
    service = ReminderService(storage_adapter=temp_storage)

    # First prescription
    med1 = MedicineInstruction(
        raw_medicine_name="Pan-D",
        frequency_raw="OD",
        user_confirmed=True
    )
    service.create_reminders_from_instruction(med1)
    assert len(service.get_all_reminders()) == 1

    # Second prescription
    med2 = MedicineInstruction(
        raw_medicine_name="Metformin 500mg",
        frequency_raw="OD",
        user_confirmed=True
    )
    service.create_reminders_from_instruction(med2)

    # Both must be preserved (non-destructive)
    all_reminders = service.get_all_reminders()
    assert len(all_reminders) == 2
    names = [r.medicine_name for r in all_reminders]
    assert "Pan-D" in names
    assert "Metformin 500mg" in names
