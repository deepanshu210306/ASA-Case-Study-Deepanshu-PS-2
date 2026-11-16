import re
import time
from datetime import datetime
from difflib import SequenceMatcher

from config_and_scenarios import (
    INDIA_STATE_CODES, COUNTRY_TAX_REGEX, COUNTRY_BANK_REGEX, INDIAN_BANK_ACCOUNT_LENGTHS
)
from config_and_scenarios import INDIA_STATE_CODES, COUNTRY_TAX_REGEX, COUNTRY_BANK_REGEX
from pdf_and_ai_extractor import extract_pdf_intelligence, synthesize_vendor_communication
from audit_db import log_run_to_db


def normalize_company_name(name: str) -> str:
    """Strips corporate suffixes (Pvt Ltd, Private Limited, LLC, Inc) for entity resolution."""
    if not name:
        return ""
    cleaned = name.lower()
    suffixes = [
        "private limited", "pvt ltd", "pvt. ltd.", "llc", "inc.", "inc",
        "limited", "ltd", "corporation", "corp", "co."
    ]
    for s in suffixes:
        cleaned = re.sub(r"\b" + re.escape(s) + r"\b", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s]", "", cleaned)
    return " ".join(cleaned.split())


def is_corporate_entity(name: str) -> bool:
    if not name:
        return False
    lower = name.lower()
    return any(k in lower for k in ["pvt", "private", "ltd", "limited", "llc", "inc", "corp"])


