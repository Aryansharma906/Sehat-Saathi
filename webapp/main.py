"""Browser-first Sehat Saathi web app backed by the existing safety services."""

import json
import os
import re
import sys
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from models.prescription import MedicineInstruction, Prescription  # noqa: E402
from services.chat_service import PrescriptionChatService  # noqa: E402
from services.device_data_service import DeviceDataService  # noqa: E402
from services.emergency_service import EmergencyService  # noqa: E402
from services.health_issue_service import HealthIssueService  # noqa: E402
from services.image_processing import ImageProcessingService  # noqa: E402
from services.mental_health_service import MentalHealthService  # noqa: E402
from services.prevention_and_facilities import PreventionAndFacilitiesService  # noqa: E402
from services.prescription_extractor import GeminiMultimodalExtractor, MockPrescriptionExtractor  # noqa: E402
from services.progress_tracker_service import ProgressTrackerService  # noqa: E402
from services.proximity_service import ProximityLocationService  # noqa: E402
from services.reminder_service import ReminderService  # noqa: E402
from services.medicine_reference import MedicineReferenceService  # noqa: E402
from storage.persistence import LocalStorageAdapter  # noqa: E402
from services.storage_config import get_data_dir  # noqa: E402

APP_MODE = os.environ.get("SEHAT_ENV", "development").strip().lower()
PUBLIC_DEMO = APP_MODE == "demo"
DATA_DIR = Path(tempfile.gettempdir()) / "sehat-saathi-public-demo" if PUBLIC_DEMO else get_data_dir()


@asynccontextmanager
async def lifespan(_: Starlette):
    if os.environ.get("SEHAT_ENV", "development").strip().lower() in {"production", "prod"}:
        raise RuntimeError(
            "Production startup is disabled: this prototype has no approved identity, "
            "authorization, audit, resilient storage, or clinical deployment controls."
        )
    yield

reminders = ReminderService(LocalStorageAdapter(DATA_DIR / "saved_schedules.json"))
vitals = DeviceDataService(DATA_DIR / "device_vitals.json")
chat = PrescriptionChatService()
issues = HealthIssueService(DATA_DIR / "treatment_issues.json")
progress = ProgressTrackerService(DATA_DIR / "progress_records.json")
wellness = MentalHealthService(DATA_DIR / "mental_health_records.json")

ASSETS = Path(__file__).resolve().parent / "static"


