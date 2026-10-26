"""
Progress Tracker & Health Questionnaire Service
Evaluates patient-reported adherence and recovery progress.
Enforces Medical Safety Invariants (Rule 7: Escalation to doctor when recovery is delayed).
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from models.progress_tracker import ProgressCheckIn


DEFAULT_PROGRESS_FILE = Path("data/progress_records.json")


QUESTIONNAIRE_ITEMS = [
    {
        "id": "feeling",
        "question_hindi": "1. दवा शुरू करने के बाद अब आपको कैसा महसूस हो रहा है?",
        "options": [
            "😊 बहुत आराम है (Feeling Much Better)",
            "😐 थोड़ा सुधार है (Slight Improvement)",
            "🙁 कोई सुधार नहीं (No Change)",
            "😣 तबीयत और खराब हुई (Feeling Worse)"
        ]
    },
    {
        "id": "adherence",
        "question_hindi": "2. क्या आपने डॉक्टर के बताए समय पर सभी दवाइयां ली हैं?",
        "options": [
            "✅ हां, सभी खुराक समय पर लीं (All Doses on Time)",
            "⚠️ 1-2 खुराक लेना भूल गए (Missed 1-2 Doses)",
            "❌ दवाइयां ठीक से नहीं ले पाए (Missed Many Doses)"
        ]
    },
    {
        "id": "symptoms",
        "question_hindi": "3. बुखार, दर्द या बीमारी के मुख्य लक्षणों में कितना आराम है?",
        "options": [
            "🟢 लक्षण लगभग खत्म हो चुके हैं (Fully Relieved)",
            "🟡 थोड़ा कम हुआ है, पर अभी बाकी है (Partially Relieved)",
            "🔴 लक्षण वैसे ही बने हुए हैं (No Relief)"
        ]
    }
]


class ProgressTrackerService:
    def __init__(self, filepath: Path = DEFAULT_PROGRESS_FILE):
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

    def evaluate_checkin(
        self,
        feeling: str,
        adherence: str,
        symptoms: str
    ) -> ProgressCheckIn:
        """
        Calculates recovery progress percentage and determines if clinician follow-up is warranted.
        """
        score = 0
        
        # Scoring Feeling
        if "बहुत आराम" in feeling:
            score += 40
        elif "थोड़ा सुधार" in feeling:
            score += 25
        elif "कोई सुधार नहीं" in feeling:
            score += 10
        else:  # Feeling worse
            score += 0

        # Scoring Adherence
        if "समय पर लीं" in adherence:
            score += 30
        elif "1-2 खुराक" in adherence:
            score += 15
        else:
            score += 5

        # Scoring Symptoms
        if "खत्म" in symptoms:
            score += 30
        elif "थोड़ा कम" in symptoms:
            score += 15
        else:
            score += 0

        # Clinical Guidance Logic
        doctor_advised = False
        if score >= 75:
            rec = "🌟 आपका स्वास्थ्य सुधार बहुत अच्छा है! डॉक्टर द्वारा बताया गया पूरा कोर्स समय पर समाप्त करें।"
        elif score >= 45:
            rec = "👍 सुधार हो रहा है। दवाएं बिना भूले समय पर लेते रहें और भरपूर पानी व आराम लें।"
        else:
            doctor_advised = True
            rec = "⚠️ तबीयत में अपेक्षित सुधार नहीं दिख रहा है। कृपया डॉक्टर से संपर्क करें या नजदीकी प्राथमिक स्वास्थ्य केंद्र (PHC) में दिखाएं।"

        checkin = ProgressCheckIn(
            overall_feeling=feeling,
            adherence_status=adherence,
            symptom_relief=symptoms,
            recovery_score=score,
            recommendation_hindi=rec,
            doctor_visit_advised=doctor_advised
        )

        current = self.get_all_checkins()
        current.insert(0, checkin)
        self._write_raw([c.model_dump() for c in current])
        return checkin

    def get_all_checkins(self) -> List[ProgressCheckIn]:
        raw = self._read_raw()
        results = []
        for item in raw:
            try:
                results.append(ProgressCheckIn.model_validate(item))
            except Exception:
                continue
        return results

    @classmethod
    def get_questionnaire_items(cls) -> List[Dict[str, Any]]:
        return QUESTIONNAIRE_ITEMS