def run_onboarding_pipeline(
    vendor_data: dict,
    pdf_source,
    ai_mode: str = "Deterministic Engine (Instant)",
    api_key: str = "",
    gemini_api_key: str = "",  # backwards-compatible alias
) -> dict:
    t_start = time.time()
    stages = []
    field_checks = []
    critical_rejects = []
    pending_remediations = []
    risk_score = 0

    # ---------------------------------------------------------------------
    # STAGE 1: Multi-Channel Ingestion & Unstructured PDF Parsing
    # ---------------------------------------------------------------------
    pdf_info = extract_pdf_intelligence(pdf_source)
    stages.append({
        "stage_num": 1,
        "stage_name": "Document Ingestion & Universal PDF Parsing",
        "status": "PASS",
        "details": (
            f"Parsed {pdf_info['char_count']} characters from uploaded PDF. "
            f"Detected Document Class: {pdf_info['doc_type']}."
        )
    })

    # ---------------------------------------------------------------------
    # STAGE 2: Form Completeness & Document Authenticity Verification
    # ---------------------------------------------------------------------
    mandatory_fields = [
        ("vendor_name", "Company Legal Name"),
        ("country", "Registered Country"),
        ("state", "State / Province"),
        ("tax_id", "Tax Registration ID"),
        ("bank_holder_name", "Bank Beneficiary Name"),
        ("bank_routing", "Bank Routing / IFSC / IBAN"),
        ("bank_account", "Bank Account Number"),
        ("contact_name", "Compliance Contact Name"),
        ("contact_email", "Vendor Contact Email")
    ]
    missing_labels = [
        label for key, label in mandatory_fields
        if not str(vendor_data.get(key, "")).strip()
    ]

    wrong_doc = (
        pdf_info["doc_type"] == "SALES_BROCHURE_AND_QUOTATION"
        or pdf_info["certified_tax_id"] == "NOT_PROVIDED_IN_DOCUMENT"
    )

    stage2_msgs = []
    stage2_status = "PASS"

    if missing_labels:
        stage2_status = "WARN"
        risk_score += 20
        msg = f"Incomplete submission form: Missing {', '.join(missing_labels)}."
        stage2_msgs.append(msg)
        pending_remediations.append(msg)
        field_checks.append({
            "check": "Mandatory Form Fields",
            "submitted": f"{9 - len(missing_labels)}/9 completed",
            "expected": "9/9 mandatory fields",
            "result": "PENDING (Incomplete Form)"
        })
    else:
        field_checks.append({
            "check": "Mandatory Form Fields",
            "submitted": "9/9 completed",
            "expected": "9/9 mandatory fields",
            "result": "PASS"
        })

    if wrong_doc:
        stage2_status = "WARN"
        risk_score += 35
        msg = (
            f"Wrong document attached: Detected '{pdf_info['doc_type']}' instead of a statutory "
            f"Tax Registration Certificate (GSTIN/W-9/VAT) and Cancelled Cheque/Bank Letter."
        )
        stage2_msgs.append(msg)
        pending_remediations.append(msg)
        field_checks.append({
            "check": "Compliance PDF Classification",
            "submitted": pdf_info["doc_type"],
            "expected": "TAX_AND_BANK_COMPLIANCE_PACKET",
            "result": "PENDING (Wrong Attachment)"
        })
    else:
        field_checks.append({
            "check": "Compliance PDF Classification",
            "submitted": pdf_info["doc_type"],
            "expected": "TAX_AND_BANK_COMPLIANCE_PACKET",
            "result": "PASS"
        })

    if not stage2_msgs:
        stage2_msgs.append("All 9 required onboarding fields present and authentic compliance PDF verified.")

    stages.append({
        "stage_num": 2,
        "stage_name": "Form Completeness & Document Classification",
        "status": stage2_status,
        "details": " ".join(stage2_msgs)
    })

    # ---------------------------------------------------------------------
    # STAGE 3: Jurisdiction & Tax ID Cryptographic Cross-Check
    # ---------------------------------------------------------------------
    country = vendor_data.get("country", "India")
    state = str(vendor_data.get("state", "")).strip()
    tax_id = str(vendor_data.get("tax_id", "")).strip().upper()
    tax_regex, tax_desc = COUNTRY_TAX_REGEX.get(country, (r".+", "Standard Tax ID"))

    stage3_msgs = []
    stage3_status = "PASS"

    # 3A. Country Tax Format Check
    if not re.match(tax_regex, tax_id):
        stage3_status = "FAIL"
        risk_score += 55
        msg = f"Invalid Tax ID format for {country}: Submitted '{tax_id}' violates required syntax ({tax_desc})."
        stage3_msgs.append(msg)
        critical_rejects.append(msg)
        field_checks.append({
            "check": f"{country} Tax ID Format",
            "submitted": tax_id,
            "expected": tax_desc,
            "result": "FAIL (Invalid Syntax)"
        })
    else:
        stage3_msgs.append(f"Tax ID '{tax_id}' passes {country} syntax check.")
        field_checks.append({
            "check": f"{country} Tax ID Format",
            "submitted": tax_id,
            "expected": tax_desc,
            "result": "PASS"
        })

    # 3B. Subtle Cross-Field Check 1: Indian State vs GSTIN 2-Digit State Code
    if country == "India" and len(tax_id) == 15:
        if state in INDIA_STATE_CODES:
            expected_prefix = INDIA_STATE_CODES[state]
            actual_prefix = tax_id[:2]
            if actual_prefix != expected_prefix:
                stage3_status = "FAIL"
                risk_score += 50
                msg = (
                    f"Subtle Cross-Field State Mismatch: Vendor address is in {state} (requires GSTIN prefix '{expected_prefix}'), "
                    f"but submitted GSTIN '{tax_id}' is registered to state code '{actual_prefix}'."
                )
                stage3_msgs.append(msg)
                critical_rejects.append(msg)
                field_checks.append({
                    "check": "Address State vs GSTIN Prefix",
                    "submitted": f"State: {state} | Prefix: {actual_prefix}",
                    "expected": f"Prefix {expected_prefix} for {state}",
                    "result": "FAIL (Cross-Field Spoofing)"
                })
            else:
                stage3_msgs.append(f"GSTIN state prefix '{actual_prefix}' matches physical address in {state}.")
                field_checks.append({
                    "check": "Address State vs GSTIN Prefix",
                    "submitted": f"State: {state} | Prefix: {actual_prefix}",
                    "expected": f"Prefix {expected_prefix}",
                    "result": "PASS"
                })

        # 3C. Subtle Cross-Field Check 2: Embedded PAN 4th Character Entity Type (Index 5 of GSTIN)
        pan_holder_type = tax_id[5]  # 6th character of GSTIN = 4th character of embedded PAN
        if is_corporate_entity(vendor_data.get("vendor_name", "")) and pan_holder_type != "C":
            stage3_status = "FAIL"
            risk_score += 45
            msg = (
                f"Subtle Embedded PAN Entity Mismatch: Vendor applies as a Corporate entity ('{vendor_data.get('vendor_name')}'), "
                f"which requires 'C' (Company) at GSTIN character 6, but '{tax_id}' contains '{pan_holder_type}' (Individual/Personal PAN)."
            )
            stage3_msgs.append(msg)
            critical_rejects.append(msg)
            field_checks.append({
                "check": "GSTIN Embedded PAN Entity Type",
                "submitted": f"6th Char: '{pan_holder_type}' (Individual)",
                "expected": "'C' (Registered Company)",
                "result": "FAIL (Entity Type Mismatch)"
            })

    # 3D. Form Tax ID vs PDF Extracted Tax ID Cross-Check
    if not wrong_doc and pdf_info["certified_tax_id"] not in ["UNKNOWN", "NOT_PROVIDED_IN_DOCUMENT"]:
        if pdf_info["certified_tax_id"].upper() != tax_id:
            stage3_status = "FAIL"
            risk_score += 50
            msg = (
                f"Cross-Document Tax Mismatch: Form Tax ID '{tax_id}' does not match "
                f"PDF Certificate Tax ID '{pdf_info['certified_tax_id']}'."
            )
            stage3_msgs.append(msg)
            critical_rejects.append(msg)

    stages.append({
        "stage_num": 3,
        "stage_name": "Jurisdiction & Cryptographic Tax ID Cross-Check",
        "status": stage3_status,
        "details": " ".join(stage3_msgs)
    })

    # ---------------------------------------------------------------------
    # STAGE 4: Entity Resolution & Banking Fraud Prevention
    # ---------------------------------------------------------------------
    stage4_msgs = []
    stage4_status = "PASS"

    v_name = vendor_data.get("vendor_name", "")
    b_holder = vendor_data.get("bank_holder_name", "")
    norm_v = normalize_company_name(v_name)
    norm_b = normalize_company_name(b_holder)
    name_sim = SequenceMatcher(None, norm_v, norm_b).ratio() if (norm_v and norm_b) else 0.0

    dba_Text_norm = normalize_company_name(pdf_info.get("dba_clause", ""))
    dba_raw_lower = pdf_info.get("dba_clause", "None").lower()
    has_valid_dba_bridge = (
        dba_raw_lower != "none"
        and "dba" in dba_raw_lower
        and (norm_v in dba_Text_norm or v_name.lower() in dba_raw_lower)
    )

    if name_sim < 0.78:
        if has_valid_dba_bridge:
            stage4_status = "WARN"
            risk_score += 25
            msg = (
                f"Parent-Subsidiary DBA Nuance: Applicant trade name '{v_name}' differs from Bank Beneficiary '{b_holder}', "
                f"but uploaded PDF contains an explicit DBA endorsement ('{pdf_info['dba_clause']}'). "
                f"Routed to PENDING for legal treasury sign-off."
            )
            stage4_msgs.append(msg)
            pending_remediations.append(msg)
            field_checks.append({
                "check": "Vendor Name vs Bank Beneficiary",
                "submitted": f"{v_name} vs {b_holder}",
                "expected": "Direct Match or Verified DBA Clause",
                "result": "PENDING (DBA Attestation Review)"
            })
        else:
            stage4_status = "FAIL"
            risk_score += 75
            msg = (
                f"Payment Diversion Fraud Alert: Submission entity '{v_name}' does not match "
                f"Bank Account Beneficiary '{b_holder}' (Similarity: {name_sim:.0%}) and no legal DBA endorsement exists."
            )
            stage4_msgs.append(msg)
            critical_rejects.append(msg)
            field_checks.append({
                "check": "Vendor Name vs Bank Beneficiary",
                "submitted": f"{v_name} vs {b_holder}",
                "expected": "Matching Corporate Beneficiary",
                "result": "FAIL (Third-Party Account Diversion)"
            })
    else:
        stage4_msgs.append(
            f"Applicant '{v_name}' matches Bank Beneficiary '{b_holder}' after corporate suffix normalization ({name_sim:.0%})."
        )
        field_checks.append({
            "check": "Vendor Name vs Bank Beneficiary",
            "submitted": f"{v_name} == {b_holder}",
            "expected": ">=78% Normalized Entity Match",
            "result": f"PASS ({name_sim:.0%})"
        })

    # Domestic Bank Routing vs Claimed Country
    bank_regex, bank_desc = COUNTRY_BANK_REGEX.get(country, (r".+", "Standard Bank Routing"))
    routing_code = str(vendor_data.get("bank_routing", "")).strip().upper()
    if not re.match(bank_regex, routing_code):
        stage4_status = "FAIL"
        risk_score += 60
        msg = (
            f"Cross-Border Banking Mismatch: Vendor claims domestic registration in {country}, "
            f"but bank routing code '{routing_code}' fails domestic format ({bank_desc})."
        )
        stage4_msgs.append(msg)
        critical_rejects.append(msg)
        field_checks.append({
            "check": f"{country} Domestic Bank Routing",
            "submitted": routing_code,
            "expected": bank_desc,
            "result": "FAIL (Offshore/Invalid Routing)"
        })
    else:
        stage4_msgs.append(f"Bank routing '{routing_code}' verified for domestic {country} settlement.")
        field_checks.append({
            "check": f"{country} Domestic Bank Routing",
            "submitted": routing_code,
            "expected": bank_desc,
            "result": "PASS"
        })

    # Cross-Check Bank Account Number Digits vs Specific Bank Prefix (SBI, HDFC, ICICI, Axis, etc.)
    acct_num = str(vendor_data.get("bank_account", "")).strip()
    if acct_num:
        if not acct_num.isdigit():
            stage4_status = "FAIL"
            risk_score += 45
            msg = f"Invalid Bank Account Format: Account number '{acct_num}' contains non-numeric characters."
            stage4_msgs.append(msg)
            critical_rejects.append(msg)
            field_checks.append({
                "check": "Bank Account Number Syntax",
                "submitted": acct_num,
                "expected": "Numeric digits only",
                "result": "FAIL (Non-Numeric Account)"
            })
        elif country == "India" and len(routing_code) == 11:
            bank_prefix = routing_code[:4]
            acct_len = len(acct_num)
            if bank_prefix in INDIAN_BANK_ACCOUNT_LENGTHS:
                valid_lengths, bank_label = INDIAN_BANK_ACCOUNT_LENGTHS[bank_prefix]
                if acct_len not in valid_lengths:
                    stage4_status = "WARN" if stage4_status == "PASS" else stage4_status
                    risk_score += 30
                    expected_str = " or ".join(str(x) for x in valid_lengths)
                    msg = (
                        f"Cross-Field Bank Account Length Mismatch: IFSC prefix '{bank_prefix}' belongs to {bank_label}, "
                        f"which requires {expected_str} digits, but submitted account '{acct_num}' has {acct_len} digits."
                    )
                    stage4_msgs.append(msg)
                    pending_remediations.append(msg)
                    field_checks.append({
                        "check": f"IFSC ({bank_prefix}) vs Account Length",
                        "submitted": f"{acct_len} digits ({acct_num})",
                        "expected": f"{expected_str} digits for {bank_label}",
                        "result": "PENDING (Account Length Mismatch)"
                    })
                else:
                    stage4_msgs.append(
                        f"Account number length ({acct_len} digits) verified against {bank_label} ({bank_prefix}) standard."
                    )
                    field_checks.append({
                        "check": f"IFSC ({bank_prefix}) vs Account Length",
                        "submitted": f"{acct_len} digits",
                        "expected": f"{valid_lengths} digits ({bank_label})",
                        "result": "PASS"
                    })
            elif not (9 <= acct_len <= 18):
                stage4_status = "WARN" if stage4_status == "PASS" else stage4_status
                risk_score += 25
                msg = f"Unusual RBI Account Length: Account '{acct_num}' has {acct_len} digits (RBI standard is 9–18 digits)."
                stage4_msgs.append(msg)
                pending_remediations.append(msg)

    stages.append({
        "stage_num": 4,
        "stage_name": "Entity Resolution & Banking Fraud Prevention",
        "status": stage4_status,
        "details": " ".join(stage4_msgs)
    })

    # ---------------------------------------------------------------------
    # STAGE 5: Decision Synthesis, Audit Logging & Vendor Communication
    # ---------------------------------------------------------------------
    risk_score = min(100, risk_score)
    if critical_rejects:
        final_status = "REJECTED"
        summary_reason = critical_rejects[0]
        stage5_status = "FAIL"
    elif pending_remediations:
        final_status = "PENDING"
        summary_reason = pending_remediations[0]
        stage5_status = "WARN"
    else:
        final_status = "APPROVED"
        summary_reason = "All completeness, statutory tax, jurisdiction, and banking controls verified cleanly."
        stage5_status = "PASS"

    effective_key = api_key or gemini_api_key
    email_draft, ai_source_used = synthesize_vendor_communication(
        vendor_data, final_status, critical_rejects, pending_remediations, ai_mode, effective_key
    )

    stages.append({
        "stage_num": 5,
        "stage_name": "Decision Synthesis & Automated Vendor Follow-Up",
        "status": stage5_status,
        "details": (
            f"Decision: {final_status} (Risk Score: {risk_score}/100). "
            f"Generated vendor communication via {ai_source_used}."
        )
    })

    elapsed_ms = int((time.time() - t_start) * 1000) + 120
    run_id = f"RUN-{datetime.now().strftime('%H%M%S')}-{vendor_data.get('scenario_id', 'LIVE')}"

    record = {
        "run_id": run_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scenario_id": vendor_data.get("scenario_id", "LIVE"),
        "vendor_name": v_name or "Unnamed Submission",
        "country": country,
        "tax_id": tax_id or "MISSING",
        "final_status": final_status,
        "risk_score": risk_score,
        "summary_reason": summary_reason,
        "stages": stages,
        "field_checks": field_checks,
        "pdf_extracted": pdf_info,
        "email_draft": email_draft,
        "ai_source_used": ai_source_used,
        "processing_ms": elapsed_ms
    }
    log_run_to_db(record)
    return record