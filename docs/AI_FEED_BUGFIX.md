# Sehat Saathi — AI feed for bugfix and UI repair

**Use this file as context for another coding agent.** Paste the “Prompt to paste” section plus this file (or the whole repo). Work **one bug at a time**. Confirm in the browser before moving to the next item. Use **synthetic data only**. Do not invent medicine names, doses, times, or durations.

**Date:** 2026-10-27  
**Repo:** local workspace `sehat-saathi` (GitHub: `Aryansharma906/Sehat-Saathi`)  
**Primary UI:** browser app (`webapp/`), not Streamlit (`app/main.py` is legacy)

---

## Prompt to paste into another AI

```
You are fixing the Sehat Saathi local browser app (Starlette + webapp/static).

Goal: find and fix real user-facing bugs, starting with My medicines → Change time, which is reported as missing/glitchy/not working. Then test other flows one by one: prescription demo save, mark taken, pause/remove, share schedule, vitals, wellness, nearby GPS/manual search, Ask Saathi.

Constraints:
- Synthetic data only. Never invent prescription fields.
- Reminders only after user confirmation.
- Do not commit local data files under data/*.json or sehat_saathi.db.
- Do not weaken medical safety (no silent dose guesses, no PRN fixed-time reminders).
- Primary files: webapp/static/app.js, webapp/static/app.css, webapp/static/index.html, webapp/main.py.
- Run locally: SEHAT_DATA_DIR=/tmp/sehat-saathi-local-data .venv/bin/uvicorn webapp.main:app --host 127.0.0.1 --port 8000
- Open http://127.0.0.1:8000
- Create a reminder via Prescription reader → “Try a clear example” → confirm checkbox → Confirm & set reminder (not as-needed/SOS medicines).
- Then fix Change time so the picker is visible, usable, and saves HH:MM.

Known likely causes for Change time (code review, not yet proven in browser logs):
1) CSS: .time-edit and .mini-action are 8–9px; reminder-card grid is 45px 1fr auto so actions can clip off-screen.
2) <input type="time"> may emit HH:MM:SS; API regex is only HH:MM → HTTP 422.
3) init() calls detectCurrentLocation({silent:true}) which later calls refresh() → renderOverview() → innerHTML rebuild, destroying the open time picker.
4) Saving time calls renderOverview() which also re-renders the home list; go("medicines") also re-renders medicines.

Fix the time-change UX first (visible control, valid payload, no mid-edit DOM wipe). Keep instrumentation in app.js if present (#region agent log) until the user confirms. Then continue to the next broken flow.

Also read docs/AI_FEED_BUGFIX.md in the repo for the full worklist.
```

---

## How to run

```bash
cd /path/to/sehat-saathi
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
SEHAT_DATA_DIR=/tmp/sehat-saathi-local-data uvicorn webapp.main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. Health: `GET /api/overview`.

Demo prescription (no Gemini key): **Prescription reader → Try a clear example**. Confirm fields + checkbox → **Confirm & set reminder**. SOS/as-needed meds are correctly refused as fixed-time reminders.

---

## User report (raw)

> Some of the functionalities are not working properly. Like medicine tracker time change option is not there, it is glitchy and not working properly. This is just one problem. We need to use it and figure out the bugs and errors, what can be added more. Test and rerun the cases. Breakdown the problems and work on every aspect one by one.

---

## Work order (do in this sequence)

| # | Area | User-visible symptom | Status |
|---|------|----------------------|--------|
| 1 | My medicines — change time | Control missing / tiny / glitchy; save may fail | **IN PROGRESS** — instrumented, not runtime-proven |
| 2 | My medicines — actions | Taken / Pause / Remove / empty state | Not tested this session |
| 3 | Overview today’s list | Mark taken; count vs medicines page | Not tested |
| 4 | Prescription scan + demo | Scan without key; confirm/save; conflicts | Partial prior work exists |
| 5 | Share with family | WhatsApp share + confirm dialog | Not tested |
| 6 | Health & wellbeing | Vitals / wellness / progress / issue forms | Not tested |
| 7 | Care nearby | GPS vs manual locality; maps links | Not tested |
| 8 | Ask Saathi | Symptom information, follow-up questions, urgent warning signs | Tested in chat service and API suites |
| 9 | Accessibility | Easy-read, 8px fonts, tap targets for older adults | Likely needed after #1 |
| 10 | Additions | Only after bugs: larger time picker, per-dose times, Hindi labels | Do not add features until #1–8 are stable |

---

## Bug 1 — Medicine tracker time change (highest priority)

### Expected

On **My medicines**, each reminder shows a **Change time** control and **Save time**. User picks a time, saves, toast confirms, displayed time updates, `/api/reminders/{id}/time` persists `HH:MM`.

### Reported

Time change option “is not there”, “glitchy”, “not working”.

### Implementation today

- Render: `webapp/static/app.js` → `renderMedicines()`
- Save: `changeReminderTime(id)` → `POST /api/reminders/{id}/time` `{ time }`
- API: `webapp/main.py` `reminder_action` action `"time"`; regex `r"(?:[01]\d|2[0-3]):[0-5]\d"`
- Styles: `webapp/static/app.css` `.reminder-card`, `.reminder-actions`, `.time-edit`, `.mini-action`

### Hypotheses (test before locking a fix)

**A — Hidden / unusable UI**  
`.time-edit { font-size: 8px }` and `.mini-action { font-size: 8px }`. Card grid `45px 1fr auto` packs five buttons + time input in the third column. On medium widths the time row can wrap, clip, or look like it is missing. Mobile override puts actions on a second row (`grid-column: 1 / -1`) but type=time native chrome is still tiny.

**B — Invalid native time value**  
`<input type="time" value="${reminder_time}">`. If stored value is empty or not `HH:MM`, some browsers show a blank/broken picker (`validity.badInput`).

**C — Save payload rejected**  
Chrome/Safari `input type="time"` can yield `19:30:00`. API `fullmatch` on `HH:MM` only → 422 “Choose a valid time in 24-hour format.” User sees a failed/glitchy save.

**D — Field not found**  
Lookup is `dataset.timeFor === id`. Unlikely for UUID ids unless encoding mismatch.

**E — DOM wipe while picker is open (strong “glitchy” candidate)**  
`init()` → `detectCurrentLocation({ silent: true })`. GPS success/fail timeout later calls `refresh()` → `renderOverview()` → `renderMedicines()` which **replaces `#medicine-list` innerHTML**, closing the native time picker and resetting the field. Same wipe happens after any vitals/wellness save if user is on medicines.

