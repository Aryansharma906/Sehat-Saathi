"""
Unit Tests for Reminder Service & Storage
"""

import pytest
from datetime import datetime
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
        frequency_raw="OD",
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
