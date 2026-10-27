"""
Unit Tests for Reminder Service & Storage
"""

import pytest
from datetime import datetime, timedelta
from models.prescription import MedicineInstruction
from models.reminder import Reminder
from services.reminder_service import ReminderService
from storage.persistence import LocalStorageAdapter
import tempfile
from pathlib import Path


@pytest.fixture
def temp_storage():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        path = Path(tf.name)
    adapter = LocalStorageAdapter(filepath=path)
    yield adapter
    if path.exists():
        path.unlink()


def test_reminder_crud_lifecycle(temp_storage):
    service = ReminderService(storage_adapter=temp_storage)

    # 1. Create confirmed medicine
    med = MedicineInstruction(
        raw_medicine_name="Tab Pan-D",
        candidate_medicine_name="Pan-D",
        dose_instruction_raw="1 capsule",
        frequency_raw="OD",
        timing_raw="Before food",
        user_confirmed=True
    )
    reminders = service.create_reminders_from_instruction(med)
    assert len(reminders) == 1
    rem_id = reminders[0].id

    # 2. Toggle reminder
    new_state = service.toggle_reminder(rem_id)
    assert new_state is False

    # 3. Mark as taken
    service.mark_as_taken(rem_id, True)
    loaded = service.get_all_reminders()
    assert loaded[0].taken_today is True
    assert loaded[0].taken_date == datetime.now().date().isoformat()

    # 4. Delete reminder
    deleted = service.delete_reminder(rem_id)
    assert deleted is True
    assert len(service.get_all_reminders()) == 0


def test_is_due_now_calculation():
    service = ReminderService()
    # Create reminder for 08:30
    rem = Reminder(
        medicine_instruction_id="123",
        medicine_name="Dolo",
        reminder_time="08:30"
    )

    # Simulated time at 08:45 (diff = 15 min <= 60 min)
    dt_due = datetime(2026, 10, 26, 8, 45)
    assert service.is_due_now(rem, current_dt=dt_due) is True

    # Simulated time at 12:00 (diff = 210 min > 60 min)
    dt_future = datetime(2026, 10, 26, 12, 0)
    assert service.is_due_now(rem, current_dt=dt_future) is False

    # If marked taken today, it is no longer due
    rem.taken_today = True
    assert service.is_due_now(rem, current_dt=dt_due) is False


def test_due_window_wraps_across_midnight_and_ignores_paused_reminders():
    service = ReminderService()
    reminder = Reminder(
        medicine_instruction_id="123",
        medicine_name="Example",
        reminder_time="23:30",
    )
    just_after_midnight = datetime(2026, 10, 27, 0, 0)
    assert service.is_due_now(reminder, current_dt=just_after_midnight) is True

    reminder.enabled = False
    assert service.is_due_now(reminder, current_dt=just_after_midnight) is False


def test_taken_state_resets_after_local_calendar_day_changes(temp_storage):
    service = ReminderService(storage_adapter=temp_storage)
    reminder = Reminder(
        medicine_instruction_id="123",
        medicine_name="Example",
        reminder_time="08:30",
    )
    temp_storage.add_reminder(reminder)

    service.mark_as_taken(reminder.id, True)
    taken_dt = datetime.now()
    next_day = datetime.combine(taken_dt.date() + timedelta(days=1), taken_dt.time())
    taken_record = service.get_all_reminders(current_dt=taken_dt)[0]
    assert taken_record.taken_today is True

    reset_record = service.get_all_reminders(current_dt=next_day)[0]
    assert reset_record.taken_today is False
    assert reset_record.taken_date is None


def test_unknown_and_as_needed_frequencies_do_not_create_default_reminders(temp_storage):
    service = ReminderService(storage_adapter=temp_storage)
    for frequency in ("SOS / as needed", "when required"):
        medicine = MedicineInstruction(
            raw_medicine_name="Example",
            candidate_medicine_name="Example",
            dose_instruction_raw="1 tablet",
            frequency_raw=frequency,
            timing_raw="As prescribed",
            user_confirmed=True,
        )
        with pytest.raises(ValueError, match="does not map to a safe reminder schedule"):
            service.create_reminders_from_instruction(medicine)
    assert service.get_all_reminders() == []


def test_reminders_require_confirmed_dose_timing_and_frequency(temp_storage):
    service = ReminderService(storage_adapter=temp_storage)
    medicine = MedicineInstruction(
        raw_medicine_name="Example",
        candidate_medicine_name="Example",
        frequency_raw="OD",
        user_confirmed=True,
    )
    with pytest.raises(ValueError, match="confirmed dose is required"):
        service.create_reminders_from_instruction(medicine)
    assert service.get_all_reminders() == []
