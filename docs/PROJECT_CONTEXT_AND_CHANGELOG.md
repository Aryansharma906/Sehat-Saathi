# Sehat Saathi — Full Project Context and Change Record

**Prepared:** 2026-10-27
**Repository:** `https://github.com/Aryansharma906/Sehat-Saathi`
**Purpose:** One-file handoff for a new developer, reviewer, or AI coding assistant. It summarizes the product, architecture, verified boundaries, Git history, latest known validation, outstanding work, and deployment discussion. It does not reproduce local health-data files or credentials.

## 1. Executive summary

Sehat Saathi ("health companion") is an India-focused research prototype exploring how a browser app can help people and caregivers read prescription text, review uncertainty, organize confirmed medication reminders, and record everyday health notes. It is not a government service, clinical record system, validated medical device, or production-ready product. Use only synthetic data.

The repository began as a Streamlit application and grew into a multi-feature local prototype. It now also contains a browser-first Starlette app and an isolated, read-only Vercel demo. The deployed demo's intended scope is synthetic prescription examples and read-only interaction. Local JSON/SQLite records are not a multi-user cloud backend.

The most recent committed change, `e1d302f`, adds the `SEHAT_DATA_DIR` setting so local testing can redirect data away from the repository's `data/` folder. This does not add cloud persistence, user authentication, tenant separation, or authorization.

## 2. Product purpose and intended users

- **Problem explored:** Handwritten prescriptions, medicine abbreviations, language barriers, and fragmented care notes can be difficult for patients, older adults, and caregivers to manage.
- **Intended assistance:** Show extracted wording with uncertainty, help a person organize instructions they have checked, and prepare notes for discussion with a clinician, pharmacist, or caregiver.
- **Primary context:** India-focused Hindi/English content and a small demo facility cluster. Some UI copy supports English, Hindi, and Hinglish.
- **Not intended to:** Diagnose, prescribe, verify a treatment plan, replace a clinician or pharmacist, establish nationwide service coverage, or make autonomous care decisions.
- **Safety principle:** Preserve raw prescription wording and ambiguity. Do not invent medicine name, dose, strength, duration, or timing. A reminder requires user review/confirmation. General references are educational and distinct from the prescription.

The plain-language short brief is also available at `docs/PROJECT_BRIEF.md`.

## 3. Current status and non-negotiable limits

### Verified project status

- Local research prototype. `SEHAT_ENV=production` intentionally blocks startup until required identity, authorization, audit, storage, security, clinical governance, and operational controls exist.
- Public Vercel entry point (`index.py`) forces `SEHAT_ENV=demo`; demo storage is isolated under the temporary directory, write routes are blocked, and only bundled synthetic prescription samples are intended to be used.
- Vercel deployment configuration excludes repository `data/`, local environment files, tests, and development folders from the deploy bundle.
- Local non-demo data services use JSON files and a local SQLite database. They do not support multiple authenticated users or secure tenant separation.
- The facility directory is a small Neemrana / Rajasthan / NCR demo cluster. It is not nationwide, and there is no U.S. public-service configuration.
- Gemini prescription extraction requires an API key. Mock/synthetic flows exist for local tests and sample behavior.

### Authentication and clinician claims

- **Google sign-in is not implemented.** `AuthService.get_google_auth_url()` fails closed. A complete OAuth callback, state validation, provider-token validation, and secure session lifecycle are absent.
- **Local profiles are not accounts.** The profile service can construct/store prototype profile objects; there is no secure identity, session, account recovery, or role-based authorization.
- **Doctor/staff profile details are unverified.** A submitted license/employee number is not proof of credentials. The app does not check a trusted registry, authenticate clinicians, or protect a clinician portal.
- The project discussion chose separate India/U.S. clinician verification adapters if such a workflow is later built. It also explicitly rejected claiming an official registry integration and instead discussed an app-owned records database. An app-owned database can hold applications and review status; it cannot prove a license without an authorized independent verification process.

### Health data and deployment

- Do not enter real patient or personal health information in the local prototype or current public demo.
- Vercel function filesystems are not a durable database. A storage provider must be provisioned and the application must be explicitly integrated before cloud writes are possible.
- A database by itself does not add authentication, authorization, consent, audit trails, encryption policy, backup/restore, support, security review, or clinical approval.
- A Mumbai data region is a hosting/data-location selection; it does not establish legal compliance or government approval.
- The user's latest database choice: **synthetic-only staging, India/Mumbai hosted**. No database project/resource has been provisioned. The Vercel browser session was signed out; the integration setup page redirected to Vercel login. Continue only after the user signs in in the browser. Do not request credentials or secrets in chat.
- The user earlier asked to be asked before provisioning and subsequently authorized only synthetic staging. Do not expand that authorization to paid plans, production health-data storage, U.S. data storage, or real users.

