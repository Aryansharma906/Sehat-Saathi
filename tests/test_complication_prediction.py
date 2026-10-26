"""
Tests for Health Complication Prediction Service (ML & DL Risk Stratification)
Enforces Medical Safety Invariants (Rule 8, 12).
"""

import pytest
from models.complication_prediction import (
    ComplicationPredictionInput,
    ComplicationPredictionResult,
    RiskTier
)
from services.complication_prediction_service import ComplicationPredictionService


def test_normal_vitals_predict_low_risk():
    """Verify that completely normal vitals yield Low Risk tier."""
    inp = ComplicationPredictionInput(
        age=50,
        systolic_bp=120.0,
        diastolic_bp=80.0,
        blood_sugar=95.0,
        spo2=98.0,
        pulse_rate=72.0,
        body_temperature=98.6,
        adherence_percentage=100.0,
        active_medications_count=2,
        recent_adverse_symptoms=[]
    )

    result = ComplicationPredictionService.predict_complication_risk(inp)
    assert isinstance(result, ComplicationPredictionResult)
    assert result.risk_tier == RiskTier.LOW
    assert result.risk_score_percentage < 35.0
    assert result.doctor_escalation_needed is False
    assert result.emergency_dial_advised is False
    assert "⚠️" in result.disclaimer  # Transparency disclaimer present


def test_hypertensive_crisis_predicts_high_risk_and_emergency():
    """Verify that extreme hypertension (185/125) triggers High Risk & Emergency call."""
    inp = ComplicationPredictionInput(
        systolic_bp=185.0,
        diastolic_bp=125.0,
        spo2=97.0
    )

    result = ComplicationPredictionService.predict_complication_risk(inp)
    assert result.risk_tier == RiskTier.HIGH
    assert result.risk_score_percentage >= 70.0
    assert result.doctor_escalation_needed is True
    assert result.emergency_dial_advised is True
    assert any("Hypertensive Crisis" in comp for comp in result.potential_complications_hindi)
    assert any(rf.feature_name == "रक्तचाप (Blood Pressure)" and rf.impact_level == "गंभीर" for rf in result.key_risk_factors)


def test_severe_hypoxia_predicts_high_risk():
    """Verify that SpO2 < 92% triggers critical hypoxia alert."""
    inp = ComplicationPredictionInput(
        spo2=89.0,
        systolic_bp=125.0,
        diastolic_bp=82.0
    )

    result = ComplicationPredictionService.predict_complication_risk(inp)
    assert result.risk_tier == RiskTier.HIGH
    assert result.emergency_dial_advised is True
    assert any("हाइपोक्सिया" in comp for comp in result.potential_complications_hindi)


def test_severe_hyperglycemia_predicts_metabolic_complication():
    """Verify that Blood Sugar >= 250 triggers metabolic DKA risk."""
    inp = ComplicationPredictionInput(
        blood_sugar=290.0,
        systolic_bp=130.0,
        diastolic_bp=85.0,
        spo2=98.0
    )

    result = ComplicationPredictionService.predict_complication_risk(inp)
    assert result.risk_tier == RiskTier.HIGH
    assert any("कीटोएसिडोसिस" in comp for comp in result.potential_complications_hindi)


def test_polypharmacy_and_poor_adherence_risk_factors():
    """Verify that >= 5 medications and poor adherence are captured in risk factors."""
    inp = ComplicationPredictionInput(
        systolic_bp=135.0,
        diastolic_bp=85.0,
        adherence_percentage=45.0,
        active_medications_count=6,
        recent_adverse_symptoms=["सांस लेने में हल्की तकलीफ"]
    )

    result = ComplicationPredictionService.predict_complication_risk(inp)
    factor_names = [rf.feature_name for rf in result.key_risk_factors]
    assert any("Polypharmacy" in name for name in factor_names)
    assert any("Adherence" in name for name in factor_names)
    assert result.doctor_escalation_needed is True


def test_temporal_trajectory_sequence_analysis():
    """Verify temporal trend slope analysis for progressive multi-day vitals."""
    # Steeply rising systolic BP over 4 days
    rising_bp = [130.0, 142.0, 155.0, 168.0]
    trend_res = ComplicationPredictionService.predict_temporal_trajectory(rising_bp)
    
    assert trend_res["early_warning"] is True
    assert trend_res["slope"] > 8.0
    assert "लगातार बढ़ रहा है" in trend_res["trend_direction"]
    assert trend_res["projected_next_day_bp"] is not None

    # Stable BP
    stable_bp = [120.0, 122.0, 119.0, 121.0]
    stable_res = ComplicationPredictionService.predict_temporal_trajectory(stable_bp)
    assert stable_res["early_warning"] is False
    assert "स्थिर" in stable_res["trend_direction"]
