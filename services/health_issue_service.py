"""
Treatment Health Issue Recording & Doctor Notification Service
Enforces Medical Safety Invariants (Rule 7: Escalation to prescribing clinician).
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import urllib.parse
from models.health_issue import TreatmentIssueLog


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ISSUES_FILE = PROJECT_ROOT / "data" / "treatment_issues.json"

COMMON_ISSUE_TYPES = [
    "त्वचा पर लाल चकत्ते / खुजली (Skin Rash / Itching)",
    "उल्टी या जी मिचलाना (Nausea / Vomiting)",
    "पेट में तेज दर्द या जलन (Stomach Ache / Acidity)",
    "चक्कर आना या कमजोरी (Dizziness / Weakness)",
    "सांस लेने में तकलीफ या घबराहट (Breathing Difficulty)",
    "चेहरे या होंठों पर सूजन (Facial Swelling / Allergy)",
    "दस्त या पेट खराब (Diarrhea)",
    "अन्य परेशानी (Other Discomfort)"
]

SEVERE_SYMPTOM_KEYWORDS = [
    "सांस", "सूजन", "breathing", "swelling", "allergy", "गंभीर", "घबराहट", "severe", "chest pain", "सीने में दर्द"
]


class HealthIssueService:
    def __init__(self, filepath: Path = DEFAULT_ISSUES_FILE):
        self.filepath = Path(filepath)
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        if not self.filepath.exists():
            self._write_raw([])

    def _read_raw(self) -> List[dict]:
        try:
            if not self.filepath.exists():
                return []
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except Exception:
            return []

    def _write_raw(self, data: List[dict]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def log_issue(
        self,
        medicine_name: str,
        issue_type: str,
        severity: str = "सामान्य (Mild)",
        notes: Optional[str] = None
    ) -> TreatmentIssueLog:
        """
        Records an adverse symptom or health issue occurring during treatment.
        """
        is_severe = False
        lower_issue = (issue_type + " " + (notes or "") + " " + severity).lower()
        if any(kw in lower_issue for kw in SEVERE_SYMPTOM_KEYWORDS) or "गंभीर" in severity or "severe" in severity.lower():
            is_severe = True

        log_entry = TreatmentIssueLog(
            medicine_name=medicine_name,
            issue_type=issue_type,
            severity=severity,
            notes=notes,
            is_severe_alert=is_severe
        )

        current = self.get_all_issues()
        current.insert(0, log_entry)  # Newest first
        self._write_raw([e.model_dump() for e in current])
        return log_entry

    def get_all_issues(self) -> List[TreatmentIssueLog]:
        raw = self._read_raw()
        results = []
        for item in raw:
            try:
                results.append(TreatmentIssueLog.model_validate(item))
            except Exception:
                continue
        return results

    def clear_issues(self) -> None:
        self._write_raw([])

    def delete_issue(self, issue_id: str) -> bool:
        """Discards a single logged health issue record."""
        current = self.get_all_issues()
        initial_len = len(current)
        filtered = [item for item in current if item.id != issue_id]
        if len(filtered) < initial_len:
            self._write_raw([e.model_dump() for e in filtered])
            return True
        return False

    @classmethod
    def generate_doctor_notification_text(
        cls,
        issue: TreatmentIssueLog,
        patient_name: Optional[str] = None
    ) -> str:
        """
        Formats a professional Hindi notification for the doctor or chemist.
        """
        p_name = patient_name or "मरीज"
        urgent_flag = "🚨 [अति-आवश्यक सूचना / Urgent]" if issue.is_severe_alert else "📋 [इलाज के दौरान परेशानी की सूचना]"
        
        lines = [
            f"{urgent_flag}",
            f"आदरणीय डॉक्टर साहब / केमिस्ट भैया,",
            f"मरीज '{p_name}' को दवा लेने के दौरान यह परेशानी हुई है:",
            f"• दवा का नाम: {issue.medicine_name}",
            f"• हुई समस्या: {issue.issue_type}",
            f"• गंभीरता: {issue.severity}",
            f"• समय: {issue.timestamp}"
        ]
        if issue.notes:
            lines.append(f"• मरीज का विवरण: {issue.notes}")

        lines.append("\nकृपया सलाह दें कि क्या यह दवा जारी रखनी है या खुराक बदलनी है?")
        return "\n".join(lines)

    @classmethod
    def generate_whatsapp_share_url(
        cls,
        issue: TreatmentIssueLog,
        patient_name: Optional[str] = None,
        doctor_phone: Optional[str] = None
    ) -> str:
        """
        Generates a direct WhatsApp link to send the issue report to the doctor.
        """
        message = cls.generate_doctor_notification_text(issue, patient_name)
        encoded_msg = urllib.parse.quote(message)
        if doctor_phone and doctor_phone.strip():
            clean_phone = doctor_phone.strip().replace("+", "").replace("-", "").replace(" ", "")
            return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
        return f"https://api.whatsapp.com/send?text={encoded_msg}"