## 4. Architecture and how it works

### Main entry points

- `app/main.py` — legacy Streamlit UI, maintained for compatibility/regression tests; the primary supported local experience is now the browser app.
- `webapp/main.py` — Starlette ASGI app, APIs, local services wiring, and static asset routes.
- `webapp/static/index.html`, `app.css`, `app.js` — browser UI.
- `index.py` — Vercel entrypoint; sets demo mode before importing the app.
- `vercel.json`, `.vercelignore` — function packaging and exclusion configuration.

### Core layers

- `models/` — Pydantic schemas for prescriptions, reminders, health issues, progress, vitals/wellness, and complication-prediction records.
- `services/` — extraction, image checks, translation/read-aloud, medicine reference, reminder rules, chat safety, emergency links, prevention/facility lookup, vitals, mental wellness, progress, health issues, profile scaffolding, and experimental risk scoring.
- `storage/persistence.py` — JSON persistence adapter for reminder records.
- `services/clinical_db_service.py` — SQLite prototype schema/data access; not a cloud or multi-tenant service.
- `services/storage_config.py` — local data directory resolver. Set `SEHAT_DATA_DIR` before startup to move JSON/SQLite data to a disposable or operator-selected directory; default remains repository `data/`. The public demo uses its own temp directory regardless.
- `data/` — bundled catalogs, thresholds, samples, local records, and SQLite DB. Do not commit secrets or real user records.
- `tests/` — unit, safety, API, integration, and legacy UI behavior checks.
- `docs/` — brief, architecture, safety, deployment readiness, feature inventory, test report, UX, research, and handoff material.

### Main request flow

1. Browser/Streamlit collects an image or form input.
2. Image processing validates/normalizes image input; prescription extraction uses Gemini when configured or test/demo mocks where appropriate.
3. Parsed prescription models preserve raw wording, missing fields, and ambiguity rather than silently completing them.
4. The user reviews extracted instructions; reminder service checks required fields/confirmation and conflicts with existing reminders.
5. Local prototype services persist JSON and/or SQLite data under the configured local data directory.
6. The UI renders status and safety notices. In Vercel demo mode, storage is isolated and writes are rejected.

This flow does not imply clinical validation or secure multi-user service.

## 5. Feature inventory (implemented in prototype to varying degrees)

- Prescription image upload, image quality checks/photo guidance, Gemini multimodal extraction, mock/synthetic sample prescriptions, uncertainty/raw text display.
- Hindi plain-language explanation/read-aloud helpers and medicine-reference lookup based on Indian NLEM/Jan Aushadhi-style data.
- Reminder create/update/toggle/delete and mark-taken flows, with required user confirmation, traceability, non-destructive merge, and conflict warnings.
- Constrained prescription Q&A with guardrails against diagnosis and emergency symptom diversion.
- Vitals logging/import samples for blood pressure, oxygen saturation, glucose, and temperature, with prototype range alerts.
- Mental-wellness check-in and Tele-MANAS contact information; observational recovery questionnaire/trend; treatment reaction/issue logging and formatted caregiver/clinician message.
- India-focused emergency dial links and public-health guidance.
- Small facility/chemist/map lookup for supported localities, not a verified nationwide directory.
- Experimental health-complication scoring/trajectory code. It is not a validated predictive model or a clinical risk tool.
- Responsive/PWA assets and multilingual/localization work from earlier commits.
- Local profile and doctor/staff portal scaffolding only; these are not secure account or verified clinician capabilities.

The feature inventory at `docs/FEATURES_AND_RESOURCES_INVENTORY.md` has a broader catalog; its checkmarks should be read as prototype implementation claims, not external validation or production readiness.

## 6. User decisions and project history from the conversation

The design direction shifted over time from Streamlit and a visual reference toward a complete browser-based redesign, with the user explicitly saying to choose a suitable stack and use a relevant, distinctive visual theme. The user asked for functions to work, testing, deployment, a brief document, and GitHub upload. A public demo was discussed, but the safety boundary was clarified and must remain explicit.

The key safety clarification from the user was: Google sign-in is not implemented; doctor profiles are not authenticated or verified; the Vercel demo should be read-only except synthetic prescription examples; do not claim these capabilities work or bypass safety checks; preserve prescription uncertainty and require review before reminders.

