"""
Unit Tests for Health Issue Logging and Doctor Notification Service
"""

import pytest
import tempfile
from pathlib import Path
from services.health_issue_service import HealthIssueService


@pytest.fixture
def temp_issue_service():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        path = Path(tf.name)
    service = HealthIssueService(filepath=path)
    yield service
    if path.exists():
        path.unlink()


def test_log_mild_issue(temp_issue_service):
    issue = temp_issue_service.log_issue(
        medicine_name="Tab Dolo 650",
        issue_type="उल्टी या जी मिचलाना (Nausea / Vomiting)",
        severity="सामान्य (Mild)"
    )
    assert issue.medicine_name == "Tab Dolo 650"
    assert issue.is_severe_alert is False
    assert len(temp_issue_service.get_all_issues()) == 1


def test_log_severe_issue_triggers_alert(temp_issue_service):
    # Severe symptom: Breathing difficulty
    issue = temp_issue_service.log_issue(
        medicine_name="Cap Augmentin 625",
        issue_type="सांस लेने में तकलीफ या घबराहट (Breathing Difficulty)",
        severity="गंभीर (Severe)"
    )
    assert issue.is_severe_alert is True


def test_generate_doctor_notification_and_whatsapp_url():
    service = HealthIssueService()
    issue = service.log_issue(
        medicine_name="Pan-D",
        issue_type="त्वचा पर लाल चकत्ते / खुजली",
        notes="दवा लेने के 1 घंटे बाद हाथ पर चकत्ते दिखे"
    )

    msg = HealthIssueService.generate_doctor_notification_text(issue, patient_name="रमेश कुमार")
    assert "रमेश कुमार" in msg
    assert "Pan-D" in msg
    assert "त्वचा पर लाल चकत्ते" in msg

    url = HealthIssueService.generate_whatsapp_share_url(issue, patient_name="रमेश कुमार", doctor_phone="9876543210")
    assert "https://api.whatsapp.com/send?phone=9876543210&text=" in url
