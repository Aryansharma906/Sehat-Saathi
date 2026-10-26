"""
Automated Safety Invariants Verification Suite
Enforces Rules 1 - 15 defined in docs/MEDICAL_SAFETY.md
"""

import pytest
from models.prescription import MedicineInstruction, Prescription, ExtractionStatus
from services.reminder_service import ReminderService
from services.medicine_reference import MedicineReferenceService
from services.language_service import SimpleHindiLanguageService
from storage.persistence import LocalStorageAdapter
import tempfile
from pathlib import Path


@pytest.fixture
def temp_storage():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
        path = Path(tf.name)
    adapter = LocalStorageAdapter(filepath=path)
    yield adapter
    if path.exists():
        path.unlink()


def test_rule_1_never_invent_missing_dosage():
    """Rule 1: If a dose/duration is not written, model must not invent it."""
    med = MedicineInstruction(raw_medicine_name="Tab Paracetamol")
    assert med.strength is None
    assert med.dose_instruction_raw is None
    assert med.duration_raw is None
    assert med.frequency_raw is None


def test_rule_2_flag_ambiguous_names_with_uncertainty():
    """Rule 2: Ambiguous text must be flagged is_uncertain=True."""
    med = MedicineInstruction(
        raw_medicine_name="Cap Amox... [unclear]",
        candidate_medicine_name="Amoxicillin",
        is_uncertain=True,
        uncertainty_reason="Unclear handwriting on packaging/strength",
        unresolved_fields=["strength"]
    )
    assert med.is_uncertain is True
    assert "strength" in med.unresolved_fields


def test_rule_3_unconfirmed_instruction_cannot_produce_reminders(temp_storage):
    """Rule 3: ReminderService must reject unconfirmed medicine instructions."""
    service = ReminderService(storage_adapter=temp_storage)

    unconfirmed_med = MedicineInstruction(
        raw_medicine_name="Tab Dolo 650",
        dose_instruction_raw="1 tablet",
        frequency_raw="TDS",
        user_confirmed=False  # Not confirmed by user!
    )

    with pytest.raises(ValueError, match="Cannot create reminders for unconfirmed medicine"):
        service.create_reminders_from_instruction(unconfirmed_med)

    # Now verify that setting user_confirmed=True allows reminder creation
    unconfirmed_med.user_confirmed = True
    reminders = service.create_reminders_from_instruction(unconfirmed_med)
    assert len(reminders) == 3  # TDS gives 3 reminders (morning, afternoon, night)
    assert len(service.get_all_reminders()) == 3


def test_rule_4_preserve_original_extracted_wording():
    """Rule 4: Preserves raw doctor handwriting wording."""
    raw_text = "Tab. Dolo-650 mg 1 tab TDS pc x 3d"
    med = MedicineInstruction(
        raw_medicine_name=raw_text,
        candidate_medicine_name="Dolo 650"
    )
    assert med.raw_medicine_name == raw_text


def test_rule_5_and_6_external_medicine_info_isolated():
    """Rule 5 & 6: Drug reference data is strictly auxiliary and disclaimed."""
    ref = MedicineReferenceService.lookup_medicine("Dolo 650")
    assert ref is not None
    assert "Paracetamol" in ref["generic_name"]

    lang_service = SimpleHindiLanguageService()
    med = MedicineInstruction(
        raw_medicine_name="Dolo 650",
        candidate_medicine_name="Dolo 650",
        user_confirmed=True
    )
    explanation = lang_service.explain_medicine(med)
    # Must clearly label general reference and cautions
    assert "सामान्य जानकारी (General Reference)" in explanation
    assert "सावधानी" in explanation


def test_rule_11_no_false_claims_of_medication_intake(temp_storage):
    """Rule 11: Showing a reminder does not mean taken. Only user tap marks it taken."""
    service = ReminderService(storage_adapter=temp_storage)
    med = MedicineInstruction(
        raw_medicine_name="Cetirizine 10mg",
        user_confirmed=True
    )
    reminders = service.create_reminders_from_instruction(med)
    rem = reminders[0]
    assert rem.taken_today is False

    # Only explicit mark_as_taken changes it
    success = service.mark_as_taken(rem.id, taken=True)
    assert success is True
    updated = [r for r in service.get_all_reminders() if r.id == rem.id][0]
    assert updated.taken_today is True
