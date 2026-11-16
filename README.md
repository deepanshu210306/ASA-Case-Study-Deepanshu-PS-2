# Zamp VendorGuard

Vendor onboarding verification: submission in → **APPROVED / PENDING / REJECTED** out, with reasons and vendor feedback.

## How to run

1. Open a terminal in this project folder.
2. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
pip install pypdf pandas
```

4. (Optional) For Groq-written vendor emails, copy `.env.example` → `.env` and add your key:

```powershell
copy .env.example .env
```

Edit `.env` and set `GROQ_API_KEY=...` from [console.groq.com/keys](https://console.groq.com/keys).

5. Start the app:

```powershell
streamlit run app.py
```

6. In the browser sidebar, pick an engine:

- **Deterministic Engine** — no API / no local LLM needed
- **Ollama Local (qwen2.5:7b)** — requires Ollama running with `qwen2.5:7b`
- **Groq API** — uses `GROQ_API_KEY` from `.env` or the sidebar field

7. Open **Live verification**, choose a demo scenario (e.g. HP-01 or EC-01), then click **Run onboarding pipeline**.

## How the project runs

1. **Input** — A vendor submission enters as a demo scenario, blank form + PDF, or JSON + PDF (company, tax ID, bank details, contact, compliance PDF).

2. **Pipeline** (`verification_engine.py`) runs five stages:
   - **Stage 1** — Parse the PDF and classify the document
   - **Stage 2** — Check required fields and whether the right document type was attached
   - **Stage 3** — Validate tax ID format and cross-check jurisdiction signals (e.g. India state vs GSTIN)
   - **Stage 4** — Match vendor name to bank beneficiary, routing rules, and account format (DBA clause can send a mismatch to PENDING instead of REJECTED)
   - **Stage 5** — Decide status, draft vendor communication, write an audit row to SQLite

3. **Decision** — Critical failures → **REJECTED**; incomplete / wrong doc / DBA review → **PENDING**; otherwise → **APPROVED**. Each run includes a summary reason, field-check matrix, and risk score.

4. **Feedback** — For PENDING/REJECTED, an email draft lists what to fix. That draft is template-based by default, or rewritten by Ollama / Groq if selected.

5. **Audit** — Every run is stored in `vendor_onboarding_audit.db` and shown under **Audit history**. Sample happy-path and edge-case packets live in `sample_vendor_jsons/` and `sample_vendor_pdfs/`.
