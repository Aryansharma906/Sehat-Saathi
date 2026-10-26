"""
Persistence Adapter for Saved Medication Schedules
Allows storing, updating, and deleting reminders locally without cloud DB lock-in.
Privacy invariant: Zero patient photos or raw unconfirmed health records stored.
"""

import json
import os
from pathlib import Path
from typing import List, Optional
from models.reminder import Reminder, ReminderSchedule
from services.storage_config import get_data_dir


DEFAULT_DATA_DIR = get_data_dir()
DEFAULT_SCHEDULES_FILE = DEFAULT_DATA_DIR / "saved_schedules.json"


class LocalStorageAdapter:
    """
    JSON-based local storage implementation for Sehat Saathi.
    """

    def __init__(self, filepath: Path = DEFAULT_SCHEDULES_FILE):
        self.filepath = Path(filepath)
        self._ensure_storage_ready()

    def _ensure_storage_ready(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self._write_raw([])

    def _read_raw(self) -> List[dict]:
        try:
            if not self.filepath.exists():
                return []
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except Exception:
            return []

    def _write_raw(self, data: List[dict]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_all_reminders(self) -> List[Reminder]:
        raw = self._read_raw()
        reminders = []
        for item in raw:
            try:
                reminders.append(Reminder.model_validate(item))
            except Exception:
                continue
        return reminders

    def save_reminders(self, reminders: List[Reminder]) -> None:
        raw = [r.model_dump() for r in reminders]
        self._write_raw(raw)

    def add_reminder(self, reminder: Reminder) -> None:
        current = self.load_all_reminders()
        # Avoid duplicate ids
        current = [r for r in current if r.id != reminder.id]
        current.append(reminder)
        self.save_reminders(current)

    def update_reminder(self, reminder: Reminder) -> bool:
        current = self.load_all_reminders()
        found = False
        for i, r in enumerate(current):
            if r.id == reminder.id:
                current[i] = reminder
                found = True
                break
        if found:
            self.save_reminders(current)
        return found

    def toggle_reminder(self, reminder_id: str) -> Optional[bool]:
        current = self.load_all_reminders()
        for r in current:
            if r.id == reminder_id:
                r.enabled = not r.enabled
                self.save_reminders(current)
                return r.enabled
        return None

    def delete_reminder(self, reminder_id: str) -> bool:
        current = self.load_all_reminders()
        initial_len = len(current)
        filtered = [r for r in current if r.id != reminder_id]
        if len(filtered) < initial_len:
            self.save_reminders(filtered)
            return True
        return False

    def clear_all(self) -> None:
        self._write_raw([])
