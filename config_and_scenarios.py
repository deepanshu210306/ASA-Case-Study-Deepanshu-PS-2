import os
import json
from fpdf import FPDF

PDF_DIR = "sample_vendor_pdfs"
JSON_DIR = "sample_vendor_jsons"
DB_PATH = "vendor_onboarding_audit.db"

# Indian State to 2-Digit GSTIN Prefix Mapping
INDIA_STATE_CODES = {
    "Delhi": "07",
    "Karnataka": "29",
    "Maharashtra": "27",
    "Tamil Nadu": "33",
    "Gujarat": "24",
    "Uttar Pradesh": "09",
    "Telangana": "36",
    "West Bengal": "19",
    "Haryana": "06"
}

# Country-Specific Tax ID Regex Rules
COUNTRY_TAX_REGEX = {
    "India": (
        r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",
        "15-char GSTIN (2-digit state code + 10-char PAN + entity code + Z + checksum)"
    ),
    "United States": (
        r"^(0[1-6]|1[0-6]|2[0-7]|3[0-9]|4[0-8]|5[0-9]|6[0-8]|7[1-7]|8[0-8]|9[0-589])-[0-9]{7}$",
        "9-digit IRS EIN (XX-XXXXXXX with valid IRS campus prefix)"
    ),
    "United Kingdom": (
        r"^GB[0-9]{9}$",
        "UK VAT Registration (GB + 9 digits)"
    )
}

# Country-Specific Domestic Bank Routing Rules
COUNTRY_BANK_REGEX = {
    "India": (r"^[A-Z]{4}0[A-Z0-9]{6}$", "11-char Indian IFSC (e.g., HDFC0000241)"),
    "United States": (r"^ABA-[0-9]{9}$", "9-digit US ABA Routing (ABA-XXXXXXXXX)"),
    "United Kingdom": (r"^GB[0-9]{2}[A-Z]{4}[0-9]{14}$", "22-char UK IBAN (GBxxXXXX...)")
}

INDIAN_BANK_ACCOUNT_LENGTHS = {
    "HDFC": ([14], "HDFC Bank (strictly 14 digits)"),
    "ICIC": ([12], "ICICI Bank (strictly 12 digits)"),
    "SBIN": ([11, 17], "State Bank of India (11 or 17 digits)"),
    "UTIB": ([15], "Axis Bank (strictly 15 digits)"),
    "KKBK": ([10, 14], "Kotak Mahindra Bank (10 or 14 digits)"),
    "PUNB": ([14, 16], "Punjab National Bank (14 or 16 digits)"),
    "BARB": ([14], "Bank of Baroda (strictly 14 digits)"),
    "CNRB": ([12, 13], "Canara Bank (12 or 13 digits)"),
    "UBIN": ([15], "Union Bank of India (strictly 15 digits)"),
    "IDIB": ([9, 10, 11], "Indian Bank (9 to 11 digits)"),
    "YESB": ([15], "Yes Bank (strictly 15 digits)"),
    "INDB": ([12, 14], "IndusInd Bank (12 or 14 digits)")
}

