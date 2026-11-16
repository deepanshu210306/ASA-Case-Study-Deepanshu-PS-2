# Zamp VendorGuard

Vendor onboarding control plane for **Zamp PS-2**.

Take a vendor submission (form / JSON + compliance PDF) → run deterministic cross-field checks → return a clear **APPROVED**, **PENDING**, or **REJECTED** decision with reasons, remediation, and an audit trail.

---

## How this project works

### End-to-end flow

```
Vendor submission  →  5-stage verification pipeline  →  Decision + email draft  →  SQLite audit log
     (UI / JSON / PDF)         (rules engine)              (APPROVED / PENDING / REJECTED)
```

1. **Input** — Submit via the Streamlit UI using one of:
   - **Demo scenarios** (pre-built happy path + edge cases)
   - **Blank form** + compliance PDF
   - **JSON + PDF** upload

2. **Pipeline** (`verification_engine.py`) runs five stages:

   | Stage | What it does |
   |---|---|
   | **1 · PDF ingest** | Parse the compliance PDF and classify the document type |
   | **2 · Completeness** | Check required fields and whether the right document was attached |
   | **3 · Tax & jurisdiction** | Validate tax ID format and cross-check country / state signals (e.g. India state vs GSTIN prefix) |
   | **4 · Entity & banking** | Match vendor name ↔ bank beneficiary, routing rules, account format; DBA clauses can route mismatches to PENDING |
   | **5 · Decision** | Score risk, finalize status, draft vendor communication, write an audit row |

3. **Decision logic**
   - Critical failures (tax spoof, bank fraud, etc.) → **REJECTED**
   - Incomplete packet / wrong document / DBA review → **PENDING**
   - All checks clear → **APPROVED**

4. **Vendor feedback** — For PENDING / REJECTED, an email draft lists what to fix. By default this is template-based. Optionally, **Ollama** or **Groq** can rewrite the email. Core APPROVED / PENDING / REJECTED decisions do **not** require an LLM.

5. **Audit** — Every run is stored in local SQLite (`vendor_onboarding_audit.db`) and shown under **Audit history**.

### App tabs

| Tab | Purpose |
|---|---|
| **Live verification** | Run the pipeline on a demo / blank / JSON submission and inspect stage output |
| **Audit history** | Browse past runs, filter by status, export CSV, inspect stages & emails |
| **Process & edge cases** | Process map + deliberate edge-case catalogue |

### Project structure

| File / folder | Role |
|---|---|
| `app.py` | Streamlit UI |
| `theme_styles.py` | Light Indigo SaaS design system |
| `verification_engine.py` | 5-stage rule engine + decision synthesis |
| `pdf_and_ai_extractor.py` | PDF parsing + optional LLM email rewrite |
| `audit_db.py` | SQLite create / insert / fetch / clear |
| `config_and_scenarios.py` | Paths, tax/bank regexes, demo scenarios |
| `sample_vendor_jsons/` | Sample vendor JSON fixtures |
| `sample_vendor_pdfs/` | Sample compliance PDFs |
| `vendor_onboarding_audit.db` | Local audit database (created on first run) |
| `.streamlit/config.toml` | Streamlit light theme tokens |
| `.env.example` | Template for optional `GROQ_API_KEY` |

### Demo scenarios (seeded on first launch)

- **HP-01 Apex** — Happy path → APPROVED  
- **EC-01 Nimbus** — Cross-field tax / bank spoofing → REJECTED  
- **EC-02 Stellar** — Payment diversion / EIN issues → REJECTED  
- **EC-03 Horizon** — Incomplete packet / wrong attachment → PENDING  
- **EC-04 Vertex** — Trade name ≠ bank holder with DBA clause → PENDING  

---

## How to run (after downloading)

### Prerequisites

- **Python 3.10+** recommended  
- Windows, macOS, or Linux  

### 1. Open the project folder

```powershell
cd path\to\zamp_vendor_onboarding-main
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. (Optional) Groq API key for LLM email drafts

Only needed if you select **Groq API** in the sidebar.

```powershell
copy .env.example .env
```

Edit `.env` and set:

```env
GROQ_API_KEY=gsk_your_key_here
```

Get a free key at [console.groq.com/keys](https://console.groq.com/keys).

> Do not commit `.env`. It is listed in `.gitignore`.

### 5. Start the app

```powershell
streamlit run app.py
```

Your browser should open to `http://localhost:8501`.

### 6. Try a first run

1. In the sidebar, leave **Communication mode** on **Deterministic Engine (Instant)** (no API key needed).  
2. Open **Live verification**.  
3. Keep **Demo scenarios** selected and pick **HP-01** or **EC-01**.  
4. Click **Run onboarding pipeline**.  
5. Inspect status, stage trace, email draft, and then check **Audit history**.

### Communication modes

| Mode | Requirements |
|---|---|
| **Deterministic Engine (Instant)** | None — recommended default |
| **Ollama Local (qwen2.5:7b)** | [Ollama](https://ollama.com) installed + `ollama pull qwen2.5:7b` |
| **Groq API** | `GROQ_API_KEY` in `.env` or pasted in the sidebar |

---

## Database notes

- Engine: **SQLite** (file-based), no external DB server  
- File: `vendor_onboarding_audit.db` in the project root  
- Table: `onboarding_runs` — one row per pipeline execution  
- Sidebar **Reset audit database** clears history and re-seeds demo runs  

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `streamlit` not found | Activate `.venv`, then `pip install -r requirements.txt` |
| Port already in use | `streamlit run app.py --server.port 8502` |
| Groq emails fail | Check `GROQ_API_KEY` in `.env`, or switch back to Deterministic Engine |
| Ollama mode fails | Ensure Ollama is running and `qwen2.5:7b` is pulled |
| UI looks like an old theme | Hard refresh the browser (**Ctrl+F5**) |

---

## License / assignment

Built for the **Zamp ASA Case Study — PS-2 (Vendor Onboarding)**.