Subsequent deployment/data decisions:

1. The user requested interactive accounts. This requires genuine identity and persistence implementation, not just a UI or database.
2. The user requested an app-owned database and separate India/U.S. clinician adapters, but declined connecting an official dataset. No official registry connection exists.
3. The user chose a Vercel database integration, with explicit instruction to ask before provisioning.
4. The user authorized **synthetic staging only** and specified “local indian based,” interpreted as Mumbai, India hosting.
5. Provisioning is still pending Vercel authentication. Nothing was created and no credentials were added.

## 7. Complete committed Git history (chronological)

This list records every commit currently in the repository history as observed on 2026-10-27. Exact file-level diffs are available with `git show <commit>`.

1. `a8814a9` — `feat: complete Sehat Saathi MVP with safety invariants, Gemini extraction, Hindi explanation, and test suite` — initial full application, core services/models/storage, sample prescriptions, safety docs, and tests.
2. `eb65f52` — `docs: add LinkedIn showcase assets and custom skill for project presentation` — project showcase guide and presentation skill.
3. `ff678bc` — `feat: integrate official Indian Healthcare Database (NLEM & Jan Aushadhi standards)` — expanded Indian medicine reference and language support.
4. `5354dde` — `feat: complete accessible rural healthcare requirements (older adults a11y, photo guidance, conflict detection, traceability, WhatsApp caregiver sharing)` — accessibility, review flow, conflict and traceability handling, caregiver share, docs/tests.
5. `630e2d0` — `feat: add environmental health, disease prevention, and nearby clinic/doctor map locator` — prevention guidance and local facility map behavior.
6. `3003de7` — `feat: add nearby medical stores/chemists map locator and safe online ordering guidance` — chemist lookup and purchasing guidance.
7. `eb62617` — `feat: add 1-tap direct emergency calling for Indian national helplines (108, 112, 104, 102)` — emergency contact/link service and safety tests.
8. `916b0c7` — `feat: add treatment health issue recording, severe reaction alerts, and 1-tap doctor notification` — issue model/service and WhatsApp-style notification formatting.
9. `3344f00` — `feat: add periodic health progress questionnaire and recovery tracker` — progress check-in model/service and tests.
10. `2b44d38` — `feat: Add health device vitals import, clinical alerts, and Tele-MANAS mental wellness screening` — vitals and wellness prototype features.
11. `74c2b75` — `feat: Add comprehensive discard features across prescription review, individual medicines, reminders, vitals, and health issues` — discard/recovery flows and tests.
12. `1e22a45` — `docs & data: Gather all data catalogs, clinical thresholds, sample device exports, and features inventory` — catalogs, synthetic device files, thresholds, and inventory.
13. `cff0e53` — `feat: Add ML & DL health complication prediction service, temporal trajectory analysis, UI integration, and 52 passing tests` — experimental risk/trajectory service and tests/docs.
14. `437c76c` — `ui: Overhaul interface for older adults and rural accessibility with visual hub cards, large high-contrast controls, and easy time-of-day medication cards` — older-adult oriented UI adjustment.
15. `289183b` — `feat: Add full cross-platform compatibility for iOS, Android, and Desktop Web with PWA manifest, service worker, and responsive media queries` — PWA assets and responsive behavior.
16. `50cf41f` — `fix: Add PROJECT_ROOT to sys.path in app/main.py and instantiate global services to resolve ModuleNotFoundError` — import/startup fix.
17. `0058309` — `fix: harden runtime execution, resolve paths to project root, and eliminate startup permission errors` — storage paths and startup/runtime adjustments.
18. `ca2f4b3` — `feat: enhance UI/UX with stunning accessible medical aesthetic and multilingual selection (Hindi, English, Hinglish)` — UI and localization expansion.
19. `fb8529a` — `feat: add Google Sign-In, user authentication, clinical relational database, and Doctor & Healthcare Staff treatment portal` — added profile/auth/clinical portal scaffolding. **Despite the commit wording, current source explicitly confirms this is not real Google authentication, verified clinician access, or production authorization.**
20. `4886f15` — `fix: resolve KeyError 'name_en' in emergency helpline bar with defensive dictionary access and bilingual data` — emergency display robustness fix.
21. `2441c09` — `feat: modernize website UX with health at-a-glance stat banner, expanded canvas, and authoritative government compliance footer` — UI information hierarchy/footer and local DB file.
22. `dd0195c` — `feat: redesign UI/UX with Apple Human Interface Guidelines aesthetic and user-friendly interaction design` — major Streamlit visual revision.
23. `df7c538` — `feat(i18n): comprehensive dynamic multilingual localization across all tabs, cards, inputs, and clinical portals` — broader localization implementation and tests.
24. `e810851` — `Initial commit` — preserved initial GitHub repository/license state during repository connection.
25. `27e5fdc` — `feat: redesign Sehat Saathi and add web demo` — new browser-first Starlette app, static UI, Vercel demo isolation, deployment guard, tests, documentation, and redesign.
26. `cffc72f` — `merge: preserve GitHub initial repository commit` — merge preserving the GitHub repository's initial commit.
27. `af1ca2c` — `docs: add Antigravity project handoff prompt` — detailed project analysis/run/test/safety handoff prompt.
28. `e1d302f` — `feat: isolate local prototype data storage` — `SEHAT_DATA_DIR` resolver, wiring into local services, tests, and README/architecture docs.