**F — Click routing**  
Document-level `[data-view]` / `[data-go]` clicks. Time input should not match those. Double handlers on Save time are possible but secondary.

### Suggested fix shape (apply only after confirming in UI)

1. Make time edit a first-class row: full-width under the card, min-height ~44px, font ≥14px, visible “Change time” label.
2. Normalize posted time: take first 5 chars if `HH:MM:SS`; reject otherwise; optionally accept seconds on the API.
3. Do not rebuild `#medicine-list` while a time input is focused. Stop silent GPS `refresh()` from calling `renderOverview()` when medicines view is active, or skip `renderMedicines()` if `document.activeElement` is a `[data-time-for]` field.
4. After successful save, update that card’s displayed time without a full-page rebuild if possible.

### Current session instrumentation (keep until verified)

Debug `fetch` logs in `webapp/static/app.js` inside `// #region agent log` at:

- `renderMedicines` — input count, values, bounding boxes
- `changeReminderTime` — field, value, HH:MM vs HH:MM:SS
- `changeReminderTime` catch — API error
- `refresh` — when overview rebuilds
- `detectCurrentLocation` GPS success
- document click on time controls

Session ingest is local debug only. Remove regions after the user confirms the time flow.

### Manual repro for Bug 1

1. Start the server as above.
2. Hard-refresh the app.
3. Prescription reader → Try a clear example → check “I checked this information” → Confirm & set reminder (for the once-daily medicine, not SOS).
4. Open **My medicines**.
5. Look for Change time + time input + Save time.
6. Open the picker, change the time, Save time.
7. Confirm toast, displayed time, and that a refresh still shows the new time.

---

## Other likely defects to verify next

1. **Overview vs medicines double render** — `renderOverview()` always calls `renderMedicines()`. `go("medicines")` calls it again. Harmless extra work but contributes to flicker.
2. **Today’s list uses only first 3 active reminders**, not “due today by time”. Empty/wrong slice may look broken.
3. **`isTodayReminder` unused** for the today list (sorted slice of all active instead).
4. **Easy-read is 118%** while many controls stay 8–9px — fails older-adult accessibility.
5. **Ask Saathi prompt cards** are not clickable (static copy).
6. **`#upload-preview` is a span**, JS sets `.src` and `display:block` — preview may not show.
7. **GPS on every load** can fail loudly or rewrite locality to `lat, lon` and confuse nearby search.
8. **Public demo** disables writes; local users may think save is broken if `demo_read_only` is on.
9. **Share schedule** needs an active reminder; empty toast is easy to miss.
10. **Streamlit tests** (`tests/test_ui_and_options_navigation.py`) are legacy; do not treat them as the browser-app spec.

---

## Safety and product rules (do not violate)

- Never guess missing dose/strength/duration/timing.
- Uncertain extraction must stay uncertain.
- No reminder without `user_confirmed`.
- SOS / as-needed must not become a clock reminder.
- Prototype, not a clinical product. No real patient data.
- Do not set `SEHAT_ENV=production` to bypass the startup guard.
- Do not commit `.env`, `data/*` local records, or secrets.

---

## Tests that already cover reminder time API

- `tests/test_webapp.py` — `POST /api/reminders/{id}/time` with `19:30` succeeds; `25:80` is 422.
- Custom create times must be unique valid `HH:MM`.

Add a UI-oriented test only if you normalize `HH:MM:SS` on the server; then assert both formats.

---

## What not to do in the first pass

- Do not rebuild Streamlit.
- Do not add auth, cloud DB, or nationwide facilities.
- Do not restyle the whole app before time-change works.
- Do not remove debug `#region agent log` blocks until time-change is confirmed.
- Do not “fix” PRN medicines by assigning a default clock time.

---

## Definition of done for Bug 1

- Change time is visible on desktop and a ~390px-wide viewport without hunting.
- Native or custom picker can be used without the control vanishing.
- Saved time persists after reload (`SEHAT_DATA_DIR` JSON).
- Invalid time shows a clear toast, not a silent no-op.
- No new medical-safety regressions (`pytest` webapp + reminder tests with `SEHAT_DATA_DIR` temp dir).