# 1 Happy Path + 4 Deliberate Edge Cases
SCENARIOS = {
    "HP-01: Apex Industrial Automation (Happy Path — Clean Approval)": {
        "scenario_id": "HP-01",
        "vendor_name": "Apex Industrial Automation Pvt Ltd",
        "country": "India",
        "state": "Maharashtra",
        "address": "Plot 42, MIDC Andheri East, Mumbai, Maharashtra 400093",
        "tax_id": "27AABCA1234F1Z5",
        "bank_holder_name": "Apex Industrial Automation Private Limited",
        "bank_routing": "HDFC0000241",
        "bank_account": "50200048192831",
        "contact_name": "Rajesh Kulkarni",
        "contact_email": "finance@apexautomation.in",
        "pdf_filename": "HP01_Apex_Compliance_Packet.pdf",
        "json_filename": "HP01_Apex_Submission.json",
        "pdf_content": {
            "doc_title": "GOVERNMENT OF INDIA - GST REGISTRATION & BANK VERIFICATION CERTIFICATE",
            "doc_type": "TAX_AND_BANK_COMPLIANCE_PACKET",
            "certified_entity": "Apex Industrial Automation Private Limited",
            "dba_clause": "None",
            "certified_tax_id": "27AABCA1234F1Z5",
            "registered_state": "Maharashtra (State Code: 27)",
            "bank_beneficiary": "Apex Industrial Automation Private Limited",
            "bank_code": "HDFC0000241",
            "bank_status": "ACTIVE CORPORATE CURRENT ACCOUNT - VERIFIED",
            "free_text": (
                "This statutory compliance certificate confirms that Apex Industrial Automation Private Limited "
                "holds active GSTIN 27AABCA1234F1Z5 registered in Maharashtra (State Code 27). "
                "The cancelled cheque confirms corporate account 50200048192831 with IFSC HDFC0000241."
            )
        }
    },
    "EC-01: Nimbus Cloud Logistics (Edge Case 1 — Subtle Cross-Field & PAN/State Spoofing)": {
        "scenario_id": "EC-01",
        "vendor_name": "Nimbus Cloud Logistics Pvt Ltd",
        "country": "India",
        "state": "Karnataka",
        "address": "Tower B, Prestige Tech Park, Outer Ring Road, Bengaluru, Karnataka 560103",
        "tax_id": "07AAAPN9876B1Z2",
        "bank_holder_name": "Nimbus Cloud Logistics Pvt Ltd",
        "bank_routing": "GB29NWBK60161331926819",
        "bank_account": "60161331926819",
        "contact_name": "Vikram Sethi",
        "contact_email": "ap@nimbuslogistics.io",
        "pdf_filename": "EC01_Nimbus_Compliance_Packet.pdf",
        "json_filename": "EC01_Nimbus_Submission.json",
        "pdf_content": {
            "doc_title": "STATUTORY TAX & REMITTANCE DECLARATION",
            "doc_type": "TAX_AND_BANK_COMPLIANCE_PACKET",
            "certified_entity": "Nimbus Cloud Logistics Pvt Ltd",
            "dba_clause": "None",
            "certified_tax_id": "07AAAPN9876B1Z2",
            "registered_state": "Delhi NCR (State Code: 07)",
            "bank_beneficiary": "Nimbus Cloud Logistics Pvt Ltd",
            "bank_code": "GB29NWBK60161331926819",
            "bank_status": "FOREIGN REMITTANCE IBAN ACCOUNT - LONDON UK",
            "free_text": (
                "Surface fields appear complete, but cross-referencing reveals three subtle compliance red flags: "
                "(1) Physical address is Karnataka (Code 29) while GSTIN 07AAAPN9876B1Z2 carries Delhi prefix 07; "
                "(2) The 4th PAN character in the GSTIN is 'P' (Individual/Personal) instead of 'C' (Company); "
                "(3) Settlement is routed to an offshore UK IBAN GB29NWBK60161331926819."
            )
        }
    },
    "EC-02: Stellar Precision Tooling LLC (Edge Case 2 — Beneficiary Fraud & Invalid Country Tax ID)": {
        "scenario_id": "EC-02",
        "vendor_name": "Stellar Precision Tooling LLC",
        "country": "United States",
        "state": "Texas",
        "address": "1400 Congress Ave, Suite 300, Austin, TX 78701",
        "tax_id": "00-1928374",
        "bank_holder_name": "Marcus Vance Personal Holdings",
        "bank_routing": "ABA-111000025",
        "bank_account": "88392019482",
        "contact_name": "Marcus Vance",
        "contact_email": "mvance@stellartooling.com",
        "pdf_filename": "EC02_Stellar_Compliance_Packet.pdf",
        "json_filename": "EC02_Stellar_Submission.json",
        "pdf_content": {
            "doc_title": "IRS FORM W-9 & BANK ACH AUTHORIZATION LETTER",
            "doc_type": "TAX_AND_BANK_COMPLIANCE_PACKET",
            "certified_entity": "Stellar Precision Tooling LLC",
            "dba_clause": "None",
            "certified_tax_id": "00-1928374",
            "registered_state": "Texas, United States",
            "bank_beneficiary": "Marcus Vance Personal Holdings",
            "bank_code": "ABA-111000025",
            "bank_status": "INDIVIDUAL CHECKING ACCOUNT - BANK OF AMERICA",
            "free_text": (
                "Submission claims United States corporate status for Stellar Precision Tooling LLC, "
                "but provides invalid IRS prefix 00-1928374 and directs ACH payments (ABA-111000025) "
                "to an unauthorized personal bank account held by Marcus Vance Personal Holdings."
            )
        }
    },
    "EC-03: Horizon Green Energy (Edge Case 3 — Incomplete Form & Wrong Document Attached)": {
        "scenario_id": "EC-03",
        "vendor_name": "Horizon Green Energy Solutions Pvt Ltd",
        "country": "India",
        "state": "Gujarat",
        "address": "GIDC Industrial Estate, Sanand, Ahmedabad, Gujarat 382110",
        "tax_id": "24AABCH5544E1Z9",
        "bank_holder_name": "Horizon Green Energy Solutions Pvt Ltd",
        "bank_routing": "ICIC0001045",
        "bank_account": "",
        "contact_name": "",
        "contact_email": "billing@horizongreen.in",
        "pdf_filename": "EC03_Horizon_Wrong_Brochure.pdf",
        "json_filename": "EC03_Horizon_Submission.json",
        "pdf_content": {
            "doc_title": "COMMERCIAL SALES QUOTATION & SOLAR PRODUCT CATALOG 2026",
            "doc_type": "SALES_BROCHURE_AND_QUOTATION",
            "certified_entity": "Horizon Green Energy Solutions Pvt Ltd",
            "dba_clause": "None",
            "certified_tax_id": "NOT_PROVIDED_IN_DOCUMENT",
            "registered_state": "Gujarat",
            "bank_beneficiary": "NOT_PROVIDED_IN_DOCUMENT",
            "bank_code": "NOT_PROVIDED_IN_DOCUMENT",
            "bank_status": "COMMERCIAL PRODUCT BROCHURE ONLY",
            "free_text": (
                "PROFORMA QUOTATION: Supply of 500kW Rooftop Solar PV Inverters and Mounting Structures. "
                "Note: Vendor mistakenly attached a sales catalog PDF instead of their GST Registration Certificate "
                "and Cancelled Cheque, and left mandatory bank account and contact name fields blank."
            )
        }
    },
    "EC-04: Vertex Digital Solutions (Edge Case 4 — Legitimate Parent-Subsidiary DBA Nuance)": {
        "scenario_id": "EC-04",
        "vendor_name": "Vertex Digital Solutions",
        "country": "United States",
        "state": "California",
        "address": "450 Mission Street, San Francisco, CA 94105",
        "tax_id": "94-3829104",
        "bank_holder_name": "Vertex Retail Group Inc",
        "bank_routing": "ABA-121000358",
        "bank_account": "44920193841",
        "contact_name": "Elena Rostova",
        "contact_email": "treasury@vertexdigital.com",
        "pdf_filename": "EC04_Vertex_DBA_Packet.pdf",
        "json_filename": "EC04_Vertex_Submission.json",
        "pdf_content": {
            "doc_title": "IRS FORM W-9 & SUBSIDIARY DBA BANK ENDORSEMENT",
            "doc_type": "TAX_AND_BANK_COMPLIANCE_PACKET",
            "certified_entity": "Vertex Retail Group Inc",
            "dba_clause": "Vertex Retail Group Inc operating under registered trade name DBA Vertex Digital Solutions",
            "certified_tax_id": "94-3829104",
            "registered_state": "California, United States",
            "bank_beneficiary": "Vertex Retail Group Inc",
            "bank_code": "ABA-121000358",
            "bank_status": "CORPORATE TREASURY ACCOUNT - PARENT ENTITY",
            "free_text": (
                "IRS W-9 and Bank Certificate issued to parent corporation Vertex Retail Group Inc (EIN 94-3829104, "
                "Routing ABA-121000358) operating under registered trade name DBA Vertex Digital Solutions. "
                "Requires legal treasury sign-off on the parent-subsidiary DBA link before activation."
            )
        }
    }
}


