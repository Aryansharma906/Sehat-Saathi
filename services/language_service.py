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
    Generates plain-language Hindi explanations and audio for low-literacy users,
    grounded in Indian National List of Essential Medicines (NLEM) & Jan Aushadhi standards.
    """

    def explain_medicine(self, medicine: MedicineInstruction, lang: str = "hi") -> str:
        """
        Creates a clear, respectful, jargon-free explanation of a confirmed medicine instruction in Hindi, English, or Hinglish.
        """
        name = medicine.candidate_medicine_name or medicine.raw_medicine_name
        dose = medicine.dose_instruction_raw or ("Doctor prescribed dose" if lang == "en" else "डॉक्टर द्वारा बताई गई मात्रा")
        freq = medicine.frequency_raw or ("As prescribed" if lang == "en" else "पर्चे के अनुसार")
        timing = medicine.timing_raw or ("After meals or as directed" if lang == "en" else "खाने के बाद या डॉक्टर के निर्देशानुसार")
        duration = f"{medicine.duration_raw}" if medicine.duration_raw else ("As long as prescribed" if lang == "en" else "जितने दिन डॉक्टर ने कहा है")

        # Look up supporting reference information from Indian Healthcare Database
        ref = MedicineReferenceService.lookup_medicine(name)
        ref_explanation = ""
        if ref:
            generic_name = ref.get("generic_name", name)
            nlem_badge = "✅ **राष्ट्रीय आवश्यक दवा (NLEM Essential)**" if ref.get("nlem_listed") else ""
            jan_badge = "💡 **जन औषधि केंद्र पर उपलब्ध (Affordable Generic)**" if ref.get("jan_aushadhi_available") else ""
            
            if lang == "en":
                ref_explanation = (
                    f"\n\n---"
                    f"\n🏛️ **सामान्य जानकारी (General Reference):** [India NLEM & Jan Aushadhi Catalog]"
                    f"\n🔹 **मूल जेनेरिक दवा (Active Salt):** {generic_name}"
                    f"\n🔹 **उपयोग (Purpose):** {ref.get('purpose_hindi', 'Therapeutic indication')}"
                    f"\n⚠️ **जरूरी सावधानी (Caution):** {ref.get('standard_cautions_hindi', 'Consult your doctor')}"
                )
            elif lang == "hinglish":
                ref_explanation = (
                    f"\n\n---"
                    f"\n🏛️ **सामान्य जानकारी (General Reference):** [India NLEM & Jan Aushadhi Catalog]"
                    f"\n🔹 **मूल जेनेरिक दवा (Active Salt):** {generic_name}"
                    f"\n🔹 **उपयोग (Purpose):** {ref['purpose_hindi']}"
                    f"\n⚠️ **जरूरी सावधानी (Caution):** {ref['standard_cautions_hindi']}"
                )
            else:
                ref_explanation = (
                    f"\n\n---"
                    f"\n🏛️ **सामान्य जानकारी (General Reference):** [India NLEM & Jan Aushadhi Catalog]"
                    f"\n🔹 **मूल जेनेरिक दवा (Active Salt):** {generic_name}"
                    f"\n🔹 **उपयोग (Purpose):** {ref['purpose_hindi']}"
                    f"\n⚠️ **जरूरी सावधानी (Caution):** {ref['standard_cautions_hindi']}"
                )
            if nlem_badge or jan_badge:
                ref_explanation += f"\n\n{nlem_badge} {jan_badge}"

        if lang == "en":
            explanation = (
                f"💊 **Medicine Name:** {name}\n"
                f"🔹 **Dosage:** {dose}\n"
                f"🕒 **When to take:** {freq} ({timing})\n"
                f"📅 **Duration:** {duration}"
                f"{ref_explanation}"
            )
        elif lang == "hinglish":
            explanation = (
                f"💊 **Dawai ka Naam:** {name}\n"
                f"🔹 **Kitni leni hai (Dose):** {dose}\n"
                f"🕒 **Kab leni hai (Timing):** {freq} ({timing})\n"
                f"📅 **Kitne din:** {duration}"
                f"{ref_explanation}"
            )
        else:
            explanation = (
                f"💊 **दवा का नाम:** {name}\n"
                f"🔹 **कितनी लेनी है:** {dose}\n"
                f"🕒 **कब लेनी है:** {freq} ({timing})\n"
                f"📅 **कितने दिन:** {duration}"
                f"{ref_explanation}"
            )
        return explanation

    def explain_prescription_summary(self, prescription: Prescription, lang: str = "hi") -> str:
        """
        Summary explanation for all confirmed medications on the prescription.
        """
        if not prescription.medicines:
            if lang == "en":
                return "No medicines detected in this prescription."
            elif lang == "hinglish":
                return "Is prescription me koi dawai nahi mili."
            return "इस पर्ची में कोई दवा नहीं मिली।"

        if lang == "en":
            lines = [
                f"Hello. Your prescription has {len(prescription.medicines)} confirmed medicines:\n"
            ]
        elif lang == "hinglish":
            lines = [
                f"Namaste. Aapke prescription me kul {len(prescription.medicines)} dawaiyan likhi hain:\n"
            ]
        else:
            lines = [
                f"नमस्ते। आपके पर्चे में कुल {len(prescription.medicines)} दवाएं लिखी हैं:\n"
            ]

        for i, med in enumerate(prescription.medicines, 1):
            name = med.candidate_medicine_name or med.raw_medicine_name
            timing = med.timing_raw or ("as directed" if lang == "en" else "निर्देशानुसार")
            freq = med.frequency_raw or ("regular" if lang == "en" else "नियमित")
            
            # Check Indian Database for generic salt
            ref = MedicineReferenceService.lookup_medicine(name)
            salt_lbl = "Active salt" if lang == "en" else "मूल दवा"
            salt_info = f" *({salt_lbl}: {ref['generic_name']})*" if ref else ""
            
            lines.append(f"{i}. **{name}**{salt_info} — {freq}, {timing}")

        if lang == "en":
            lines.append(
                "\n⚠️ **Important Safety Notice:** This summary is for educational reference only. "
                "Always consult your doctor or pharmacist in case of any questions."
            )
        elif lang == "hinglish":
            lines.append(
                "\n⚠️ **Zaroori Soochna:** Yeh aapki jaankari aur samajh ke liye simple summary hai. "
                "Kisi bhi doubt me turant doctor ya chemist se baat karein."
            )
        else:
            lines.append(
                "\n⚠️ **महत्वपूर्ण सूचना:** यह केवल आपके समझने के लिए सरल सारांश है। "
                "कृपया किसी भी संदेह की स्थिति में अपने डॉक्टर या फार्मासिस्ट से संपर्क करें।"
            )
        return "\n".join(lines)

    def generate_speech_audio(self, text_hindi: str, lang: str = "hi") -> Optional[bytes]:
        """
        Generates spoken audio using gTTS (Google Text-to-Speech) in Hindi or English.
        Fails safely if offline or error occurs.
        """
        if not text_hindi or not text_hindi.strip():
            return None

        # Clean markdown formatting before sending to TTS
        clean_text = (
            text_hindi.replace("**", "")
            .replace("💊", "दवा " if lang != "en" else "Medicine ")
            .replace("🕒", "समय " if lang != "en" else "Time ")
            .replace("📅", "दिन " if lang != "en" else "Duration ")
            .replace("⚠️", "चेतावनी " if lang != "en" else "Warning ")
            .replace("ℹ️", "जानकारी " if lang != "en" else "Notice ")
            .replace("🏛️", "")
            .replace("💡", "")
            .replace("✅", "")
            .replace("#", "")
            .replace("🔹", "")
            .replace("---", "")
        )

        try:
            from gtts import gTTS
            tts_lang = "en" if lang == "en" else "hi"
            tts = gTTS(text=clean_text, lang=tts_lang, slow=False)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp.read()
        except Exception:
            return None