## 8. Current Git/worktree state

At handoff preparation:

- Current local branch: `master`.
- Remote: `origin` points to the user's GitHub repository above.
- Local `HEAD` and `origin/main` were both observed at `e1d302f` (`feat: isolate local prototype data storage`).
- No source-code edits were pending at the time of inspection.
- The following **existing local data files are modified and uncommitted**. Their contents are deliberately not copied into this document:
  - `data/mental_health_records.json`
  - `data/progress_records.json`
  - `data/saved_schedules.json`
  - `data/sehat_saathi.db`
  - `data/treatment_issues.json`
- Treat these as user/local records. Do not reset, overwrite, stage, commit, or inspect their contents unless specifically needed and safely authorized. Use a separate `SEHAT_DATA_DIR` for tests.
- The previous source/docs change `e1d302f` is already committed and pushed to `origin/main`.
- Since this context file was first created, the following uncommitted code/test edits were made in response to a report that the main features were not working:
  - `webapp/main.py` — custom reminder times now require unique, valid 24-hour `HH:MM` values; malformed, duplicate, and empty schedules return HTTP 422 instead of allowing an invalid time to become an HTTP 500.
  - `webapp/static/app.js` — a live scan without `GEMINI_API_KEY` now explains that model setup is missing and offers a synthetic sample locally. It does not invent medicines or claim the scan worked.
  - `models/reminder.py`, `services/reminder_service.py` — added the date an explicit “taken” action occurred; old taken flags reset on the next local calendar day, and reminder due windows now work across midnight and ignore paused reminders.
  - `services/device_data_service.py`, `webapp/main.py` — validate known vital formats and units, return 422 for malformed values rather than recording them as normal, and mark unsupported measurements as not assessed.
  - `app/main.py` — added stable `emg_call_<number>` keys to the Streamlit emergency call links.
  - `tests/test_webapp.py`, `tests/test_reminders.py`, `tests/test_vitals_and_mental_health.py` — added end-to-end synthetic prescription/reminder, invalid time, no-key scan, daily taken reset, midnight due window, and vital validation coverage.
- The source/test/document changes belong in Git; the five existing local data files remain local-only and were not modified by these checks.

## 9. Validation evidence and known failure

Earlier validation in the work immediately preceding this handoff was:

- Focused command: `pytest -q tests/test_storage_config.py tests/test_webapp.py tests/test_clinical_database_and_auth.py` — **25 passed**.
- Full suite with isolated storage: `SEHAT_DATA_DIR=/tmp/sehat-saathi-workable-tests pytest -q` — **99 passed, 10 failed**. The failures were legacy Streamlit `AppTest` navigation compatibility assumptions: one expected iterable `ButtonGroup` value but received an integer; others called a missing `AppTest.segmented_control`. Do not report the whole suite as passing.
- Local browser app smoke check: Uvicorn started bound to `127.0.0.1:8765` with `SEHAT_DATA_DIR=/tmp/sehat-saathi-local-smoke`; `/`, `/api/health`, `/api/overview`, and browser JS asset returned HTTP 200; server was stopped afterward.
- Earlier test reports in `docs/TEST_REPORT.md` are historical and do not supersede the above latest run. They describe prototype-level tests, not clinical validation or acceptance for deployment.

Latest validation after the full local workflow audit (2026-10-27):

