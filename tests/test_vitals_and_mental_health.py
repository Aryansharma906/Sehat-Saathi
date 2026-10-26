"""
Unit Tests for Mental Health Evaluation and Device Vitals Data Compatibility
"""

import pytest
import tempfile
from pathlib import Path
from services.mental_health_service import MentalHealthService
from services.device_data_service import DeviceDataService


@pytest.fixture
def temp_mental_service():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        path = Path(tf.name)
    service = MentalHealthService(filepath=path)
    yield service
    if path.exists():
        path.unlink()


@pytest.fixture
def temp_device_service():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        path = Path(tf.name)
    service = DeviceDataService(filepath=path)
    yield service
    if path.exists():
        path.unlink()


def test_mental_health_wellness_good(temp_mental_service):
    res = temp_mental_service.evaluate_mental_wellness(
        sleep="अच्छी नींद",
        stress="सामान्य",
        mood="प्रसन्न"
    )
    assert res.wellness_score == 100
    assert res.tele_manas_recommended is False
    assert "मानसिक संतुलन बहुत अच्छा है" in res.supportive_advice_hindi


def test_mental_health_severe_distress_triggers_tele_manas(temp_mental_service):
    res = temp_mental_service.evaluate_mental_wellness(
        sleep="बहुत कम नींद",
        stress="बहुत अधिक चिंता",
        mood="उदास या अकेलापन"
    )
    assert res.wellness_score <= 15
    assert res.tele_manas_recommended is True


def test_device_oximeter_critical_alert(temp_device_service):
    reading = temp_device_service.record_reading(
        device_type="पल्स ऑक्सीमीटर (Pulse Oximeter)",
        metric_name="ऑक्सीजन (SpO2)",
        value="88%",
        unit="%"
    )
    assert "Critical Alert" in reading.status_flag
    assert "92% से कम है" in reading.alert_message


def test_device_bp_monitor_high_alert(temp_device_service):
    reading = temp_device_service.record_reading(
        device_type="डिजिटल बीपी मॉनिटर (BP Monitor)",
        metric_name="रक्तचाप (Blood Pressure)",
        value="155/95",
        unit="mmHg"
    )
    assert "High BP" in reading.status_flag
    assert "सामान्य (120/80) से अधिक है" in reading.alert_message


def test_device_json_import_compatibility(temp_device_service):
    json_export = """
    [
        {"device_type": "Smart Oximeter", "metric_name": "SpO2", "value": "97", "unit": "%"},
        {"device_type": "Digital Glucometer", "metric_name": "Blood Sugar (Fasting)", "value": "110", "unit": "mg/dL"}
    ]
    """
    imported = temp_device_service.import_device_json_data(json_export)
    assert len(imported) == 2
    assert imported[0].value == "97"
    assert imported[1].value == "110"
