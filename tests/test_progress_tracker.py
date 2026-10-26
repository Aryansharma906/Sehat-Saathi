"""
Unit Tests for Progress Tracker & Treatment Questionnaire Service
"""

import pytest
import tempfile
from pathlib import Path
from services.progress_tracker_service import ProgressTrackerService


@pytest.fixture
def temp_tracker_service():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        path = Path(tf.name)
    service = ProgressTrackerService(filepath=path)
    yield service
    if path.exists():
        path.unlink()


def test_high_recovery_progress_checkin(temp_tracker_service):
    checkin = temp_tracker_service.evaluate_checkin(
        feeling="😊 बहुत आराम है (Feeling Much Better)",
        adherence="✅ हां, सभी खुराक समय पर लीं (All Doses on Time)",
        symptoms="🟢 लक्षण लगभग खत्म हो चुके हैं (Fully Relieved)"
    )
    assert checkin.recovery_score == 100
    assert checkin.doctor_visit_advised is False
    assert "स्वास्थ्य सुधार बहुत अच्छा है" in checkin.recommendation_hindi
    assert len(temp_tracker_service.get_all_checkins()) == 1


def test_low_recovery_triggers_doctor_advice(temp_tracker_service):
    checkin = temp_tracker_service.evaluate_checkin(
        feeling="😣 तबीयत और खराब हुई (Feeling Worse)",
        adherence="❌ दवाइयां ठीक से नहीं ले पाए (Missed Many Doses)",
        symptoms="🔴 लक्षण वैसे ही बने हुए हैं (No Relief)"
    )
    assert checkin.recovery_score <= 15
    assert checkin.doctor_visit_advised is True
    assert "डॉक्टर से संपर्क करें" in checkin.recommendation_hindi


def test_questionnaire_items_structure():
    items = ProgressTrackerService.get_questionnaire_items()
    assert len(items) == 3
    for it in items:
        assert "id" in it
        assert "question_hindi" in it
        assert len(it["options"]) >= 3
