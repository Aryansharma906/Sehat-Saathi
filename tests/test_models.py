"""
Unit Tests for Pydantic Data Models and Safety Invariants
"""

import pytest
from models.prescription import MedicineInstruction, Prescription, ExtractionStatus
from models.reminder import Reminder, ReminderSchedule


def test_medicine_instruction_requires_raw_name():
    with pytest.raises(ValueError):
        MedicineInstruction(raw_medicine_name="   ")


def test_unknown_values_remain_none():
    med = MedicineInstruction(raw_medicine_name="Tab Paracetamol")
    assert med.dose_instruction_raw is None
    assert med.frequency_raw is None
    assert med.duration_raw is None
    assert med.timing_raw is None
    assert med.is_uncertain is False
    assert med.user_confirmed is False


def test_safety_gate_cannot_create_reminders_without_confirmation():
    med = MedicineInstruction(
        raw_medicine_name="Dolo 650",
        dose_instruction_raw="1 tablet",
        frequency_raw="TDS",
        is_uncertain=True,
        user_confirmed=False
    )
    prescription = Prescription(medicines=[med])
    # Safety Invariant: cannot create reminders while unconfirmed
    assert prescription.can_create_reminders() is False

    # Once user confirms:
    med.user_confirmed = True
    assert prescription.can_create_reminders() is True


def test_reminder_time_validation():
    # Valid time
    r = Reminder(
        medicine_instruction_id="test-123",
        medicine_name="Dolo 650",
        reminder_time="08:30"
    )
    assert r.reminder_time == "08:30"

    # Invalid time format raises ValueError
    with pytest.raises(ValueError):
        Reminder(
            medicine_instruction_id="test-123",
            medicine_name="Dolo 650",
            reminder_time="25:99"
        )
