"""
Language & Explanation Service
Explains prescriptions in simple Hindi and generates voice audio (TTS).
Enforces Medical Safety Invariants (Rule 4, 5, 6, 8, 9).
"""

from abc import ABC, abstractmethod
import io
import os
from typing import Optional, List
from models.prescription import Prescription, MedicineInstruction
from services.medicine_reference import MedicineReferenceService


class BaseLanguageService(ABC):
    @abstractmethod
    def explain_medicine(self, medicine: MedicineInstruction) -> str:
        pass

    @abstractmethod
    def explain_prescription_summary(self, prescription: Prescription) -> str:
        pass

    @abstractmethod
    def generate_speech_audio(self, text_hindi: str) -> Optional[bytes]:
        pass


class SimpleHindiLanguageService(BaseLanguageService):
    """
    Generates plain-language Hindi explanations and audio for low-literacy users.
    """

    def explain_medicine(self, medicine: MedicineInstruction) -> str:
        """
        Creates a clear, respectful, jargon-free Hindi explanation of a confirmed medicine instruction.
        """
        name = medicine.candidate_medicine_name or medicine.raw_medicine_name
        dose = medicine.dose_instruction_raw or "डॉक्टर द्वारा बताई गई मात्रा"
        freq = medicine.frequency_raw or "पर्चे के अनुसार"
        timing = medicine.timing_raw or "खाने के बाद या डॉक्टर के निर्देशानुसार"
        duration = f"{medicine.duration_raw} तक" if medicine.duration_raw else "जितने दिन डॉक्टर ने कहा है"

        # Look up supporting reference information
        ref = MedicineReferenceService.lookup_medicine(name)
        ref_explanation = ""
        if ref:
            ref_explanation = f"\n\nℹ️ **सामान्य जानकारी (General Reference):** {ref['purpose_hindi']}\n⚠️ **सावधानी:** {ref['standard_cautions_hindi']}"

        explanation = (
            f"💊 **दवा का नाम:** {name}\n"
            f"🔹 **कितनी लेनी है:** {dose}\n"
            f"🕒 **कब लेनी है:** {freq} ({timing})\n"
            f"📅 **कितने दिन:** {duration}"
            f"{ref_explanation}"
        )
        return explanation

    def explain_prescription_summary(self, prescription: Prescription) -> str:
        """
        Summary explanation for all confirmed medications on the prescription.
        """
        if not prescription.medicines:
            return "इस पर्ची में कोई दवा नहीं मिली।"

        lines = [
            f"नमस्ते। आपके पर्चे में कुल {len(prescription.medicines)} दवाएं लिखी हैं:\n"
        ]

        for i, med in enumerate(prescription.medicines, 1):
            name = med.candidate_medicine_name or med.raw_medicine_name
            timing = med.timing_raw or "निर्देशानुसार"
            freq = med.frequency_raw or "नियमित"
            lines.append(f"{i}. **{name}** — {freq}, {timing}")

        lines.append(
            "\n⚠️ **महत्वपूर्ण सूचना:** यह केवल आपके समझने के लिए सरल सारांश है। "
            "कृपया किसी भी संदेह की स्थिति में अपने डॉक्टर या फार्मासिस्ट से संपर्क करें।"
        )
        return "\n".join(lines)

    def generate_speech_audio(self, text_hindi: str) -> Optional[bytes]:
        """
        Generates spoken Hindi audio using gTTS (Google Text-to-Speech).
        Fails safely if offline or error occurs.
        """
        if not text_hindi or not text_hindi.strip():
            return None

        # Clean markdown formatting before sending to TTS
        clean_text = (
            text_hindi.replace("**", "")
            .replace("💊", "दवा ")
            .replace("🕒", "समय ")
            .replace("📅", "दिन ")
            .replace("⚠️", "चेतावनी ")
            .replace("ℹ️", "जानकारी ")
            .replace("#", "")
            .replace("🔹", "")
        )

        try:
            from gtts import gTTS
            tts = gTTS(text=clean_text, lang="hi", slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception:
            # Graceful fallback: speech synthesis failure does not break the UI
            return None
