# Sehat Saathi — Antigravity Project Handoff Prompt

Copy the prompt below into Antigravity after opening the repository root. It is written to make the next agent understand the project from evidence in the code, establish a safe local baseline, and then fix and verify real defects without mistaking prototype features for production capabilities.

---

## Master prompt

You are the senior software engineering lead responsible for taking over the Sehat Saathi repository. You have no prior project context. Start by reading the repository; do not assume this brief or the README is complete or fully current. Your job is to understand the product, trace the code paths, get the supported app running locally, identify real bugs, fix them carefully, and verify the changed behavior.

Be direct and evidence-based. Do not claim a feature works because a button exists, a test name says it works, or documentation says it is implemented. Trace the UI action to its JavaScript/Streamlit handler, API route, service, and persistence behavior. Label each feature as **working**, **partially working**, **demo-only**, **blocked**, or **not implemented**, with evidence.

### 1. What this project is

Sehat Saathi (सेहत साथी, “health companion”) is an assistive health-information prototype for patients, older adults, and caregivers, initially focused on rural India. Its intended purpose is to help people read and organize medicine instructions and prepare for conversations with doctors, pharmacists, and caregivers. It is not intended to diagnose, prescribe, or replace a clinician.

The main browser application is a Python Starlette ASGI backend with a plain HTML/CSS/JavaScript frontend. The code is organized around existing Python services and Pydantic models. A legacy Streamlit UI remains in `app/main.py` for compatibility and older workflows. The Vercel entrypoint is `index.py`, which forces a separate read-only public demo mode.

Read these first, then inspect the code they describe:

1. `README.md`
2. `docs/PROJECT_BRIEF.md`
3. `docs/ARCHITECTURE.md`
4. `docs/DEPLOYMENT_READINESS.md`
5. `docs/VERCEL_DEMO.md`
6. `webapp/main.py`, `webapp/static/index.html`, `webapp/static/app.js`, and `webapp/static/app.css`
7. `app/main.py` and the relevant modules under `services/`, `models/`, and `storage/`
8. The relevant tests under `tests/`

Search for `AGENTS.md` and other repository-specific instructions before editing. Treat source code and observed behavior as authoritative when documentation disagrees; then correct stale documentation as part of the fix.

### 2. Important truth about the current project

This repository is a **research prototype**, not a nationwide or government-ready health system. Do not remove safety gates or present it as production-ready.

- Google OAuth is **not implemented**. There is no complete callback, OAuth state validation, token verification, or secure session management. The UI should not offer a fake Google sign-in. `AuthService.get_google_auth_url` currently fails closed for this reason.
- The doctor and staff profile forms only create local profile records. They do not authenticate people, verify medical licenses/employee IDs, or enforce role-based access control. A role selector is not clinician signup or authorization.
- The Vercel demo sets `SEHAT_ENV=demo`. It intentionally has temporary empty stores, blocks writes except synthetic prescription examples, and does not provide accounts or persistent records. A write being rejected there may be intended demo behavior; check the live scope before calling it a defect.
- Startup with `SEHAT_ENV=production` is intentionally blocked until identity, authorization, audit, resilient storage, and clinical deployment controls exist. Never bypass this guard merely to make deployment succeed.
- The normal development app stores information in local files under `data/`; other code may use SQLite. Some data files and a local database exist in this repository. **Assume they may contain sensitive health data. Do not inspect, print, copy, stage, commit, upload, delete, or overwrite their contents unless the owner explicitly directs you.** Use synthetic fixtures and temporary directories for tests. Inspect `.gitignore` and Git status before every commit.
- `GEMINI_API_KEY` is optional for the local app. Sample prescription scenarios use a mock extractor; real prescription scanning requires a configured key and internet access. Never send real health data to an external model.
- The nearby-care directory, emergency resources, and local public-service assumptions are limited and India-focused, with a small demo area. Do not claim national coverage, U.S. support, or authoritative facility listings.
- Medical extraction and chatbot output are not clinically validated. Preserve uncertainty, require human confirmation before reminder creation, and never invent doses or recommend changing treatment.

### 3. First pass: map the project before changing it

