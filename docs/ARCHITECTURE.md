# Technical Architecture & System Design

**Project:** Sehat Saathi (सेहत साथी)  
**Lead:** Agent 1 (Technical Lead / Coordinator)  
**Stack:** Python 3.13, Starlette + Uvicorn, HTML/CSS/JavaScript, Google GenAI SDK, Pydantic v2, Pillow, Pytest

---

## 1. System Architecture Diagram

```
+--------------------------------------------------------------------------+
|                  Browser Frontend (webapp/static/)                      |
|   Overview -> Prescription Review -> Confirmed Reminders                |
|   -> Vitals & Wellbeing -> Nearby Care -> Grounded Health Q&A            |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                 Starlette ASGI App and JSON API (webapp/)                 |
|   Local-only by default; prescription photos handled in memory           |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                         Application Core & Services                      |
|                                                                          |
|  +---------------------------+   +------------------------------------+  |
|  |   PrescriptionExtractor   |   |        MedicineReferenceService    |  |
|  |  (BasePrescriptionExtractor)  |  (Indian Essential Drugs + RxNorm) |  |
|  |   - GeminiMultimodalImpl  |   +------------------------------------+  |
|  |   - MockExtractor (Tests) |                                           |
|  +---------------------------+   +------------------------------------+  |
|                                  |           LanguageService          |  |
|  +---------------------------+   |      (Hindi Explanations &         |  |
|  |      ReminderService      |   |       Audio / Web Speech TTS)      |  |
|  |  (Active/Upcoming/Status) |   +------------------------------------+  |
|  +---------------------------+                                           |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                     Data Models & Validation (models/)                   |
|   - Prescription (raw text, uncertainty flags, medicines)                |
|   - MedicineInstruction (dose, freq, duration, user_confirmed)           |
|   - Reminder (scheduled_time, status, notification_notes)                |
+------------------------------------+-------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                        Storage Layer (storage/)                          |
|   - LocalStorageAdapter (JSON / SessionState / SQLite ready)             |
|   - Privacy: Zero permanent patient image storage by default            |
+--------------------------------------------------------------------------+
```

---

Local JSON services and the SQLite clinical database use the directory configured by `SEHAT_DATA_DIR`; when unset, the repository's `data/` directory is used. The Vercel public demo forces its own temporary directory and remains read-only.

The browser prescription review calls `POST /api/prescriptions/explanation` and `POST /api/prescriptions/audio` only for a user-confirmed medicine and a supported language. Explanation text is generated locally by the language service; audio is generated through gTTS and requires an external network request. Real image extraction sends the uploaded image bytes to Gemini when a live API key is configured. In-memory image handling means the app does not write the upload to its local store; it does not guarantee third-party retention behavior.

## 2. Core Pydantic Schemas

### `MedicineInstruction`
```python
class MedicineInstruction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    raw_medicine_name: str
    candidate_medicine_name: Optional[str] = None
    strength: Optional[str] = None
    dose_instruction_raw: Optional[str] = None
    frequency_raw: Optional[str] = None
    duration_raw: Optional[str] = None
    timing_raw: Optional[str] = None
    quantity_raw: Optional[str] = None
    is_uncertain: bool = False
    uncertainty_reason: Optional[str] = None
    unresolved_fields: List[str] = Field(default_factory=list)
    user_confirmed: bool = False
```

### `Prescription`
```python
class Prescription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    original_text: Optional[str] = None
    extraction_status: str  # "SUCCESS", "PARTIAL", "FAILED", "UNCERTAIN"
    medicines: List[MedicineInstruction] = Field(default_factory=list)
    unresolved_fields: List[str] = Field(default_factory=list)
    user_confirmed: bool = False
    source_image_retained: bool = False
```

### `Reminder`
```python
class Reminder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    medicine_instruction_id: str
    medicine_name: str
    dosage: str
    reminder_time: str  # "HH:MM" 24hr format
    schedule_description: str
    enabled: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    user_confirmed: bool = True
```

---

## 3. Component Decoupling & Interfaces

### `BasePrescriptionExtractor`
Enables swapping extraction engines (e.g. `GeminiMultimodalExtractor`, `MockExtractor`, or a future `CloudVisionExtractor`) without changing UI logic:
```python
class BasePrescriptionExtractor(ABC):
    @abstractmethod
    def extract_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> Prescription:
        pass
```

### `BaseLanguageService`
Provides translation and Hindi explanation generation with graceful fallbacks:
```python
class BaseLanguageService(ABC):
    @abstractmethod
    def explain_prescription(self, prescription: Prescription) -> str:
        pass
    @abstractmethod
    def generate_speech_audio(self, text: str) -> Optional[bytes]:
        pass
```

### Privacy & Storage Strategy
- Uploaded prescription photos are processed in-memory (`BytesIO`) and not written to the app's local store. When live scanning is enabled, image bytes are sent to Gemini; this local behavior does not determine Gemini's data retention.
- The browser's optional read-aloud feature sends explanation text to Google Text-to-Speech through gTTS.
- Confirmed schedules are saved in a clean session state or lightweight local JSON file (`data/saved_schedules.json`), editable and deletable by the user at any time.
