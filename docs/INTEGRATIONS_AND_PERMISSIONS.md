# Integrations and Permissions Matrix

**Project:** Sehat Saathi (सेहत साथी)  
**Date Checked:** 2026-10-26  
**Environment:** macOS (Darwin), Python 3.13.7, Antigravity Agent Runtime

---

## 1. Discovered Integrations & Tools

| Integration / Tool | Category | Installed / Available | Status / Authentication | Required Permissions | Expected Benefit | Risks & Mitigations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Local Terminal (`run_command`)** | Dev Tool | Yes | Standard Sandbox Mode (BypassSandbox=false) | Workspace read/write, process execution | Run tests (`pytest`), local server (`streamlit`), pip installs | Keep sandbox active; avoid modifying external OS files |
| **Workspace File Tools** (`read_file`, `write_file`, `edit_file`) | Dev Tool | Yes | Connected | Project directory read/write | Code generation, configuration, documentation | Scope restricted to `/Users/aryansharma/Downloads/Sehat Saathi` |
| **Gemini API Docs MCP** (`gemini-api_gemini-api-docs`) | MCP Server | Yes (Eager) | Connected | Read-only documentation access | Real-time verification of Google GenAI SDK methods and schemas | Zero risk, purely documentation |
| **Google GenAI SDK (`google-genai`)** | AI Library | Installable via pip | Configured via `GEMINI_API_KEY` in `.env` | Network access to Gemini endpoints | Multimodal extraction, structured JSON output, safe explanation | Secrets stored in `.env` (gitignored); never send real patient data |
| **Web Search (`search_web`)** | Research Tool | Yes | Connected | Read-only external search | API status checks, repository comparison, drug database research | Non-sensitive queries only |
| **Subagent Framework** (`invoke_subagent`, `define_subagent`) | Multi-agent | Yes | Connected | In-session communication | Parallel research and isolated testing | Tasks coordinated via central architecture files |
| **Data Agent Kit & Biomolecular MCPs** | Plugin MCPs | Yes (Lazy) | Connected | Data exploration / visualization | Not required for core MVP scope | Out of scope for prescription reader MVP |

---

## 2. Permission Policy & Boundaries

### Permitted Workflow (Autonomous)
- Read and edit files within `/Users/aryansharma/Downloads/Sehat Saathi/`.
- Run sandboxed terminal commands: `pytest`, virtual environment management, package checks.
- Read official public documentation via MCP or web search.
- Create local mock test fixtures and synthetic prescription images.
- Manage local git commits and branches.

### Boundaries Requiring User Approval
- Executing commands requiring `BypassSandbox: true` (e.g. system-level installations or unsandboxed network daemons).
- Modifying files outside the workspace directory.
- Accessing or transmitting sensitive production patient records (strictly forbidden; synthetic data only).
- Enabling paid cloud services or generating billable external infrastructure.

---

## 3. Secret Management Protocol
- `.env` contains local environment variables and is strictly excluded via `.gitignore`.
- `.env.example` provides non-sensitive template placeholders (`GEMINI_API_KEY=your_gemini_api_key_here`).
- No raw API keys, tokens, or personal identifiers are written to log files, console output, or git commits.
- Application handles missing API keys gracefully with setup guidance rather than crashing.
