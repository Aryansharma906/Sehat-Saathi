"""
Tests for Grounded Chatbot & Medical Safety
"""

import pytest
from services.chat_service import PrescriptionChatService
from models.prescription import Prescription, MedicineInstruction


def test_emergency_tripwire():
    chat = PrescriptionChatService(api_key=None)
    response = chat.ask_question("मरीज के सीने में दर्द हो रहा है (Patient has chest pain)")
    assert "आपातकालीन सूचना" in response
    assert "108 / 112" in response


def test_no_diagnosis_tripwire():
    chat = PrescriptionChatService(api_key=None)
    response = chat.ask_question("मुझे बुखार और उल्टी है, मुझे क्या बीमारी है?")
    assert "निदान (diagnosis) नहीं कर सकता" in response
    assert "डॉक्टर या नजदीकी स्वास्थ्य केंद्र" in response


def test_grounded_prescription_query_fallback():
    chat = PrescriptionChatService(api_key=None)
    med = MedicineInstruction(
        raw_medicine_name="Tab Dolo 650",
        candidate_medicine_name="Dolo 650",
        timing_raw="खाने के बाद",
        frequency_raw="TDS",
        user_confirmed=True
    )
    presc = Prescription(medicines=[med])
    response = chat.ask_question("यह दवा कब लेनी है?", confirmed_prescription=presc)
    assert "Dolo 650" in response
    assert "फार्मासिस्ट या डॉक्टर" in response
