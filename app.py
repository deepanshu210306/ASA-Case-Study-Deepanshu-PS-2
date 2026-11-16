import os
import json
import time
import pandas as pd
import streamlit as st

from config_and_scenarios import (
    PDF_DIR, JSON_DIR, SCENARIOS, generate_sample_assets
)
from audit_db import init_db, fetch_all_runs, clear_all_runs
from verification_engine import run_onboarding_pipeline
import importlib
import theme_styles as _theme_styles
importlib.reload(_theme_styles)
from theme_styles import inject_styles


def _load_dotenv(path: str = ".env") -> None:
    """Load KEY=VALUE pairs from .env into os.environ (does not override existing)."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()

# -------------------------------------------------------------------------
# PAGE SETUP
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="Zamp VendorGuard",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

CHANNEL_DEMO = "Demo scenarios"
CHANNEL_BLANK = "Blank submission form"
CHANNEL_JSON = "JSON + PDF upload"

AI_OPTIONS = [
    "Deterministic Engine (Instant)",
    "Ollama Local (qwen2.5:7b)",
    "Groq API (qwen/qwen3.8-27b)",
]

STATUS_CLASS = {
    "APPROVED": "vg-badge vg-badge--ok",
    "PENDING": "vg-badge vg-badge--warn",
    "REJECTED": "vg-badge vg-badge--bad",
    "PASS": "vg-chip vg-chip--ok",
    "WARN": "vg-chip vg-chip--warn",
    "FAIL": "vg-chip vg-chip--bad",
}


def bootstrap_system():
    generate_sample_assets()
    init_db()
    df = fetch_all_runs()
    if df.empty:
        for _, scen in SCENARIOS.items():
            pdf_path = os.path.join(PDF_DIR, scen["pdf_filename"])
            run_onboarding_pipeline(scen, pdf_path)


def stage_html(stg: dict) -> str:
    status = stg["status"]
    tone = "ok" if status == "PASS" else ("warn" if status == "WARN" else "bad")
    chip = STATUS_CLASS.get(status, "vg-chip")
    return f"""
    <div class="vg-stage vg-stage--{tone}">
      <div class="vg-stage-head">
        <span>Stage {stg['stage_num']} · {stg['stage_name']}</span>
        <span class="{chip}">{status}</span>
      </div>
      <div class="vg-stage-detail">{stg['details']}</div>
    </div>
    """


inject_styles()
bootstrap_system()

# -------------------------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="vg-side-brand">
          <div class="vg-kicker">Zamp · PS-2</div>
          <h2>VendorGuard</h2>
          <p>Submission → verification → decision, with a durable audit trail.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="vg-side-section">
          <div class="vg-section-label">Engine</div>
          <div class="vg-section-title">Communication mode</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    ai_mode = st.selectbox(
        "Communication mode",
        AI_OPTIONS,
        index=0,
        label_visibility="collapsed",
    )
    api_key = ""
    if ai_mode.startswith("Groq"):
        default_env_key = os.environ.get("GROQ_API_KEY", "")
        api_key = st.text_input(
            "Groq API key",
            value=default_env_key,
            type="password",
            placeholder="Paste key from console.groq.com",
            help="Or set GROQ_API_KEY in .env",
        )
        st.caption("Loaded from `.env` when present.")

    animate_pipeline = st.checkbox("Animate stage playback", value=True)

    st.markdown("---")
    st.markdown(
        """
        <div class="vg-side-section">
          <div class="vg-section-label">Fixtures</div>
          <div class="vg-section-title">Sample inputs</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Download PDF / JSON for blank form or JSON upload demos.")
    for _, scen in SCENARIOS.items():
        c_pdf, c_json = st.columns(2)
        pdf_p = os.path.join(PDF_DIR, scen["pdf_filename"])
        json_p = os.path.join(JSON_DIR, scen["json_filename"])
        with c_pdf:
            with open(pdf_p, "rb") as f:
                st.download_button(
                    label=f"{scen['scenario_id']} PDF",
                    data=f,
                    file_name=scen["pdf_filename"],
                    mime="application/pdf",
                    key=f"dl_pdf_{scen['scenario_id']}",
                    use_container_width=True,
                )
        with c_json:
            with open(json_p, "rb") as jf:
                st.download_button(
                    label=f"{scen['scenario_id']} JSON",
                    data=jf,
                    file_name=scen["json_filename"],
                    mime="application/json",
                    key=f"dl_json_{scen['scenario_id']}",
                    use_container_width=True,
                )

    st.markdown("---")
    if st.button("Reset audit database", use_container_width=True):
        clear_all_runs()
        bootstrap_system()
        st.rerun()

