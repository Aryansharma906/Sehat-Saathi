"""
Prescription Extraction Service
Provides BasePrescriptionExtractor interface, GeminiMultimodalExtractor, and MockPrescriptionExtractor.
Enforces Medical Safety Invariants (Rule 1, 2, 4, 10, 15).
"""

from abc import ABC, abstractmethod
import os
import json
from typing import Optional, List
from pydantic import BaseModel, Field

from models.prescription import MedicineInstruction, Prescription, ExtractionStatus


class StructuredMedicineOutput(BaseModel):
    raw_medicine_name: str = Field(description="Exact raw text read from image")
    candidate_medicine_name: Optional[str] = Field(default=None, description="Cleaned brand or generic name")
    strength: Optional[str] = Field(default=None, description="Strength e.g. 500 mg, or null if missing")
    dose_instruction_raw: Optional[str] = Field(default=None, description="Dosage e.g. 1 tablet, or null if missing")
    frequency_raw: Optional[str] = Field(default=None, description="Frequency e.g. Twice daily, OD, BD, or null")
    duration_raw: Optional[str] = Field(default=None, description="Duration e.g. 5 days, or null")
    timing_raw: Optional[str] = Field(default=None, description="Timing e.g. After meals, or null")
    quantity_raw: Optional[str] = Field(default=None, description="Quantity or null")
    is_uncertain: bool = Field(default=False, description="True if handwriting is ambiguous or difficult to read")
    uncertainty_reason: Optional[str] = Field(default=None, description="Why this field is uncertain")
    unresolved_fields: List[str] = Field(default_factory=list, description="List of unreadable field names")


class StructuredPrescriptionOutput(BaseModel):
    patient_name: Optional[str] = None
    prescription_date: Optional[str] = None
    doctor_info: Optional[str] = None
    original_text: Optional[str] = Field(description="Full text transcription of the prescription")
    medicines: List[StructuredMedicineOutput] = Field(default_factory=list)


EXTRACTION_SYSTEM_PROMPT = """
You are a specialized clinical transcription assistant for Sehat Saathi, an accessible assistive app for patients in rural India.
Your mission is to read handwritten or printed medical prescriptions with strict medical safety.

CRITICAL SAFETY RULES:
1. Extract ONLY what is explicitly legible in the image.
2. DO NOT invent, guess, or assume missing dosages, frequencies, or durations. If a duration or dose is not written, return null.
3. If handwriting is ambiguous, faint, or could be read as multiple different medicines, set is_uncertain=true, record the unreadable fields in unresolved_fields, and explain why in uncertainty_reason.
4. Preserve the raw text exactly as interpreted in raw_medicine_name.
5. In original_text, provide a complete verbatim transcription of the text in the prescription.
"""


class BasePrescriptionExtractor(ABC):
    @abstractmethod
    def extract_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Prescription:
        pass