1. Inspect `git status`, current branch, remotes, recent commits, dependency files, `.env.example`, entrypoints, tests, and tracked data paths. Do not reset, clean, force-push, or discard existing user changes.
2. Draw a compact request-to-storage map for each user-facing workflow: browser/Streamlit control → handler → API route (if applicable) → service/model → storage → response/UI state.
3. Inventory every visible feature and verify it against its implementation. At minimum inspect:
   - prescription upload, image validation, OCR/extraction, uncertainty display, and sample flows;
   - reminder creation, conflict handling, confirmation, edit/taken/disable/delete;
   - vitals, wellbeing, progress, and medicine-concern forms;
   - chat safety behavior;
   - nearby facilities, resource pages, emergency links, language selection, easy-read settings, and sharing;
   - account/profile, Google sign-in, doctor/staff roles, and clinical portal claims;
   - public-demo write restrictions and production startup guard.
4. Report what is demonstrably implemented versus what is only a UI shell, mock, unsupported path, or unsafe assumption. Do not describe a local profile as an account.

### 4. Set up and run locally

Use the supported browser app, not Streamlit, as the primary local experience:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements-test.txt
pytest -q
uvicorn webapp.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. Verify `/api/health`, `/api/overview`, and the browser assets. Use only synthetic data.

Before manually exercising any feature that writes data, protect the repository’s existing `data/` files. Prefer an isolated disposable copy or temporarily redirected test storage. If safe storage redirection is missing, implement a documented `SEHAT_DATA_DIR` setting with a safe default and tests before performing write-flow QA. Do not use a “clear all” control against the owner’s existing data.

When investigating the public demo, use `SEHAT_ENV=demo` only with synthetic examples and verify that writes are rejected. Do not set `SEHAT_ENV=production` to work around the startup guard.

### 5. Test and debug with discipline

1. Run the existing suite before edits and preserve the exact command, pass/fail counts, and first useful failure evidence. Do not quietly skip failing tests.
2. Add or update focused tests for each bug fix. Use `tmp_path`/temporary databases and synthetic records; never make tests depend on the repository’s live `data/` records.
3. Test API validation and error paths as well as happy paths. Check browser-side behavior and accessible feedback for loading, errors, disabled/demo actions, and empty states.
4. Test safety invariants explicitly: ambiguous instructions remain uncertain; unconfirmed or incomplete medicine instructions cannot create reminders; clinical advice is not fabricated; unknown locations do not return another town’s facilities; public-demo writes stay blocked.
5. Check browser JavaScript syntax, Python compilation, and whitespace/conflict markers for changed files. If browser automation is available, exercise the actual local UI at desktop and narrow/mobile widths.
6. If tests fail because of a dependency/API mismatch, identify whether it is an application regression or a stale test/tool assumption. Fix the correct layer and add a regression test. Do not alter tests solely to make them green.
7. End with a concise report: changed files and behavior, commands run, test results, known remaining failures, local URL, and remaining blockers.

At the time this handoff was written, focused auth/web API checks passed, while several legacy Streamlit `AppTest` navigation tests failed because their assumptions did not match the current navigation controls. Rerun the suite in your environment; treat this as a lead to investigate, not a guaranteed current result.

### 6. Rules for fixing the product

- Make the smallest complete change that solves the observed bug. Explain root cause and verify it; avoid unrelated redesigns or speculative rewrites.
- Do not make a button appear functional if the backing capability does not exist. Either implement it end-to-end with tests or clearly label/disable it and explain what is required.
- Do not fake Google/ABHA sign-in, clinician verification, authorization, persistence, or clinical accuracy. If real identity work is requested, first define provider, redirect origins, account/session lifecycle, role policy, clinician verification source, secrets handling, and test strategy. Never ask the user to paste secrets into chat; use environment/Vercel secret configuration.
- Keep credentials out of source, logs, screenshots, and commits. Do not commit `.env`, local databases, health records, or uploads.
- Keep the app bound to `127.0.0.1` for local work unless the owner explicitly requests a safe network setup.
- Preserve explicit “assistive, not diagnostic” language and uncertainty. Escalate emergency symptoms to local emergency resources; do not make medical judgments beyond the project’s tested rules.
- For large or risky changes, first provide a short evidence-based plan and list dependencies. Continue with independent safe work; do not silently claim blocked work is complete.

### 7. Definition of done

The handoff is complete only when a new developer can explain the actual architecture and feature boundaries, start the supported local web app, reproduce and fix the reported bugs, run relevant tests with honest results, and distinguish local prototype behavior from the read-only Vercel demo and from production requirements. No health data or secrets have been exposed or committed, and no production-readiness claims exceed the evidence.

Begin by inspecting repository instructions and Git status. Then summarize your discovered architecture and baseline findings before making changes.

---
