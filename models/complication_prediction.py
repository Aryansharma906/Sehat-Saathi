"""
Data Models for Health Complication Prediction (ML & DL Risk Stratification)
Enforces Medical Safety Invariants (Rule 8, 12: Risk prediction, not clinical diagnosis).
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
import uuid
from datetime import datetime


class RiskTier(str, Enum):
    LOW = "कम जोखिम (Low Risk)"
    MODERATE = "मध्यम जोखिम (Moderate Risk)"
    HIGH = "उच्च जोखिम (High / Critical Alert)"


class ComplicationPredictionInput(BaseModel):
    """
    Input feature vector for ML/DL health complication risk prediction.
    """
    age: Optional[int] = Field(default=55, ge=1, le=120, description="Patient age in years")
    systolic_bp: Optional[float] = Field(default=None, description="Systolic blood pressure (mmHg)")
    diastolic_bp: Optional[float] = Field(default=None, description="Diastolic blood pressure (mmHg)")
    blood_sugar: Optional[float] = Field(default=None, description="Blood glucose (mg/dL)")
    spo2: Optional[float] = Field(default=None, description="Oxygen saturation %")
    pulse_rate: Optional[float] = Field(default=None, description="Heart/Pulse rate (bpm)")
    body_temperature: Optional[float] = Field(default=None, description="Body temperature (°F)")
    adherence_percentage: float = Field(default=100.0, ge=0.0, le=100.0, description="Medication adherence %")
    active_medications_count: int = Field(default=1, ge=0, description="Number of concurrent medicines prescribed")
    recent_adverse_symptoms: List[str] = Field(default_factory=list, description="Adverse reactions or symptoms reported")


class ComplicationRiskFactor(BaseModel):
    """
    Explains an individual driving factor behind the complication risk.
    """
    feature_name: str
    observed_value: str
    impact_level: str  # "सामान्य", "चिंताजनक", "गंभीर"
    explanation_hindi: str


class ComplicationPredictionResult(BaseModel):
    """
    Prediction output from ML/DL risk stratification models.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %I:%M %p"))
    risk_score_percentage: float = Field(..., ge=0.0, le=100.0, description="Predicted complication risk score (0-100%)")
    risk_tier: RiskTier
    potential_complications_hindi: List[str] = Field(default_factory=list, description="List of possible complications identified")
    key_risk_factors: List[ComplicationRiskFactor] = Field(default_factory=list, description="Explainable feature contributions")
    clinical_guidance_hindi: str = Field(..., description="Actionable safety guidance in plain Hindi")
    doctor_escalation_needed: bool = Field(default=False)
    emergency_dial_advised: bool = Field(default=False)
    model_name: str = Field(default="SehatSaathi-ClinicalRisk-RF/v1.0")
    disclaimer: str = Field(
        default="⚠️ यह एमएल मॉडल द्वारा सांख्यिकीय जोखिम मूल्यांकन है, डॉक्टर का क्लिनिकल डायग्नोसिस नहीं। किसी भी लक्षण में तुरंत डॉक्टर से संपर्क करें।"
    )
