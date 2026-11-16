import json
import sqlite3
import pandas as pd
from config_and_scenarios import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS onboarding_runs (
            run_id TEXT PRIMARY KEY,
            timestamp TEXT,
            scenario_id TEXT,
            vendor_name TEXT,
            country TEXT,
            tax_id TEXT,
            final_status TEXT,
            risk_score INTEGER,
            summary_reason TEXT,
            stages_json TEXT,
            field_checks_json TEXT,
            pdf_extracted_json TEXT,
            email_draft TEXT,
            processing_ms INTEGER
        )
    """)
    conn.commit()
    conn.close()


def log_run_to_db(result: dict):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO onboarding_runs
        (run_id, timestamp, scenario_id, vendor_name, country, tax_id,
         final_status, risk_score, summary_reason, stages_json,
         field_checks_json, pdf_extracted_json, email_draft, processing_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        result["run_id"],
        result["timestamp"],
        result["scenario_id"],
        result["vendor_name"],
        result["country"],
        result["tax_id"],
        result["final_status"],
        result["risk_score"],
        result["summary_reason"],
        json.dumps(result["stages"]),
        json.dumps(result["field_checks"]),
        json.dumps(result["pdf_extracted"]),
        result["email_draft"],
        result["processing_ms"]
    ))
    conn.commit()
    conn.close()


def fetch_all_runs() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM onboarding_runs ORDER BY timestamp DESC", conn)
    conn.close()
    return df


def clear_all_runs():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM onboarding_runs")
    conn.commit()
    conn.close()