import re
import requests
import os
from pypdf import PdfReader


def extract_pdf_intelligence(pdf_file_or_path) -> dict:
    """
    Universal PDF extractor:
    Works on both structured compliance certificates AND arbitrary unstructured PDFs
    by combining header parsing with universal regex & keyword classification.
    """
    reader = PdfReader(pdf_file_or_path)
    raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
    upper_text = raw_text.upper()

    def grab_header(label):
        m = re.search(rf"{label}:\s*(.+)", raw_text)
        return m.group(1).strip() if m else None

    # Universal Regex Scanners for arbitrary uploaded PDFs
    tax_match = re.search(
        r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}|[0-9]{2}-[0-9]{7}|GB[0-9]{9})\b",
        upper_text
    )
    bank_match = re.search(
        r"\b([A-Z]{4}0[A-Z0-9]{6}|ABA-[0-9]{9}|GB[0-9]{2}[A-Z]{4}[0-9]{14})\b",
        upper_text
    )

    # Dynamic Document Classification
    doc_type = grab_header("DOCUMENT CLASSIFICATION")
    if not doc_type:
        if any(w in upper_text for w in ["QUOTATION", "BROCHURE", "CATALOG", "PROFORMA", "PRICE LIST"]):
            doc_type = "SALES_BROCHURE_AND_QUOTATION"
        elif any(w in upper_text for w in ["GST", "W-9", "TAX", "EIN", "VAT", "IFSC", "IBAN", "CHEQUE", "BANK"]):
            doc_type = "TAX_AND_BANK_COMPLIANCE_PACKET"
        else:
            doc_type = "UNVERIFIED_EXTERNAL_PDF"

    # Dynamic DBA / Trade Name Detection
    dba_clause = grab_header("DBA / TRADE NAME ENDORSEMENT")
    if not dba_clause:
        dba_search = re.search(r"([^\n.]*\b(?:DBA|DOING BUSINESS AS|TRADE NAME)\b[^\n.]*)", raw_text, re.IGNORECASE)
        dba_clause = dba_search.group(1).strip() if dba_search else "None"

    certified_tax = grab_header("CERTIFIED TAX REGISTRATION ID")
    if not certified_tax or certified_tax == "UNKNOWN":
        certified_tax = tax_match.group(1) if tax_match else "NOT_PROVIDED_IN_DOCUMENT"

    bank_code = grab_header("BANK ROUTING / IFSC / IBAN")
    if not bank_code or bank_code == "UNKNOWN":
        bank_code = bank_match.group(1) if bank_match else "NOT_PROVIDED_IN_DOCUMENT"

    return {
        "char_count": len(raw_text),
        "raw_text_preview": raw_text[:600] + ("..." if len(raw_text) > 600 else ""),
        "doc_type": doc_type,
        "certified_entity": grab_header("CERTIFIED LEGAL ENTITY") or "Extracted via Document Body",
        "dba_clause": dba_clause,
        "certified_tax_id": certified_tax,
        "registered_state": grab_header("REGISTERED JURISDICTION") or "Scanned from Text",
        "bank_beneficiary": grab_header("BANK ACCOUNT BENEFICIARY") or "Extracted via Document Body",
        "bank_code": bank_code,
        "bank_status": grab_header("BANK ACCOUNT VERIFICATION STATUS") or (
            "VERIFIED_ROUTING_FOUND" if bank_code != "NOT_PROVIDED_IN_DOCUMENT" else "MISSING_BANK_PROOF"
        )
    }