def generate_sample_assets():
    """Creates realistic PDF compliance packets and JSON submission payloads on disk."""
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)

    for _, data in SCENARIOS.items():
        # 1. Generate PDF Packet
        pdf_path = os.path.join(PDF_DIR, data["pdf_filename"])
        if not os.path.exists(pdf_path):
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            c = data["pdf_content"]
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(w=pdf.epw, h=9, text=c["doc_title"], align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
            
            pdf.set_font("Helvetica", "", 10)
            lines = [
                f"DOCUMENT CLASSIFICATION: {c['doc_type']}",
                f"CERTIFIED LEGAL ENTITY: {c['certified_entity']}",
                f"DBA / TRADE NAME ENDORSEMENT: {c['dba_clause']}",
                f"CERTIFIED TAX REGISTRATION ID: {c['certified_tax_id']}",
                f"REGISTERED JURISDICTION: {c['registered_state']}",
                f"BANK ACCOUNT BENEFICIARY: {c['bank_beneficiary']}",
                f"BANK ROUTING / IFSC / IBAN: {c['bank_code']}",
                f"BANK ACCOUNT VERIFICATION STATUS: {c['bank_status']}",
                "",
                "EXTRACTED OCR DOCUMENT BODY:",
                c["free_text"]
            ]
            for line in lines:
                if not line.strip():
                    pdf.ln(6)
                else:
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(w=pdf.epw, h=7, text=line, new_x="LMARGIN", new_y="NEXT")
            pdf.output(pdf_path)

        # 2. Generate Raw JSON Vendor Submission Payload
        json_path = os.path.join(JSON_DIR, data["json_filename"])
        if not os.path.exists(json_path):
            payload = {
                k: data[k] for k in [
                    "scenario_id", "vendor_name", "country", "state", "address",
                    "tax_id", "bank_holder_name", "bank_routing", "bank_account",
                    "contact_name", "contact_email"
                ]
            }
            with open(json_path, "w", encoding="utf-8") as jf:
                json.dump(payload, jf, indent=2)