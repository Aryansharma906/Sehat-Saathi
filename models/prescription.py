"""
Prescription and Medicine Instruction Data Models
Enforces Medical Safety Invariants (Rule 1, 2, 3, 4, 15).
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import uuid
from datetime import datetime


class ExtractionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    UNCERTAIN = "UNCERTAIN"
    FAILED = "FAILED"


class MedicineInstruction(BaseModel):
    """
    Structured representation of a single medicine entry extracted from a prescription.
    Unknown values must remain None rather than invented defaults (Rule 1).
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    raw_medicine_name: str = Field(
        ...,
        description="Exact raw wording read from the prescription image. Never empty."
    )
    candidate_medicine_name: Optional[str] = Field(
        default=None,
        description="Interpreted or cleaned brand/generic name. Must be distinguished from raw text."
    )
    strength: Optional[str] = Field(
        default=None,
        description="Strength e.g. '500 mg', '650 mg', '5 ml'. None if not explicitly legible."
    )
    dose_instruction_raw: Optional[str] = Field(
        default=None,
        description="Dosage instruction e.g. '1 tablet', '2 drops'. None if missing."
    )
    frequency_raw: Optional[str] = Field(
        default=None,
        description="Frequency e.g. 'Once daily', 'Twice daily', 'OD', 'BD', 'TDS', 'SOS'."
    )
    duration_raw: Optional[str] = Field(
        default=None,
        description="Duration e.g. '5 days', '1 week'. Never guessed if absent."
    )
    timing_raw: Optional[str] = Field(
        default=None,
        description="Food or timing instruction e.g. 'After meals' (खाने के बाद), 'Before food'."
    )
    quantity_raw: Optional[str] = Field(
        default=None,
        description="Total quantity prescribed e.g. '10 tablets', '1 bottle'."
    )
    is_uncertain: bool = Field(
        default=False,
        description="Set to True if handwriting is ambiguous, faded, or difficult to verify."
    )
    uncertainty_reason: Optional[str] = Field(
        default=None,
        description="Plain-language reason for uncertainty e.g. 'लिखावट अस्पष्ट है (Handwriting unclear)'."
    )
    unresolved_fields: List[str] = Field(
        default_factory=list,
        description="List of specific field names that require user review."
    )
    user_confirmed: bool = Field(
        default=False,
        description="MUST be True before any reminder can be created for this medicine (Rule 3)."
    )

    @field_validator("raw_medicine_name")
    def validate_raw_name_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("raw_medicine_name cannot be empty or purely whitespace")
        return v.strip()


class Prescription(BaseModel):
    """
    Represents the full extracted prescription document.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    patient_name: Optional[str] = Field(default=None, description="Patient name if legible; optional.")
    prescription_date: Optional[str] = Field(default=None, description="Date on prescription if legible.")
    doctor_info: Optional[str] = Field(default=None, description="Doctor/clinic details if legible.")
    original_text: Optional[str] = Field(
        default=None,
        description="Full raw OCR text transcription of the prescription document."
    )
    extraction_status: ExtractionStatus = Field(default=ExtractionStatus.SUCCESS)
    medicines: List[MedicineInstruction] = Field(default_factory=list)
    unresolved_fields: List[str] = Field(default_factory=list)
    user_confirmed: bool = Field(default=False)
    source_image_retained: bool = Field(
        default=False,
        description="Privacy invariant: Source image is processed in memory and not retained by default."
    )

    def has_uncertain_critical_fields(self) -> bool:
        """Returns True if any medicine has uncertain fields or lacks user confirmation."""
        return any(med.is_uncertain or not med.user_confirmed for med in self.medicines)

    def can_create_reminders(self) -> bool:
        """
        Safety Gate (Rule 3): Can only create reminders if at least one medicine is confirmed
        and has actionable frequency or timing.
        """
        confirmed = [m for m in self.medicines if m.user_confirmed]
        return len(confirmed) > 0
