"""
Medication Reminder Data Models
Enforces Medical Safety Invariants (Rule 3, 11).
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
from datetime import datetime, time


class Reminder(BaseModel):
    """
    A single reminder trigger for a confirmed medication.
    Must ONLY be created from a confirmed MedicineInstruction (Rule 3).
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    medicine_instruction_id: str = Field(..., description="Foreign key linking to confirmed MedicineInstruction")
    medicine_name: str = Field(..., description="Confirmed medicine name")
    dosage: Optional[str] = Field(default=None, description="Confirmed dosage (e.g. '1 गोली (1 tablet)')")
    timing_label: str = Field(
        default="सुबह (Morning)",
        description="Human readable time period e.g. 'सुबह (Morning)', 'दोपहर (Afternoon)', 'रात (Night)'"
    )
    reminder_time: str = Field(
        ...,
        description="24-hour format string 'HH:MM' (e.g. '08:00', '14:00', '20:30')"
    )
    food_relation: Optional[str] = Field(
        default="खाने के बाद (After Food)",
        description="Relation to food intake"
    )
    enabled: bool = Field(default=True, description="Active toggle status")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_confirmed: bool = Field(
        default=True,
        description="Safety invariant: Reminders must be explicitly confirmed by user."
    )
    taken_today: bool = Field(
        default=False,
        description="Rule 11: Indicates user tapped 'Mark as Taken', never assumed automatically."
    )

    @field_validator("reminder_time")
    def validate_time_format(cls, v: str) -> str:
        parts = v.strip().split(":")
        if len(parts) != 2:
            raise ValueError("reminder_time must be in 'HH:MM' format")
        h, m = int(parts[0]), int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError(f"Invalid time values: {h}:{m}")
        return f"{h:02d}:{m:02d}"


class ReminderSchedule(BaseModel):
    """
    Collection of reminders for a user/prescription.
    """
    prescription_id: Optional[str] = None
    reminders: List[Reminder] = Field(default_factory=list)
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

    def get_active_reminders(self) -> List[Reminder]:
        return [r for r in self.reminders if r.enabled]
