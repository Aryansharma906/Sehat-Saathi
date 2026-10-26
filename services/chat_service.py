"""
Constrained Prescription Q&A Assistant
Enforces Medical Safety Invariants (Rule 8, 9, 10).
"""

import os
from typing import Optional
from models.prescription import Prescription


EMERGENCY_KEYWORDS = ["सीने में दर्द", "chest pain", "सांस फूलना", "difficulty breathing", "बेहोश", "unconscious", "खून", "bleeding"]

SAFE_SYSTEM_PROMPT = """
You are 'सेहत साथी (Sehat Saathi) सहायक', an accessible and humble medication companion assistant for patients in rural India.

CRITICAL MEDICAL SAFETY BOUNDARIES:
1. You can ONLY answer questions directly related to the user's confirmed prescription instructions and general educational facts about the listed medicines.
2. DO NOT DIAGNOSE ANY DISEASE OR SYMPTOMS. If a user asks "Do I have cancer/typhoid?" or describes symptoms, reply politely that you cannot diagnose illnesses and they must visit a doctor or nearby Primary Health Centre (PHC).
3. DO NOT RECOMMEND DOSAGE CHANGES OR STOPPING/STARTING DRUGS. If a user asks if they can take more or stop, say only the doctor or pharmacist can advise this.
4. If emergency symptoms (chest pain, severe bleeding, difficulty breathing) are mentioned, provide an urgent advisory to call 108/112 or visit the nearest emergency facility immediately.
5. Always keep responses short, respectful, and in simple Hindi with easy words.
"""


class PrescriptionChatService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def ask_question(self, user_question: str, confirmed_prescription: Optional[Prescription] = None) -> str:
        q_lower = user_question.lower()

        # 1. Emergency safety tripwire
        for kw in EMERGENCY_KEYWORDS:
            if kw in q_lower:
                return (
                    "🚨 **आपातकालीन सूचना:** यह लक्षण गंभीर हो सकते हैं। "
                    "कृपया तुरंत अपने नजदीकी अस्पताल जाएं या 108 / 112 एम्बुलेंस सेवा पर संपर्क करें। "
                    "इस ऐप पर निर्भर न रहें।"
                )

        # 2. Symptom / diagnosis tripwire
        if any(term in q_lower for term in ["मुझे क्या बीमारी है", "क्या मुझे", "क्या रोग है", "diagnose", "what illness", "लक्षण"]):
            return (
                "⚠️ **क्षमा करें:** सेहत साथी किसी बीमारी की जांच या निदान (diagnosis) नहीं कर सकता। "
                "कृपया अपनी जांच के लिए डॉक्टर या नजदीकी स्वास्थ्य केंद्र (PHC) से संपर्क करें।"
            )

        # 3. Contextual answer using Gemini or rule-based fallback
        context_str = "कोई सक्रिय पर्ची उपलब्ध नहीं है।"
        if confirmed_prescription and confirmed_prescription.medicines:
            med_summaries = []
            for m in confirmed_prescription.medicines:
                name = m.candidate_medicine_name or m.raw_medicine_name
                med_summaries.append(f"- {name}: {m.dose_instruction_raw or ''}, {m.frequency_raw or ''}, {m.timing_raw or ''}")
            context_str = "मरीज की पुष्टि की गई दवाइयां:\n" + "\n".join(med_summaries)

        if not self.client:
            # Rule-based fallback when offline or without API key
            return (
                f"ℹ️ आपकी पर्ची में यह दवाएं शामिल हैं:\n{context_str}\n\n"
                "दवा लेने के सही समय या किसी भी बदलाव के लिए कृपया अपने नजदीकी फार्मासिस्ट या डॉक्टर से परामर्श लें।"
            )

        try:
            prompt = (
                f"{SAFE_SYSTEM_PROMPT}\n\n"
                f"[PRESCRIPTION CONTEXT]\n{context_str}\n\n"
                f"[USER QUESTION]\n{user_question}\n\n"
                "उत्तर सरल हिंदी में दें:"
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text or "क्षमा करें, उत्तर प्राप्त नहीं हो सका।"
        except Exception as e:
            return f"संपर्क में समस्या आई। कृपया डॉक्टर या फार्मासिस्ट से परामर्श लें। ({str(e)})"
