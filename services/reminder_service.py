"""
Reminder and Scheduling Service
Transforms user-confirmed medicine instructions into actionable medication reminders.
Enforces Medical Safety Invariants (Rule 3, 11).
"""

from typing import List, Optional
from datetime import datetime, time
import re
from models.prescription import MedicineInstruction
from models.reminder import Reminder
from storage.persistence import LocalStorageAdapter


DEFAULT_TIME_MORNING = "08:00"
DEFAULT_TIME_AFTERNOON = "13:00"
DEFAULT_TIME_NIGHT = "20:00"


class ReminderService:
    def __init__(self, storage_adapter: Optional[LocalStorageAdapter] = None):
        self.storage = storage_adapter or LocalStorageAdapter()

    @staticmethod
    def schedule_for_frequency(frequency_raw: Optional[str]) -> List[tuple[str, str]]:
        """Return supported default times, refusing ambiguous or as-needed frequencies."""
        frequency = (frequency_raw or "").strip().lower()
        words = set(re.findall(r"[a-z]+", frequency))
        numbers = set(re.findall(r"(?<!\w)[123](?!\w)", frequency))

        if (
            words & {"tds", "tid"}
            or "दिन में 3 बार" in frequency
            or "तीन बार" in frequency
            or ("3" in numbers and words & {"daily", "day", "times"})
            or ("three" in words and words & {"daily", "day", "times"})
        ):
            return [
                ("सुबह (Morning)", DEFAULT_TIME_MORNING),
                ("दोपहर (Afternoon)", DEFAULT_TIME_AFTERNOON),
                ("रात (Night)", DEFAULT_TIME_NIGHT),
            ]
        if (
            words & {"bd", "bid"}
            or "2 बार" in frequency
            or "दो बार" in frequency
            or ("2" in numbers and words & {"daily", "day", "times"})
            or ("twice" in words and words & {"daily", "day"})
        ):
            return [
                ("सुबह (Morning)", DEFAULT_TIME_MORNING),
                ("रात (Night)", DEFAULT_TIME_NIGHT),
            ]
        if (
            "od" in words
            or "दिन में 1 बार" in frequency
            or "एक बार" in frequency
            or ("1" in numbers and words & {"daily", "day", "times"})
            or ("once" in words and words & {"daily", "day"})
        ):
            return [("सुबह (Morning)", DEFAULT_TIME_MORNING)]

        raise ValueError(
            "This frequency does not map to a safe reminder schedule. "
            "Please ask your prescriber or pharmacist to clarify it."
        )

    def create_reminders_from_instruction(
        self,
        medicine: MedicineInstruction,
        custom_times: Optional[List[str]] = None,
        prescription_id: Optional[str] = None,
        prescription_date: Optional[str] = None
    ) -> List[Reminder]:
        """
        Creates reminder objects for a confirmed medicine instruction.
        CRITICAL SAFETY RULE 3: medicine.user_confirmed MUST be True!
        Preserves source prescription association (Accessible Rural Healthcare Requirement 3).
        """
        if not medicine.user_confirmed:
            raise ValueError(
                f"Cannot create reminders for unconfirmed medicine: {medicine.raw_medicine_name}. "
                "User must verify and confirm the instruction first."
            )

        if not medicine.candidate_medicine_name or not medicine.candidate_medicine_name.strip():
            raise ValueError("A confirmed medicine name is required before creating reminders.")
        if not medicine.dose_instruction_raw or not medicine.dose_instruction_raw.strip():
            raise ValueError("A confirmed dose is required before creating reminders.")
        if not medicine.frequency_raw or not medicine.frequency_raw.strip():
            raise ValueError("A confirmed frequency is required before creating reminders.")
        if not medicine.timing_raw or not medicine.timing_raw.strip():
            raise ValueError("A confirmed timing instruction is required before creating reminders.")

        scheduled_times = self.schedule_for_frequency(medicine.frequency_raw)
        name = medicine.candidate_medicine_name or medicine.raw_medicine_name
        dose = medicine.dose_instruction_raw
        food = medicine.timing_raw

        created_reminders = []

        if custom_times is not None:
            if not custom_times:
                raise ValueError("Provide at least one reminder time.")
            if len(set(custom_times)) != len(custom_times):
                raise ValueError("Reminder times must be unique.")
            if len(custom_times) != len(scheduled_times):
                raise ValueError("The number of reminder times must match the confirmed frequency.")
            for t_str in custom_times:
                r = Reminder(
                    medicine_instruction_id=medicine.id,
                    source_prescription_id=prescription_id,
                    source_prescription_date=prescription_date,
                    source_raw_text=medicine.raw_medicine_name,
                    medicine_name=name,
                    dosage=dose,
                    timing_label="समय (Custom Time)",
                    reminder_time=t_str,
                    food_relation=food,
                    user_confirmed=True
                )
                created_reminders.append(r)
        else:
            for label, t_str in scheduled_times:
                r = Reminder(
                    medicine_instruction_id=medicine.id,
                    source_prescription_id=prescription_id,
                    source_prescription_date=prescription_date,
                    source_raw_text=medicine.raw_medicine_name,
                    medicine_name=name,
                    dosage=dose,
                    timing_label=label,
                    reminder_time=t_str,
                    food_relation=food,
                    user_confirmed=True
                )
                created_reminders.append(r)

        # Non-destructive save: appends/merges without wiping existing schedules
        for r in created_reminders:
            self.storage.add_reminder(r)

        return created_reminders

    def check_potential_conflicts(self, medicine: MedicineInstruction) -> List[dict]:
        """
        Requirement 3: Flag conflicting instructions for professional clarification.
        Detects if an active saved reminder exists with a similar name but different dosage.
        """
        conflicts = []
        name_clean = (medicine.candidate_medicine_name or medicine.raw_medicine_name).strip().lower()
        active = [r for r in self.storage.load_all_reminders() if r.enabled]

        for rem in active:
            rem_name_clean = rem.medicine_name.strip().lower()
            if name_clean in rem_name_clean or rem_name_clean in name_clean:
                # Same medicine name, check if dosage or timing differs
                if medicine.dose_instruction_raw and rem.dosage and medicine.dose_instruction_raw.strip() != rem.dosage.strip():
                    conflicts.append({
                        "existing_reminder_id": rem.id,
                        "medicine_name": rem.medicine_name,
                        "existing_dosage": rem.dosage,
                        "new_dosage": medicine.dose_instruction_raw,
                        "reason": f"पहले से सहेजी गई खुराक '{rem.dosage}' है, जबकि नए पर्चे में '{medicine.dose_instruction_raw}' लिखी है।"
                    })
        return conflicts

    def get_all_reminders(self, current_dt: Optional[datetime] = None) -> List[Reminder]:
        """Load reminders and clear yesterday's taken state without assuming a dose was taken today."""
        now = current_dt or datetime.now()
        today = now.date().isoformat()
        reminders = self.storage.load_all_reminders()
        for reminder in reminders:
            changed = False
            if reminder.taken_today and reminder.taken_date is None:
                # Existing records predate taken_date. Preserve their current-day state once,
                # then future days can reset it safely.
                reminder.taken_date = today
                changed = True
            elif reminder.taken_today and reminder.taken_date != today:
                reminder.taken_today = False
                reminder.taken_date = None
                changed = True
            elif not reminder.taken_today and reminder.taken_date is not None:
                reminder.taken_date = None
                changed = True
            if changed:
                self.storage.update_reminder(reminder)
        return reminders

    def toggle_reminder(self, reminder_id: str) -> Optional[bool]:
        return self.storage.toggle_reminder(reminder_id)

    def delete_reminder(self, reminder_id: str) -> bool:
        return self.storage.delete_reminder(reminder_id)

    def delete_all_reminders(self) -> None:
        """Discards all saved reminder schedules."""
        self.storage.clear_all()

    def discard_inactive_reminders(self) -> int:
        """
        Discards only inactive/disabled reminder schedules, preserving active schedules.
        Returns the count of discarded schedules.
        """
        current = self.storage.load_all_reminders()
        active = [r for r in current if r.enabled]
        discarded_count = len(current) - len(active)
        self.storage.save_reminders(active)
        return discarded_count

    def mark_as_taken(self, reminder_id: str, taken: bool = True) -> bool:
        """
        Rule 11: Marks medicine as taken strictly on explicit user action.
        """
        reminders = self.storage.load_all_reminders()
        for r in reminders:
            if r.id == reminder_id:
                r.taken_today = taken
                r.taken_date = datetime.now().date().isoformat() if taken else None
                return self.storage.update_reminder(r)
        return False

    def is_due_now(self, reminder: Reminder, current_dt: Optional[datetime] = None) -> bool:
        """
        Determines if a reminder is due within a +/- 60-minute window of current time.
        """
        now = current_dt or datetime.now()
        try:
            parts = reminder.reminder_time.split(":")
            rem_time = time(int(parts[0]), int(parts[1]))
            # Compare minutes from midnight
            now_minutes = now.hour * 60 + now.minute
            rem_minutes = rem_time.hour * 60 + rem_time.minute
            raw_diff = abs(now_minutes - rem_minutes)
            diff = min(raw_diff, 24 * 60 - raw_diff)
            is_marked_taken_today = reminder.taken_today and reminder.taken_date in {
                None, now.date().isoformat()
            }
            return reminder.enabled and diff <= 60 and not is_marked_taken_today
        except Exception:
            return False
