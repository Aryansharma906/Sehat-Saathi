"""
Patient Progress & Health Questionnaire Data Models
Observational treatment tracking and patient-reported outcome measures.
Enforces Medical Safety Invariants (Rule 8: Observational tracking, no automated diagnosis).
"""

from typing import Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class ProgressCheckIn(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %I:%M %p"))
    overall_feeling: str = Field(..., description="बहुत आराम है / थोड़ा आराम है / कोई सुधार नहीं / तबीयत खराब हुई")
    adherence_status: str = Field(..., description="नियमित दवा ली / कुछ खुराक छूटी / दवा नहीं ले पाए")
    symptom_relief: str = Field(..., description="पूरी तरह ठीक / हल्का सुधार / कोई फर्क नहीं")
    recovery_score: int = Field(default=50, ge=0, le=100, description="Estimated recovery progress percentage 0-100")
    recommendation_hindi: str = Field(default="दवा का कोर्स जारी रखें।", description="Simple guidance based on response")
    doctor_visit_advised: bool = Field(default=False, description="True if no improvement after several days")