class GeminiMultimodalExtractor(BasePrescriptionExtractor):
    """
    Multimodal visual extractor using the official google-genai SDK.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None

    def extract_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Prescription:
        if not self.api_key or not self.client:
            return Prescription(
                extraction_status=ExtractionStatus.FAILED,
                original_text="API कुंजी उपलब्ध नहीं है (GEMINI_API_KEY is missing or invalid).",
                unresolved_fields=["GEMINI_API_KEY"]
            )

        try:
            from google.genai import types

            image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    EXTRACTION_SYSTEM_PROMPT,
                    "Please transcribe and extract all medicine instructions from this prescription image into the structured JSON schema.",
                    image_part,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=StructuredPrescriptionOutput.model_json_schema(),
                    temperature=0.1,  # Low temperature for grounded transcription
                ),
            )

            if not response.text:
                return Prescription(
                    extraction_status=ExtractionStatus.FAILED,
                    original_text="मॉडल से कोई प्रतिक्रिया नहीं मिली (Empty response from AI model)."
                )

            data = json.loads(response.text)
            structured = StructuredPrescriptionOutput.model_validate(data)

            # Map to domain models
            medicines = []
            for item in structured.medicines:
                med = MedicineInstruction(
                    raw_medicine_name=item.raw_medicine_name,
                    candidate_medicine_name=item.candidate_medicine_name,
                    strength=item.strength,
                    dose_instruction_raw=item.dose_instruction_raw,
                    frequency_raw=item.frequency_raw,
                    duration_raw=item.duration_raw,
                    timing_raw=item.timing_raw,
                    quantity_raw=item.quantity_raw,
                    is_uncertain=item.is_uncertain,
                    uncertainty_reason=item.uncertainty_reason,
                    unresolved_fields=item.unresolved_fields,
                    user_confirmed=False
                )
                medicines.append(med)

            status = ExtractionStatus.SUCCESS
            if any(m.is_uncertain for m in medicines):
                status = ExtractionStatus.UNCERTAIN

            return Prescription(
                patient_name=structured.patient_name,
                prescription_date=structured.prescription_date,
                doctor_info=structured.doctor_info,
                original_text=structured.original_text,
                extraction_status=status,
                medicines=medicines,
                unresolved_fields=[field for m in medicines for field in m.unresolved_fields],
                user_confirmed=False
            )

        except Exception as e:
            return Prescription(
                extraction_status=ExtractionStatus.FAILED,
                original_text=f"पर्ची पढ़ने में त्रुटि (Extraction error): {str(e)}",
                unresolved_fields=["EXTRACTION_ERROR"]
            )


class MockPrescriptionExtractor(BasePrescriptionExtractor):
    """
    Deterministic mock extractor for automated testing and offline demos.
    Simulates:
    1. Clean legible prescription (Dolo 650, Pantoprazole 40mg)
    2. Ambiguous handwritten prescription with explicit uncertainty flag (Amoxicillin/Augmentin ambiguous dose)
    """

    def __init__(self, scenario: str = "clean"):
        self.scenario = scenario

    def extract_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Prescription:
        if self.scenario == "ambiguous":
            # Demonstrates Invariant 2 & 15: Highlight uncertain handwriting
            m1 = MedicineInstruction(
                raw_medicine_name="Tab Dolo 650",
                candidate_medicine_name="Dolo 650 (Paracetamol)",
                strength="650 mg",
                dose_instruction_raw="1 गोली (1 tablet)",
                frequency_raw="TDS (दिन में 3 बार)",
                duration_raw="3 दिन (3 days)",
                timing_raw="खाने के बाद (After Food)",
                is_uncertain=False,
                user_confirmed=False
            )
            m2 = MedicineInstruction(
                raw_medicine_name="Cap Amox... [illegible handwriting]",
                candidate_medicine_name="Amoxicillin (अनुमानित / Possible)",
                strength=None,  # Rule 1: unknown dose must NOT be guessed
                dose_instruction_raw=None,
                frequency_raw="BD (दिन में 2 बार)",
                duration_raw=None,
                timing_raw="खाने के बाद (After Food)",
                is_uncertain=True,
                uncertainty_reason="डॉक्टर की लिखावट अस्पष्ट है (Handwriting unclear. Strength and duration unreadable).",
                unresolved_fields=["strength", "dose_instruction_raw", "duration_raw"],
                user_confirmed=False
            )
            return Prescription(
                patient_name="Ramesh Kumar (काल्पनिक / Synthetic)",
                prescription_date="2026-10-26",
                doctor_info="Dr. A. Sharma, Community Health Centre",
                original_text="Rx:\n1. Tab Dolo 650 - 1 TDS x 3 days p/c\n2. Cap Amox... [unclear dose] - 1 BD p/c",
                extraction_status=ExtractionStatus.UNCERTAIN,
                medicines=[m1, m2],
                unresolved_fields=["strength", "duration_raw"],
                user_confirmed=False
            )
        elif self.scenario == "failure":
            return Prescription(
                extraction_status=ExtractionStatus.FAILED,
                original_text="तस्वीर बहुत धुंधली होने के कारण पर्ची नहीं पढ़ी जा सकी।",
                unresolved_fields=["IMAGE_UNREADABLE"]
            )
        else:
            # Clean scenario
            m1 = MedicineInstruction(
                raw_medicine_name="Tab Pan-D",
                candidate_medicine_name="Pan-D (Pantoprazole + Domperidone)",
                strength="40 mg / 30 mg",
                dose_instruction_raw="1 कैप्सूल (1 capsule)",
                frequency_raw="OD (दिन में 1 बार)",
                duration_raw="5 दिन (5 days)",
                timing_raw="सुबह खाली पेट (Morning Before Food)",
                is_uncertain=False,
                user_confirmed=False
            )
            m2 = MedicineInstruction(
                raw_medicine_name="Tab Dolo 650",
                candidate_medicine_name="Dolo 650 (Paracetamol)",
                strength="650 mg",
                dose_instruction_raw="1 गोली (1 tablet)",
                frequency_raw="SOS / जरूरत पड़ने पर (When required for fever)",
                duration_raw="3 दिन (3 days)",
                timing_raw="खाने के बाद (After Food)",
                is_uncertain=False,
                user_confirmed=False
            )
            return Prescription(
                patient_name="Sunita Devi (काल्पनिक / Synthetic)",
                prescription_date="2026-10-26",
                doctor_info="Primary Health Centre (PHC), Rajasthan",
                original_text="Rx:\n1. Tab Pan-D - 1 OD empty stomach x 5 days\n2. Tab Dolo 650 - 1 SOS after food x 3 days",
                extraction_status=ExtractionStatus.SUCCESS,
                medicines=[m1, m2],
                user_confirmed=False
            )