def payload(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [payload(item) for item in value]
    if isinstance(value, dict):
        return {key: payload(item) for key, item in value.items()}
    return value


async def json_body(request: Request) -> dict:
    try:
        if int(request.headers.get("content-length", "0")) > 64 * 1024:
            raise HTTPException(413, "Request is too large.")
    except ValueError as exc:
        raise HTTPException(400, "Invalid content length.") from exc
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(400, "Please send valid JSON.") from exc
    if not isinstance(body, dict):
        raise HTTPException(400, "A JSON object is required.")
    return body


async def home(_: Request):
    return FileResponse(ASSETS / "index.html")


async def overview(_: Request):
    saved = reminders.get_all_reminders()
    readings = vitals.get_all_readings()
    p_checkins = progress.get_all_checkins()
    m_checkins = wellness.get_all_checkins()
    locality = "Neemrana"
    nearby = ProximityLocationService.find_facilities_within_proximity(locality, max_radius_miles=10)
    return JSONResponse({
        "reminders": payload(saved),
        "vitals": payload(readings[:12]),
        "progress": payload(p_checkins[:5]),
        "wellness": payload(m_checkins[:5]),
        "issues": payload(issues.get_all_issues()[:8]),
        "nearby": nearby,
        "emergency": EmergencyService.get_emergency_numbers(),
        "demo_mode": not bool(os.environ.get("GEMINI_API_KEY")),
        "service_scope": {
            "status": "public_demo" if PUBLIC_DEMO else "prototype",
            "region": "Neemrana, Rajasthan, India demo cluster",
            "production_ready": False,
            "demo_read_only": PUBLIC_DEMO,
            "notice": (
                "Public demo: synthetic examples only. Changes are not saved; do not enter personal or patient information."
                if PUBLIC_DEMO else
                "Prototype with local demo data. Not a government service or a clinical record system."
            ),
        },
    })


async def facilities(request: Request):
    locality = request.query_params.get("locality", "Neemrana")
    if not locality.strip():
        raise HTTPException(400, "Enter a town or city to search.")
    try:
        radius = min(max(float(request.query_params.get("radius", "10")), 1), 100)
    except ValueError as exc:
        raise HTTPException(400, "Radius must be a number.") from exc
    return JSONResponse(ProximityLocationService.find_facilities_within_proximity(locality, max_radius_miles=radius))


async def prescription_scan(request: Request):
    try:
        if int(request.headers.get("content-length", "0")) > 11 * 1024 * 1024:
            raise HTTPException(413, "Choose an image smaller than 10 MB.")
    except ValueError as exc:
        raise HTTPException(400, "Invalid content length.") from exc
    form = await request.form()
    upload = form.get("prescription")
    if upload is None or not hasattr(upload, "read"):
        raise HTTPException(400, "Choose a prescription image first.")
    from io import BytesIO
    image_buffer = BytesIO()
    size = 0
    while chunk := await upload.read(64 * 1024):
        size += len(chunk)
        if size > 10 * 1024 * 1024:
            raise HTTPException(413, "Choose an image smaller than 10 MB.")
        image_buffer.write(chunk)
    image_bytes = image_buffer.getvalue()
    ok, error = ImageProcessingService.validate_file(image_bytes, getattr(upload, "filename", "prescription.jpg"))
    if not ok:
        raise HTTPException(400, error or "This image could not be read.")
    image, error = ImageProcessingService.load_and_normalize(image_bytes)
    if image is None:
        raise HTTPException(400, error or "This image could not be opened.")
    good, quality_hint = ImageProcessingService.assess_quality(image)
    if not good:
        return JSONResponse({"quality_warning": quality_hint, "prescription": None}, status_code=422)
    out = BytesIO()
    image.save(out, format="JPEG", quality=92)
    extracted = GeminiMultimodalExtractor().extract_from_image(out.getvalue(), "image/jpeg")
    return JSONResponse({"quality_warning": quality_hint, "prescription": payload(extracted)})


async def prescription_demo(request: Request):
    body = await json_body(request)
    scenario = body.get("scenario", "clean")
    if scenario not in {"clean", "ambiguous"}:
        raise HTTPException(400, "Unknown demo prescription.")
    image_name = "ambiguous_sample_prescription.jpg" if scenario == "ambiguous" else "clean_sample_prescription.jpg"
    image_bytes = (Path(__file__).resolve().parent / "demo_data" / image_name).read_bytes()
    extracted = MockPrescriptionExtractor(scenario=scenario).extract_from_image(image_bytes, "image/jpeg")
    return JSONResponse({"quality_warning": None, "prescription": payload(extracted), "demo": True})


async def create_schedule(request: Request):
    body = await json_body(request)
    try:
        medicine = MedicineInstruction.model_validate(body.get("medicine", {}))
    except Exception as exc:
        raise HTTPException(422, f"Medicine details need review: {exc}") from exc
    if not medicine.user_confirmed:
        raise HTTPException(409, "Confirm that you checked this medicine against the prescription before saving a reminder.")
    if not medicine.candidate_medicine_name or not medicine.dose_instruction_raw or not medicine.frequency_raw or not medicine.timing_raw:
        raise HTTPException(422, "The medicine name, dose, frequency, and timing must be legible and confirmed before a reminder can be created.")
    frequency = medicine.frequency_raw.strip().lower()
    words = set(re.findall(r"[a-z]+", frequency))
    known_schedule = (
        bool(words & {"od", "bd", "bid", "tds", "tid"})
        or ({"once"} <= words and bool(words & {"daily", "day"}))
        or bool(words & {"twice", "three"}) and bool(words & {"daily", "times"})
        or bool(re.search(r"(?<!\w)[123](?!\w)", frequency)) and bool(words & {"daily", "times"})
        or any(token in frequency for token in ("दिन में 1 बार", "एक बार", "2 बार", "दो बार", "3 बार", "तीन बार"))
    )
    if not known_schedule:
        raise HTTPException(422, "This frequency does not map to a safe reminder schedule. Please ask your prescriber or pharmacist to clarify it.")
    conflicts = reminders.check_potential_conflicts(medicine)
    if conflicts and not body.get("acknowledge_conflicts"):
        return JSONResponse({"conflicts": conflicts, "created": []}, status_code=409)
    times = body.get("times")
    if times is not None:
        if (
            not isinstance(times, list)
            or not times
            or any(not isinstance(value, str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value) for value in times)
        ):
            raise HTTPException(422, "Provide one or more valid reminder times in 24-hour HH:MM format.")
        if len(set(times)) != len(times):
            raise HTTPException(422, "Reminder times must be unique.")
    created = reminders.create_reminders_from_instruction(
        medicine,
        custom_times=times,
        prescription_id=body.get("prescription_id"),
        prescription_date=body.get("prescription_date"),
    )
    return JSONResponse({"conflicts": conflicts, "created": payload(created)})


async def reminder_action(request: Request):
    reminder_id = request.path_params["reminder_id"]
    action = request.path_params["action"]
    if action == "toggle":
        result = reminders.toggle_reminder(reminder_id)
    elif action == "taken":
        result = reminders.mark_as_taken(reminder_id, True)
    elif action == "delete":
        result = reminders.delete_reminder(reminder_id)
    elif action == "time":
        body = await json_body(request)
        value = str(body.get("time", ""))
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
            raise HTTPException(422, "Choose a valid time in 24-hour format.")
        existing = next((r for r in reminders.get_all_reminders() if r.id == reminder_id), None)
        if existing is None:
            raise HTTPException(404, "Reminder not found.")
        existing.reminder_time = value
        result = reminders.storage.update_reminder(existing)
    else:
        raise HTTPException(404, "Unknown reminder action.")
    if result is None or (action != "toggle" and result is False):
        raise HTTPException(404, "Reminder not found.")
    return JSONResponse({"ok": True, "result": result, "reminders": payload(reminders.get_all_reminders())})


async def create_vital(request: Request):
    body = await json_body(request)
    required = ("device_type", "metric_name", "value", "unit")
    if any(not str(body.get(key, "")).strip() for key in required):
        raise HTTPException(422, "Device, measure, value, and unit are required.")
    try:
        reading = vitals.record_reading(
            *(str(body[key]).strip() for key in required),
            sync_source=str(body.get("sync_source", "Manual / Device Export")),
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return JSONResponse({"reading": payload(reading)})


async def ask_question(request: Request):
    body = await json_body(request)
    question = str(body.get("question", "")).strip()
    if not question:
        raise HTTPException(422, "Write a question first.")
    if len(question) > 1200:
        raise HTTPException(413, "Please keep the question under 1,200 characters.")
    prescription = None
    if body.get("prescription"):
        try:
            prescription = Prescription.model_validate(body["prescription"])
        except Exception:
            prescription = None
    return JSONResponse({"answer": chat.ask_question(question, prescription)})


async def progress_checkin(request: Request):
    body = await json_body(request)
    required = ("feeling", "adherence", "symptoms")
    if any(not str(body.get(key, "")).strip() for key in required):
        raise HTTPException(422, "Answer all three check-in questions.")
    entry = progress.evaluate_checkin(*(str(body[key]) for key in required), lang=body.get("lang", "en"))
    return JSONResponse({"checkin": payload(entry)})


async def mental_checkin(request: Request):
    body = await json_body(request)
    required = ("sleep", "stress", "mood")
    if any(not str(body.get(key, "")).strip() for key in required):
        raise HTTPException(422, "Answer all three check-in questions.")
    entry = wellness.evaluate_mental_wellness(*(str(body[key]) for key in required), lang=body.get("lang", "en"))
    return JSONResponse({"checkin": payload(entry)})


async def log_issue(request: Request):
    body = await json_body(request)
    if not str(body.get("medicine_name", "")).strip() or not str(body.get("issue_type", "")).strip():
        raise HTTPException(422, "Medicine and concern are required.")
    issue = issues.log_issue(
        str(body["medicine_name"]).strip(), str(body["issue_type"]).strip(),
        str(body.get("severity", "Mild")), str(body.get("notes", "")).strip() or None,
    )
    return JSONResponse({"issue": payload(issue)})


async def health_resources(_: Request):
    return JSONResponse({
        "emergency": EmergencyService.get_emergency_numbers(),
        "prevention": PreventionAndFacilitiesService.get_prevention_topics(),
        "medicines": MedicineReferenceService.get_essential_medicines_summary(),
    })


async def health(_: Request):
    return JSONResponse({"status": "ok", "app": "Sehat Saathi"})


async def http_error(request: Request, exc: HTTPException):
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)


routes = [
    Route("/", home),
    Route("/api/health", health),
    Route("/api/overview", overview),
    Route("/api/resources", health_resources),
    Route("/api/facilities", facilities),
    Route("/api/prescriptions/scan", prescription_scan, methods=["POST"]),
    Route("/api/prescriptions/demo", prescription_demo, methods=["POST"]),
    Route("/api/reminders", create_schedule, methods=["POST"]),
    Route("/api/reminders/{reminder_id:str}/{action:str}", reminder_action, methods=["POST"]),
    Route("/api/vitals", create_vital, methods=["POST"]),
    Route("/api/chat", ask_question, methods=["POST"]),
    Route("/api/progress", progress_checkin, methods=["POST"]),
    Route("/api/wellness", mental_checkin, methods=["POST"]),
    Route("/api/issues", log_issue, methods=["POST"]),
    Mount("/assets", app=StaticFiles(directory=ASSETS), name="assets"),
    Mount("/illustrations", app=StaticFiles(directory=ROOT / "static"), name="illustrations"),
]

async def demo_access_guard(request: Request, call_next):
    if PUBLIC_DEMO:
        is_synthetic_example = request.url.path == "/api/prescriptions/demo" and request.method == "POST"
        if request.method not in {"GET", "HEAD", "OPTIONS"} and not is_synthetic_example:
            return JSONResponse(
                {"detail": "This public demo is read-only. Do not submit personal or patient information."},
                status_code=403,
                headers={"Cache-Control": "no-store"},
            )
    response = await call_next(request)
    if PUBLIC_DEMO:
        response.headers["Cache-Control"] = "no-store"
    return response


app = Starlette(
    debug=False,
    routes=routes,
    exception_handlers={HTTPException: http_error},
    lifespan=lifespan,
    middleware=[Middleware(BaseHTTPMiddleware, dispatch=demo_access_guard)],
)
