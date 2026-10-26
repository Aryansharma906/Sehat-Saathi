"""
Mental Health Screening and Health Device Vitals Data Models
Supports observational mental wellness (Tele-MANAS aligned) and standardized health device data collection.
Enforces Medical Safety Invariants (Rule 8: Observational screening only, not psychiatric certification).
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid
from datetime import datetime


class MentalHealthCheckIn(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %I:%M %p"))
    sleep_quality: str = Field(..., description="अच्छी नींद / कभी-कभी परेशानी / बहुत कम नींद")
    stress_level: str = Field(..., description="सामान्य / हल्का तनाव / बहुत अधिक चिंता")
    mood_status: str = Field(..., description="प्रसन्न / सामान्य / उदास या अकेलापन")
    wellness_score: int = Field(default=50, ge=0, le=100)
    supportive_advice_hindi: str
    tele_manas_recommended: bool = Field(default=False, description="True if severe distress; prompts Tele-MANAS 14416 call")


class DeviceVitalsReading(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %I:%M %p"))
    device_type: str = Field(..., description="BP Monitor / Pulse Oximeter / Glucometer / Thermometer")
    metric_name: str = Field(..., description="Blood Pressure / SpO2 / Pulse / Blood Sugar / Temperature")
    value: str = Field(..., description="Recorded reading e.g. '120/80', '98', '110', '98.6'")
    unit: str = Field(..., description="mmHg, %, bpm, mg/dL, °F")
    sync_source: str = Field(default="Manual / Device Export", description="Connection protocol or import source")
    status_flag: str = Field(default="सामान्य (Normal)", description="Normal / Warning / Critical")
    alert_message: Optional[str] = None