# -------------------------------------------------------------------------
# HERO
# -------------------------------------------------------------------------
st.markdown(
    """
    <div class="vg-hero">
      <div class="vg-kicker">Vendor onboarding control plane</div>
      <h1 class="vg-brand">Zamp <em>VendorGuard</em></h1>
      <p>Take a vendor submission, run cross-field compliance checks, and return a clear approved / pending / rejected decision with reasons and remediation.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_live, tab_dash, tab_map = st.tabs([
    "Live verification",
    "Audit history",
    "Process & edge cases",
])

# =========================================================================
# TAB 1: LIVE
# =========================================================================
with tab_live:
    col_form, col_live = st.columns([1.05, 1.2], gap="large")

    with col_form:
        st.markdown(
            """
            <div class="vg-panel">
              <div class="vg-section-label">Input</div>
              <div class="vg-section-title">Vendor submission</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        input_channel = st.radio(
            "Submission channel",
            [CHANNEL_DEMO, CHANNEL_BLANK, CHANNEL_JSON],
            horizontal=True,
        )

        blank_state = {
            "scenario_id": "LIVE-PORTAL",
            "vendor_name": "",
            "country": "India",
            "state": "",
            "address": "",
            "tax_id": "",
            "bank_holder_name": "",
            "bank_routing": "",
            "bank_account": "",
            "contact_name": "",
            "contact_email": "",
            "pdf_filename": None,
        }

        if input_channel == CHANNEL_DEMO:
            chosen_key = st.selectbox("Prepared scenario", list(SCENARIOS.keys()))
            active_data = SCENARIOS[chosen_key]
        elif input_channel == CHANNEL_JSON:
            active_data = blank_state.copy()
            active_data["scenario_id"] = "JSON-UPLOAD"
            uploaded_json = st.file_uploader("Vendor JSON", type=["json"])
            if uploaded_json is not None:
                try:
                    parsed_json = json.load(uploaded_json)
                    active_data.update(parsed_json)
                    st.success(f"Loaded: {active_data.get('vendor_name')}")
                except Exception as ex:
                    st.error(f"Invalid JSON: {ex}")
        else:
            active_data = blank_state

        with st.form("live_vendor_onboarding_form"):
            c1, c2 = st.columns(2)
            countries = ["India", "United States", "United Kingdom"]
            c_idx = countries.index(active_data["country"]) if active_data.get("country") in countries else 0

            with c1:
                f_name = st.text_input("Company legal / trade name *", value=active_data.get("vendor_name", ""))
                f_country = st.selectbox("Registered country *", countries, index=c_idx)
                f_state = st.text_input("State / province *", value=active_data.get("state", ""))
                f_tax = st.text_input("Tax ID (GSTIN / EIN / VAT) *", value=active_data.get("tax_id", ""))
            with c2:
                f_bank_holder = st.text_input("Bank beneficiary name *", value=active_data.get("bank_holder_name", ""))
                f_routing = st.text_input("Routing (IFSC / ABA / IBAN) *", value=active_data.get("bank_routing", ""))
                f_account = st.text_input("Bank account number *", value=active_data.get("bank_account", ""))
                f_contact = st.text_input("Compliance contact *", value=active_data.get("contact_name", ""))

            f_email = st.text_input("Contact email *", value=active_data.get("contact_email", ""))
            f_address = st.text_input("Registered address", value=active_data.get("address", ""))

            pdf_hint = (
                f"Optional — scenario PDF `{active_data['pdf_filename']}` will be used if empty"
                if active_data.get("pdf_filename")
                else "Required for blank / JSON submissions"
            )
            uploaded_pdf = st.file_uploader(f"Compliance PDF · {pdf_hint}", type=["pdf"])
            execute_btn = st.form_submit_button("Run onboarding pipeline", use_container_width=True)

    with col_live:
        st.markdown(
            """
            <div class="vg-panel vg-panel--delay">
              <div class="vg-section-label">Output</div>
              <div class="vg-section-title">Decision & stage trace</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if execute_btn:
            if uploaded_pdf is None and not active_data.get("pdf_filename"):
                st.error("Attach a compliance PDF before running verification.")
                st.stop()

            submission_payload = {
                "scenario_id": active_data.get("scenario_id", "LIVE"),
                "vendor_name": f_name,
                "country": f_country,
                "state": f_state,
                "address": f_address,
                "tax_id": f_tax,
                "bank_holder_name": f_bank_holder,
                "bank_routing": f_routing,
                "bank_account": f_account,
                "contact_name": f_contact,
                "contact_email": f_email,
            }
            pdf_target = (
                uploaded_pdf
                if uploaded_pdf is not None
                else os.path.join(PDF_DIR, active_data["pdf_filename"])
            )

            result = run_onboarding_pipeline(
                submission_payload, pdf_target, ai_mode=ai_mode, api_key=api_key
            )

            with st.status("Running 5-stage pipeline…", expanded=True) as status_box:
                for stg in result["stages"]:
                    st.markdown(stage_html(stg), unsafe_allow_html=True)
                    if animate_pipeline:
                        time.sleep(0.28)
                status_box.update(
                    label=f"Complete · {result['processing_ms']} ms · {result['final_status']}",
                    state="complete",
                    expanded=True,
                )

            badge = STATUS_CLASS.get(result["final_status"], "vg-badge")
            st.markdown(
                f"""
                <div class="vg-metric-grid">
                  <div class="vg-metric">
                    <span>Final status</span>
                    <span class="{badge}">{result['final_status']}</span>
                  </div>
                  <div class="vg-metric">
                    <span>Risk score</span>
                    <strong>{result['risk_score']} / 100</strong>
                  </div>
                  <div class="vg-metric">
                    <span>Audit run</span>
                    <strong style="font-size:0.95rem;">{result['run_id']}</strong>
                  </div>
                </div>
                <div class="vg-summary"><b>Decision summary.</b> {result['summary_reason']}</div>
                """,
                unsafe_allow_html=True,
            )

            out_tab1, out_tab2, out_tab3 = st.tabs([
                "Vendor email",
                "Field matrix",
                "PDF extract",
            ])
            with out_tab1:
                st.caption(f"Source · {result['ai_source_used']}")
                st.text_area("Dispatched communication", value=result["email_draft"], height=220)
            with out_tab2:
                st.dataframe(pd.DataFrame(result["field_checks"]), use_container_width=True, hide_index=True)
            with out_tab3:
                st.json(result["pdf_extracted"])
        else:
            st.markdown(
                """
                <div class="vg-empty">
                  <strong>Ready when you are</strong>
                  Choose a scenario on the left and run the pipeline to see status, reasoning, and remediation output here.
                </div>
                """,
                unsafe_allow_html=True,
            )

# =========================================================================
# TAB 2: DASHBOARD
# =========================================================================
with tab_dash:
    st.markdown(
        """
        <div class="vg-panel">
          <div class="vg-section-label">Operations</div>
          <div class="vg-section-title">Audit history</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    df_history = fetch_all_runs()
    n_ok = len(df_history[df_history["final_status"] == "APPROVED"]) if not df_history.empty else 0
    n_pend = len(df_history[df_history["final_status"] == "PENDING"]) if not df_history.empty else 0
    n_bad = len(df_history[df_history["final_status"] == "REJECTED"]) if not df_history.empty else 0

    st.markdown(
        f"""
        <div class="vg-stat-row">
          <div class="vg-stat"><span>Total runs</span><strong>{len(df_history)}</strong></div>
          <div class="vg-stat"><span>Approved</span><strong>{n_ok}</strong><em>ready to pay</em></div>
          <div class="vg-stat"><span>Pending</span><strong>{n_pend}</strong><em>awaiting fix</em></div>
          <div class="vg-stat"><span>Rejected</span><strong>{n_bad}</strong><em>fraud / tax risk</em></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    f_col1, f_col2 = st.columns([3, 1])
    with f_col1:
        status_filter = st.multiselect(
            "Filter by status",
            ["APPROVED", "PENDING", "REJECTED"],
            default=["APPROVED", "PENDING", "REJECTED"],
        )
    with f_col2:
        csv_bytes = df_history.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Export CSV",
            data=csv_bytes,
            file_name="zamp_vendor_onboarding_audit.csv",
            mime="text/csv",
            use_container_width=True,
        )

    filtered_df = df_history[df_history["final_status"].isin(status_filter)] if not df_history.empty else df_history
    st.dataframe(
        filtered_df[[
            "run_id", "timestamp", "scenario_id", "vendor_name",
            "country", "tax_id", "final_status", "risk_score", "summary_reason"
        ]] if not filtered_df.empty else filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("##### Run inspector")
    if not filtered_df.empty:
        chosen_run = st.selectbox(
            "Select run",
            filtered_df["run_id"].tolist(),
            label_visibility="collapsed",
        )
        row = filtered_df[filtered_df["run_id"] == chosen_run].iloc[0]
        ins_left, ins_right = st.columns([1.15, 1])
        with ins_left:
            st.markdown(f"**{row['vendor_name']}** · `{row['run_id']}`")
            for s in json.loads(row["stages_json"]):
                st.markdown(stage_html(s), unsafe_allow_html=True)
            st.markdown("**Field matrix**")
            st.dataframe(
                pd.DataFrame(json.loads(row["field_checks_json"])),
                use_container_width=True,
                hide_index=True,
            )
        with ins_right:
            st.markdown("**Vendor communication**")
            st.code(row["email_draft"], language="text")

# =========================================================================
# TAB 3: PROCESS MAP
# =========================================================================
with tab_map:
    st.markdown(
        """
        <div class="vg-panel">
          <div class="vg-section-label">Architecture</div>
          <div class="vg-section-title">Process map & deliberate edge cases</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.graphviz_chart("""
    digraph VendorOnboarding {
        rankdir=LR;
        bgcolor="transparent";
        node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, color="#E4E7F0", fontcolor="#172033", fillcolor="#FFFFFF"];
        Input [label="Vendor Submission\\nForm / JSON + PDF", fillcolor="#EEF0FF", color="#5B5CE2"];
        S1 [label="Stage 1\\nPDF ingest"];
        S2 [label="Stage 2\\nCompleteness"];
        S3 [label="Stage 3\\nTax & jurisdiction"];
        S4 [label="Stage 4\\nEntity & banking"];
        Approved [label="APPROVED", fillcolor="#ECFDF3", color="#12B76A", fontcolor="#12B76A"];
        Pending [label="PENDING", fillcolor="#FFFAEB", color="#F79009", fontcolor="#F79009"];
        Rejected [label="REJECTED", fillcolor="#FEF3F2", color="#F04438", fontcolor="#F04438"];

        edge [color="#98A2B3", fontcolor="#667085", fontsize=8];
        Input -> S1 -> S2 -> S3 -> S4;
        S2 -> Pending [label="missing / wrong doc"];
        S3 -> Rejected [label="tax spoof"];
        S4 -> Rejected [label="bank fraud"];
        S4 -> Pending [label="DBA review"];
        S4 -> Approved [label="all clear", color="#12B76A"];
    }
    """)

    edges = [
        ("HP-01 Apex", "Happy path", "State, GSTIN prefix, PAN entity type, and domestic IFSC all align.", "APPROVED"),
        ("EC-01 Nimbus", "Cross-field spoofing", "Karnataka address vs Delhi GSTIN; personal PAN in corporate GSTIN; UK IBAN.", "REJECTED"),
        ("EC-02 Stellar", "Payment diversion", "Invalid IRS EIN prefix; corporate vendor pays into a personal account.", "REJECTED"),
        ("EC-03 Horizon", "Incomplete packet", "Missing account + contact; sales brochure attached instead of tax/bank proof.", "PENDING"),
        ("EC-04 Vertex", "DBA nuance", "Trade name ≠ bank holder, bridged by an explicit DBA clause in the PDF.", "PENDING"),
    ]

    rows_html = ['<div class="vg-edge-wrap"><div class="vg-edge-head"><div>Scenario</div><div>Pattern</div><div>Signals</div><div>Decision</div></div>']
    for name, pattern, signals, decision in edges:
        badge = STATUS_CLASS.get(decision, "vg-badge")
        rows_html.append(
            f"""
            <div class="vg-edge">
              <div><strong>{name}</strong></div>
              <div><p>{pattern}</p></div>
              <div><p>{signals}</p></div>
              <div><span class="{badge}">{decision}</span></div>
            </div>
            """
        )
    rows_html.append("</div>")
    st.markdown("".join(rows_html), unsafe_allow_html=True)
