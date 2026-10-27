"""
Tests for Prescription Extraction Service
"""

import pytest
from services.prescription_extractor import (
    MockPrescriptionExtractor,
    GeminiMultimodalExtractor,
    ExtractionStatus,
    live_extractor_or_none,
)


def test_mock_clean_extraction():
    extractor = MockPrescriptionExtractor(scenario="clean")
    prescription = extractor.extract_from_image(b"fake_image_bytes")

    assert prescription.extraction_status == ExtractionStatus.SUCCESS
    assert len(prescription.medicines) == 2
    assert prescription.medicines[0].candidate_medicine_name.startswith("Pan-D")
    assert prescription.medicines[0].is_uncertain is False
    assert prescription.medicines[0].user_confirmed is False


def test_mock_ambiguous_extraction_flags_uncertainty():
    extractor = MockPrescriptionExtractor(scenario="ambiguous")
    prescription = extractor.extract_from_image(b"fake_image_bytes")

    assert prescription.extraction_status == ExtractionStatus.UNCERTAIN
    assert len(prescription.medicines) == 2
    
    # Medicine 2 should have explicit uncertainty
    med2 = prescription.medicines[1]
    assert med2.is_uncertain is True
    assert "strength" in med2.unresolved_fields
    assert med2.strength is None  # Never guessed!
    assert med2.user_confirmed is False


def test_mock_failure_scenario():
    extractor = MockPrescriptionExtractor(scenario="failure")
    prescription = extractor.extract_from_image(b"fake_image_bytes")

    assert prescription.extraction_status == ExtractionStatus.FAILED
    assert len(prescription.medicines) == 0


def test_gemini_missing_api_key_fails_safely():
    # Pass empty API key
    extractor = GeminiMultimodalExtractor(api_key="")
    prescription = extractor.extract_from_image(b"fake_image_bytes")

    assert prescription.extraction_status == ExtractionStatus.FAILED
    assert "GEMINI_API_KEY" in prescription.unresolved_fields


def test_live_scanning_requires_api_key_and_demo_mode_off():
    assert live_extractor_or_none(None, demo_mode=False) is None
    assert live_extractor_or_none("", demo_mode=False) is None
    assert live_extractor_or_none("configured-key", demo_mode=True) is None
    assert isinstance(live_extractor_or_none("configured-key", demo_mode=False), GeminiMultimodalExtractor)