def synthesize_vendor_communication(
    vendor_data: dict,
    final_status: str,
    critical_errors: list,
    pending_items: list,
    ai_mode: str = "Deterministic Engine (Instant)",
    api_key: str = "",
) -> tuple[str, str]:
    """
    Generates an actionable vendor email communicating exact missing/mismatched items.
    Returns (email_body, generation_source_label).
    """
    contact_person = vendor_data.get("contact_name") or "Vendor Finance & Compliance Team"
    v_name = vendor_data.get("vendor_name") or "Unnamed Vendor"
    v_email = vendor_data.get("contact_email") or "vendor-contact@missing-email.com"

    # 1. Deterministic Baseline Draft (Always available, 0ms latency)
    if final_status == "APPROVED":
        acct_tail = str(vendor_data.get("bank_account", "XXXX"))[-4:]
        deterministic_draft = (
            f"To: {v_email}\n"
            f"Subject: [APPROVED] Vendor Onboarding Complete — {v_name}\n\n"
            f"Dear {contact_person},\n\n"
            f"We are pleased to confirm that {v_name} has passed all statutory tax, jurisdiction, document, "
            f"and banking verification controls. Your vendor profile is now ACTIVE in our ERP under "
            f"Tax ID {vendor_data.get('tax_id')} for settlement to account ending in {acct_tail}.\n\n"
            f"Best regards,\nZamp Autonomous Procurement Operations"
        )
    elif final_status == "PENDING":
        action_bullets = "\n".join([f"  • {item}" for item in (pending_items + critical_errors)])
        deterministic_draft = (
            f"To: {v_email}\n"
            f"Subject: [ACTION REQUIRED] Pending Vendor Onboarding — {v_name}\n\n"
            f"Dear {contact_person},\n\n"
            f"Thank you for submitting the onboarding packet for {v_name}. Our automated compliance review "
            f"placed your application in PENDING status because the following items require action:\n\n"
            f"{action_bullets}\n\n"
            f"NEXT STEPS: Please reply with the updated details or upload the corrected statutory documents "
            f"via the onboarding portal to complete your approval.\n\n"
            f"Best regards,\nZamp Autonomous Procurement Operations"
        )
    else:
        reject_bullets = "\n".join([f"  • {item}" for item in (critical_errors + pending_items)])
        deterministic_draft = (
            f"To: {v_email}\n"
            f"Subject: [COMPLIANCE REJECTION] Vendor Onboarding Halted — {v_name}\n\n"
            f"Dear {contact_person},\n\n"
            f"Our automated risk and compliance engine reviewed the onboarding submission for {v_name} "
            f"and could not approve the profile due to critical verification failures:\n\n"
            f"{reject_bullets}\n\n"
            f"Per corporate treasury controls, we cannot onboard vendors with cross-jurisdictional tax mismatches, "
            f"invalid tax IDs, or unverified third-party bank beneficiaries. To appeal, submit a notarized "
            f"corporate treasury attestation.\n\n"
            f"Best regards,\nZamp Risk & Treasury Compliance Desk"
        )

    # 2. Optional AI Enhancement (Ollama qwen2.5:7b or Groq)
    if final_status != "APPROVED":
        findings_text = "; ".join(critical_errors + pending_items)
        prompt = (
            f"You are an enterprise Procurement Compliance Officer at Zamp. Write a clear, professional email "
            f"to '{contact_person}' at '{v_name}' ({v_email}) explaining that their vendor onboarding status is "
            f"{final_status}. Explicitly list every required remediation step from these findings: {findings_text}. "
            f"Keep it under 150 words, include To: and Subject: lines, and output ONLY the email text."
        )

        if ai_mode.startswith("Ollama"):
            model_tag = "qwen2.5:7b"
            try:
                resp = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": model_tag,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.2, "num_predict": 300},
                    },
                    timeout=45,
                )
                if resp.status_code == 200:
                    raw = resp.json().get("response", "")
                    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
                    if len(cleaned) > 60:
                        return cleaned, f"Ollama Local ({model_tag})"
            except Exception as ex:
                return deterministic_draft, f"Deterministic Fallback (Ollama unreachable: {ex})"

        elif ai_mode.startswith("Groq"):
            effective_key = (api_key or "").strip() or os.environ.get("GROQ_API_KEY", "").strip()
            if not effective_key:
                try:
                    import streamlit as st
                    effective_key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
                except Exception:
                    effective_key = ""
            if not effective_key:
                return deterministic_draft, "Deterministic Fallback (GROQ_API_KEY missing)"
            try:
                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {effective_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "qwen/qwen3.8-27b",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "max_tokens": 350,
                    },
                    timeout=30,
                )
                if resp.status_code == 200:
                    text = resp.json()["choices"][0]["message"]["content"].strip()
                    if len(text) > 60:
                        return text, "Groq API (qwen/qwen3.8-27b)"
                return deterministic_draft, f"Deterministic Fallback (Groq HTTP {resp.status_code})"
            except Exception as ex:
                return deterministic_draft, f"Deterministic Fallback (Groq error: {ex})"

    return deterministic_draft, "Deterministic Compliance Template (Zero-Latency Fallback)"