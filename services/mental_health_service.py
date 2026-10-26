"""
Mental Health Evaluation & Monitoring Service
Alignd with Government of India National Tele Mental Health Programme (Tele-MANAS).
Enforces Medical Safety Invariants (Rule 8: Supportive screening only, not clinical psychiatric diagnosis).
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from models.vitals_and_mental_health import MentalHealthCheckIn


DEFAULT_MENTAL_HEALTH_FILE = Path("data/mental_health_records.json")

TELE_MANAS_HELPLINE = "14416"
TELE_MANAS_TOLLFREE = "1800-891-4416"


class MentalHealthService:
    def __init__(self, filepath: Path = DEFAULT_MENTAL_HEALTH_FILE):
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

    def evaluate_mental_wellness(
        self,
        sleep: str,
        stress: str,
        mood: str
    ) -> MentalHealthCheckIn:
        """
        Evaluates observational mental wellness and provides compassionate guidance.
        """
        score = 0
        
        # Sleep
        if "अच्छी नींद" in sleep:
            score += 35
        elif "कभी-कभी परेशानी" in sleep:
            score += 20
        else:
            score += 5

        # Stress
        if "सामान्य" in stress:
            score += 35
        elif "हल्का तनाव" in stress:
            score += 20
        else:
            score += 5

        # Mood
        if "प्रसन्न" in mood:
            score += 30
        elif "सामान्य" in mood:
            score += 20
        else:
            score += 5

        tele_manas = False
        if score >= 75:
            advice = "🌸 आपका मानसिक संतुलन बहुत अच्छा है। नियमित दिनचर्या, सुबह की धूप और परिवार से बातचीत जारी रखें।"
        elif score >= 45:
            advice = "🌿 हल्का तनाव स्वाभाविक है। गहरी सांस लेने का अभ्यास करें, चाय/कैफीन कम करें और किसी अपने से मन की बात साझा करें।"
        else:
            tele_manas = True
            advice = "🕊️ यदि आप लंबे समय से अत्यधिक चिंता, उदासी या नींद की कमी महसूस कर रहे हैं, तो संकोच न करें। सहायता हमेशा उपलब्ध है।"

        checkin = MentalHealthCheckIn(
            sleep_quality=sleep,
            stress_level=stress,
            mood_status=mood,
            wellness_score=score,
            supportive_advice_hindi=advice,
            tele_manas_recommended=tele_manas
        )

        current = self.get_all_checkins()
        current.insert(0, checkin)
        self._write_raw([c.model_dump() for c in current])
        return checkin

    def get_all_checkins(self) -> List[MentalHealthCheckIn]:
        raw = self._read_raw()
        results = []
        for item in raw:
            try:
                results.append(MentalHealthCheckIn.model_validate(item))
            except Exception:
                continue
        return results
