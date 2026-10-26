"""
Treatment Health Issue and Adverse Reaction Data Models
Allows patients and caregivers to log side effects or discomforts during treatment.
Enforces Medical Safety Invariants (Rule 7: Escalation to clinician).
"""

from typing import Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class TreatmentIssueLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %I:%M %p"))
    medicine_name: str = Field(..., description="Name of the medicine associated with the issue")
    issue_type: str = Field(..., description="Type of health problem or adverse symptom")
    severity: str = Field(default="सामान्य (Mild)", description="Mild, Moderate, or Severe")
    notes: Optional[str] = Field(default=None, description="Additional notes or description")
    is_severe_alert: bool = Field(default=False, description="True if symptom requires immediate hospital visit")