- Full suite: `SEHAT_DATA_DIR=/tmp/sehat-saathi-main-func-audit .venv/bin/pytest -q` — **116 passed**, with one Starlette/httpx deprecation warning.
- Focused webapp, emergency link, vital, and reminder checks — **31 passed** in the most recent focused run.
- `node --check webapp/static/app.js` and `.venv/bin/python -m compileall -q webapp services app/main.py` — passed.
- End-to-end tests load a synthetic clear sample, explicitly confirm its legible once-daily medicine, save a reminder, and verify the reminder appears in overview. Reminder tests also verify 24-hour reset and due-time behavior across midnight.
- Vitals tests verify invalid readings and mismatched units are rejected rather than stored with a normal status. Unsupported measurements are stored as not assessed.
- A live Gemini request was not made. The test verifies that when the key is absent the API returns no parsed medicines and reports the missing key; configure a valid `GEMINI_API_KEY` locally for real image extraction.
- The local Uvicorn browser smoke test could not be repeated in this execution environment because binding to `127.0.0.1:8765` was denied (`Operation not permitted`). Starlette `TestClient` covered the API routes and the static JavaScript passed syntax validation.

## 10. Local development

Use a Python virtual environment and only synthetic input. The recommended browser app is:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
SEHAT_DATA_DIR=/tmp/sehat-saathi-local-data uvicorn webapp.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. The API health check is `/api/health`. For tests, use `SEHAT_DATA_DIR` pointing to a disposable directory. Gemini extraction requires a configured `GEMINI_API_KEY`; keep it in local environment configuration and never put it in Git or chat. Review `README.md`, `.env.example`, and `docs/ANTIGRAVITY_MASTER_PROMPT.md` before changing the setup.

Do not set production mode to bypass its startup guard. Do not expose the local server to a network without designing and implementing access controls.

## 11. Outstanding work and decision gates

### Immediate staging database task

1. User has authorized only synthetic staging with an India/Mumbai region.
2. Vercel integration setup requires an authenticated Vercel browser session. The marketplace page showed Install redirecting to Vercel login; the Vercel CLI was not installed in the environment at the time.
3. No Supabase project, Vercel Marketplace resource, or environment variable was created. No billing or provider authorization occurred.
4. After the user signs in, provision only the approved free/synthetic staging resource if region and billing screen match that scope. Stop and ask if the provider requires a paid plan, unexpected spend, broader account permissions, or terms beyond the user's approval.
5. Verify selected project is Mumbai (`ap-south-1`), connect only the intended Vercel project, and do not paste secrets into chat. Keep real health data and real users out.
6. Even after provisioning, the app still needs a deliberate database adapter, schema/migrations, server-side access policy, proper auth, tenant isolation, and automated tests before any app workflow can use the database.
7. The public Vercel demo is expected to reject reminder writes; local synthetic reminder creation is covered by the API tests. The synthetic “clear” prescription has a once-daily Pan-D sample and an as-needed Dolo sample. The latter is correctly refused as a fixed-time reminder because the current reminder model cannot safely represent PRN use.

### Larger product work before any real-world pilot

- Implement and security-review real identity/session management; clearly separate patient, caregiver, clinician, and operator roles.
- Establish consent, data ownership, access boundaries, revocation, retention/deletion, audit, encryption, secrets/key management, backups, disaster recovery, monitoring, and incident response.
- Build a secure persistence layer and migrations; prove tenant isolation and least privilege.
- Design manual clinician application review and separately approved country-specific credential verification adapters. Until credentials are actually verified, display pending/unverified status.
- Get clinical owner review, intended-use definition, risk analysis, clinical validation, language/accessibility testing, and independent security/privacy/legal review in each jurisdiction.
- Replace demo facility/emergency configuration with approved, maintained sources and service operations for the intended geography.
- Evaluate the ten legacy UI tests and fix application/test harness mismatches without weakening tests just to achieve green status.

## 12. Core project instructions for a new contributor

- Read this file, `README.md`, `docs/DEPLOYMENT_READINESS.md`, `docs/MEDICAL_SAFETY.md`, and `docs/ANTIGRAVITY_MASTER_PROMPT.md` first.
- Check `git status` before work. Protect the five uncommitted data files listed above.
- Never claim Google sign-in, verified doctor access, official registry connectivity, real database-backed accounts, clinical validity, U.S. coverage, or production readiness unless implemented and independently evidenced.
- Preserve prescription uncertainty and explicit human confirmation before creating a reminder.
- Use synthetic records and isolated storage for manual tests.
- Do not commit `.env`, credentials, local DBs, or user/health records.
- Report commands and results accurately, including failures.

---

**End of consolidated context.** For exact line-by-line source changes, inspect the commit history listed above with `git show`; this document is a human-readable full handoff, not a replacement for version-control diffs.
