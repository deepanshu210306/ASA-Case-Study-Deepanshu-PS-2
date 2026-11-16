"""VendorGuard design system — single light Indigo SaaS theme. No dark mode."""

import json
import streamlit.components.v1 as components

CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --bg: #F5F7FF;
  --surface: #FFFFFF;
  --surface-soft: #EEF0FF;
  --heading: #172033;
  --body: #667085;
  --muted: #98A2B3;
  --border: #E4E7F0;
  --accent: #5B5CE2;
  --accent-hover: #4A4BD4;
  --accent-soft: rgba(91, 92, 226, 0.12);
  --accent-ring: rgba(91, 92, 226, 0.18);
  --success: #12B76A;
  --success-bg: #ECFDF3;
  --success-border: #A6F4C5;
  --warning: #F79009;
  --warning-bg: #FFFAEB;
  --warning-border: #FEDF89;
  --error: #F04438;
  --error-bg: #FEF3F2;
  --error-border: #FECDCA;
  --radius: 14px;
  --radius-sm: 10px;
  --shadow: 0 1px 2px rgba(23, 32, 51, 0.04), 0 8px 24px rgba(23, 32, 51, 0.05);
  --shadow-hover: 0 4px 12px rgba(23, 32, 51, 0.07), 0 16px 32px rgba(91, 92, 226, 0.08);
  --shadow-btn: 0 6px 16px rgba(91, 92, 226, 0.28);
}

html, body, .stApp, [class*="css"] {
  font-family: "Inter", sans-serif !important;
  color: var(--heading) !important;
}

.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
section.main,
.main .block-container {
  background: var(--bg) !important;
  background-color: var(--bg) !important;
}

[data-testid="stHeader"] {
  background: rgba(245, 247, 255, 0.88) !important;
  backdrop-filter: blur(10px);
  height: 3rem;
  border-bottom: 1px solid transparent;
}
[data-testid="stToolbar"] { right: 1rem; top: 0.45rem; }

.block-container {
  padding-top: 3.5rem !important;
  padding-bottom: 3.25rem !important;
  max-width: 1160px !important;
}

[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
  color: var(--heading) !important;
  font-family: "Space Grotesk", sans-serif !important;
  letter-spacing: -0.02em;
}

[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] span:not([data-tag]),
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span:not([data-tag]) {
  color: var(--body) !important;
}
[data-testid="stCaption"], .stCaption,
[data-testid="stAppViewContainer"] small,
[data-testid="stSidebar"] .stCaption {
  color: var(--muted) !important;
}

a, a span { color: var(--accent) !important; }
a:hover { color: var(--accent-hover) !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg) !important;
  background-color: var(--bg) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  background: transparent !important;
  padding-top: 1.1rem;
  padding-left: 0.85rem;
  padding-right: 0.85rem;
}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: var(--body) !important;
}
[data-testid="stSidebar"] hr {
  border: none;
  height: 1px;
  background: var(--border);
  margin: 1.05rem 0;
}
[data-testid="stSidebar"] .stDownloadButton button,
[data-testid="stSidebar"] .stButton button {
  background: var(--surface) !important;
  color: var(--heading) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-sm) !important;
  font-weight: 600 !important;
  font-size: 0.82rem !important;
  box-shadow: var(--shadow);
  transition: border-color 0.18s ease, transform 0.15s ease, box-shadow 0.18s ease, color 0.18s ease;
}
[data-testid="stSidebar"] .stDownloadButton button:hover,
[data-testid="stSidebar"] .stButton button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-hover);
}

/* ── Inputs ── */
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stNumberInput"] input,
div[data-baseweb="input"],
div[data-baseweb="base-input"],
div[data-baseweb="base-input"] input,
div[data-baseweb="textarea"] textarea {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  color: #172033 !important;
  border: 1px solid #E4E7F0 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  caret-color: #172033 !important;
  font-family: "Inter", sans-serif !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus,
div[data-baseweb="base-input"]:focus-within {
  border-color: #5B5CE2 !important;
  box-shadow: 0 0 0 3px rgba(91, 92, 226, 0.16) !important;
}

/* Selects / dropdowns */
div[data-baseweb="select"] > div {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  color: #172033 !important;
  border: 1px solid #E4E7F0 !important;
  border-radius: 12px !important;
  box-shadow: none !important;
  min-height: 42px;
}
div[data-baseweb="select"] > div:hover {
  border-color: #C8CDDB !important;
}
div[data-baseweb="select"] > div:focus-within {
  border-color: #5B5CE2 !important;
  box-shadow: 0 0 0 3px rgba(91, 92, 226, 0.16) !important;
}
div[data-baseweb="select"] > div *,
div[data-baseweb="select"] span {
  color: #172033 !important;
  background: transparent !important;
}
div[data-baseweb="select"] svg {
  fill: #98A2B3 !important;
  color: #98A2B3 !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="menu"],
ul[role="listbox"] {
  background: #FFFFFF !important;
  background-color: #FFFFFF !important;
  border: 1px solid #E4E7F0 !important;
  border-radius: 12px !important;
  box-shadow: var(--shadow-hover) !important;
}
li[role="option"] {
  background: #FFFFFF !important;
  color: #172033 !important;
  border-radius: 8px !important;
}
li[role="option"]:hover,
li[role="option"][aria-selected="true"] {
  background: #EEF0FF !important;
  color: #172033 !important;
}

/* Radio / checkbox */
div[data-testid="stRadio"] label p,
div[data-testid="stCheckbox"] label p {
  color: #667085 !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] {
  gap: 0.35rem;
}
div[data-testid="stRadio"] div[role="radio"] {
  background: #FFFFFF !important;
  border: 2px solid #E4E7F0 !important;
}
div[data-testid="stRadio"] div[role="radio"][aria-checked="true"] {
  border-color: #5B5CE2 !important;
  background: #5B5CE2 !important;
  box-shadow: inset 0 0 0 3px #FFFFFF;
}
div[data-testid="stCheckbox"] span[data-baseweb="checkbox"] {
  background: #FFFFFF !important;
  border: 2px solid #E4E7F0 !important;
  border-radius: 6px !important;
}
div[data-testid="stCheckbox"] span[data-baseweb="checkbox"][data-checked="true"] {
  background: #5B5CE2 !important;
  border-color: #5B5CE2 !important;
}

/* Multiselect chips — soft lavender + indigo text (high contrast) */
[data-testid="stMultiSelect"] span[data-tag],
span[data-tag],
div[data-baseweb="tag"],
span[data-baseweb="tag"] {
  background: #EEF0FF !important;
  background-color: #EEF0FF !important;
  border: 1px solid rgba(91, 92, 226, 0.35) !important;
  border-radius: 8px !important;
  color: #5B5CE2 !important;
}
[data-testid="stMultiSelect"] span[data-tag] *,
span[data-tag] *,
div[data-baseweb="tag"] *,
span[data-baseweb="tag"] * {
  color: #5B5CE2 !important;
  fill: #5B5CE2 !important;
  stroke: currentColor !important;
  font-weight: 600 !important;
  -webkit-text-fill-color: #5B5CE2 !important;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"],
section[data-testid="stFileUploader"],
section[data-testid="stFileUploader"] > div {
  background: #FFFFFF !important;
  color: #667085 !important;
  border-color: #E4E7F0 !important;
}
[data-testid="stFileUploaderDropzone"] {
  border: 1.5px dashed #D0D5E0 !important;
  border-radius: 14px !important;
  transition: border-color 0.18s ease, background 0.18s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
  border-color: #5B5CE2 !important;
  background: #EEF0FF !important;
}

div[data-testid="stAlert"],
[data-testid="stExpander"],
[data-testid="stStatusWidget"],
[data-testid="stMetric"] {
  background: #FFFFFF !important;
  color: #667085 !important;
  border: 1px solid #E4E7F0 !important;
  border-radius: 14px !important;
}

/* ── Brand / sidebar cards ── */
.vg-side-brand {
  position: relative;
  overflow: hidden;
  background: #FFFFFF;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.25rem 1.2rem 1.15rem;
  margin-bottom: 1.15rem;
  box-shadow: var(--shadow);
  animation: vg-rise 0.4s ease both;
}
.vg-side-brand::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--accent);
}
.vg-side-brand .vg-kicker {
  font-family: "JetBrains Mono", monospace !important;
  font-size: 0.66rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--accent) !important;
  margin-bottom: 0.4rem;
  font-weight: 600;
}
.vg-side-brand h2 {
  font-family: "Space Grotesk", sans-serif !important;
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin: 0 0 0.45rem 0;
  color: var(--heading) !important;
  line-height: 1.15;
}
.vg-side-brand p {
  margin: 0;
  font-size: 0.84rem;
  line-height: 1.5;
  color: var(--muted) !important;
}

.vg-side-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 0.85rem 1rem 0.7rem;
  margin-bottom: 0.75rem;
  box-shadow: var(--shadow);
}
.vg-side-section .vg-section-label,
.vg-section-label,
.vg-kicker {
  font-family: "JetBrains Mono", monospace !important;
  font-size: 0.62rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: var(--accent) !important;
  font-weight: 600;
  margin-bottom: 0.28rem;
}
.vg-side-section .vg-section-title,
.vg-section-title {
  font-family: "Space Grotesk", sans-serif !important;
  font-size: 1.08rem;
  font-weight: 600;
  color: var(--heading) !important;
  margin: 0;
  letter-spacing: -0.02em;
}

/* ── Hero ── */
.vg-hero {
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  padding: 2rem 2.1rem 1.85rem;
  margin: 0.15rem 0 1.35rem 0;
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow);
  animation: vg-rise 0.45s ease both;
}
.vg-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 90% at 100% 0%, rgba(91, 92, 226, 0.10), transparent 55%),
    linear-gradient(180deg, #EEF0FF 0%, #FFFFFF 62%);
  pointer-events: none;
}
.vg-hero::after {
  content: "";
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 4px;
  background: var(--accent);
  border-radius: 18px 0 0 18px;
}
.vg-hero > * { position: relative; z-index: 1; }
.vg-hero .vg-kicker {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.28rem 0.65rem;
  margin-bottom: 0.75rem;
  background: var(--surface-soft);
  border: 1px solid rgba(91, 92, 226, 0.18);
  border-radius: 999px;
  color: var(--accent) !important;
  font-size: 0.68rem;
}
.vg-brand {
  font-family: "Space Grotesk", sans-serif !important;
  font-weight: 700;
  font-size: clamp(1.95rem, 3.4vw, 2.65rem);
  line-height: 1.08;
  letter-spacing: -0.04em;
  margin: 0 0 0.65rem 0;
  color: #172033 !important;
}
.vg-brand em {
  font-style: normal;
  color: var(--accent) !important;
}
.vg-hero p {
  margin: 0;
  max-width: 38rem;
  color: #667085 !important;
  font-size: 1.02rem;
  line-height: 1.62;
}

/* ── Panels / cards ── */
.vg-panel {
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius);
  padding: 1.15rem 1.25rem 1.05rem;
  margin-bottom: 1.05rem;
  box-shadow: var(--shadow);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
  animation: vg-rise 0.5s ease both;
}
.vg-panel:hover {
  border-color: rgba(91, 92, 226, 0.28) !important;
  box-shadow: var(--shadow-hover);
}
.vg-panel--delay { animation-delay: 0.06s; }

.vg-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.32rem 0.72rem;
  border-radius: 999px;
  font-family: "JetBrains Mono", monospace !important;
  font-weight: 600;
  font-size: 0.7rem;
  letter-spacing: 0.04em;
}
.vg-badge--ok { background: var(--success-bg); color: var(--success) !important; border: 1px solid var(--success-border); }
.vg-badge--warn { background: var(--warning-bg); color: var(--warning) !important; border: 1px solid var(--warning-border); }
.vg-badge--bad { background: var(--error-bg); color: var(--error) !important; border: 1px solid var(--error-border); }

.vg-chip {
  display: inline-block;
  padding: 0.14rem 0.45rem;
  border-radius: 6px;
  font-family: "JetBrains Mono", monospace !important;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}
.vg-chip--ok { background: var(--success-bg); color: var(--success) !important; }
.vg-chip--warn { background: var(--warning-bg); color: var(--warning) !important; }
.vg-chip--bad { background: var(--error-bg); color: var(--error) !important; }

.vg-stage {
  border: 1px solid var(--border);
  border-left: 3px solid var(--border);
  padding: 0.8rem 0.95rem;
  margin: 0.45rem 0;
  background: #FFFFFF !important;
  border-radius: 0 12px 12px 0;
  transition: border-color 0.2s ease, background 0.2s ease;
}
.vg-stage--ok { border-left-color: var(--success); background: linear-gradient(90deg, rgba(18,183,106,0.06), #FFFFFF 48%) !important; }
.vg-stage--warn { border-left-color: var(--warning); background: linear-gradient(90deg, rgba(247,144,9,0.07), #FFFFFF 48%) !important; }
.vg-stage--bad { border-left-color: var(--error); background: linear-gradient(90deg, rgba(240,68,56,0.06), #FFFFFF 48%) !important; }
.vg-stage-head {
  display: flex;
  gap: 0.55rem;
  align-items: center;
  flex-wrap: wrap;
  font-family: "Space Grotesk", sans-serif !important;
  font-weight: 600;
  color: var(--heading) !important;
  margin-bottom: 0.28rem;
}
.vg-stage-detail {
  color: var(--muted) !important;
  font-size: 0.87rem;
  line-height: 1.5;
}

.vg-metric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.9rem;
  margin: 0.95rem 0 1.05rem;
}
.vg-metric {
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  border-top: 3px solid var(--accent);
  border-radius: 14px;
  padding: 1.05rem 1.1rem;
  box-shadow: var(--shadow);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.vg-metric:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  border-color: rgba(91, 92, 226, 0.28) !important;
  border-top-color: var(--accent) !important;
}
.vg-metric span {
  display: block;
  font-family: "JetBrains Mono", monospace !important;
  font-size: 0.62rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted) !important;
  font-weight: 500;
  margin-bottom: 0.45rem;
}
.vg-metric strong {
  font-family: "Space Grotesk", sans-serif !important;
  font-size: 1.18rem;
  color: var(--heading) !important;
  font-weight: 600;
}

.vg-empty {
  border: 1.5px dashed rgba(91, 92, 226, 0.28) !important;
  border-radius: 16px;
  padding: 2.6rem 1.6rem;
  text-align: center;
  background: #EEF0FF !important;
  color: var(--muted) !important;
  box-shadow: none;
}
.vg-empty strong {
  display: block;
  font-family: "Space Grotesk", sans-serif !important;
  color: var(--heading) !important;
  font-size: 1.12rem;
  margin-bottom: 0.45rem;
  font-weight: 600;
}

.vg-summary {
  background: var(--surface-soft) !important;
  border: 1px solid rgba(91, 92, 226, 0.18);
  border-radius: 14px;
  padding: 1rem 1.1rem;
  color: var(--body) !important;
  line-height: 1.55;
  margin-bottom: 0.95rem;
}
.vg-summary b { color: var(--accent) !important; font-weight: 600; }

.vg-stat-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.9rem;
  margin: 0.35rem 0 1.15rem;
}
.vg-stat {
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px;
  padding: 1.05rem 1.1rem;
  box-shadow: var(--shadow);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}
.vg-stat:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  border-color: rgba(91, 92, 226, 0.25) !important;
}
.vg-stat span {
  display: block;
  font-family: "JetBrains Mono", monospace !important;
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted) !important;
  font-weight: 500;
}
.vg-stat strong {
  font-family: "Space Grotesk", sans-serif !important;
  font-size: 1.6rem;
  color: var(--heading) !important;
  font-weight: 700;
  letter-spacing: -0.03em;
}
.vg-stat em {
  font-style: normal;
  font-size: 0.76rem;
  color: var(--muted) !important;
}

.vg-edge-wrap {
  background: #FFFFFF !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--shadow);
}
.vg-edge-head {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr 2fr 0.7fr;
  gap: 0.7rem;
  padding: 0.7rem 1.05rem;
  font-family: "JetBrains Mono", monospace !important;
  font-size: 0.6rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted) !important;
  font-weight: 600;
  border-bottom: 1px solid var(--border);
  background: var(--surface-soft) !important;
}
.vg-edge {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr 2fr 0.7fr;
  gap: 0.7rem;
  padding: 1rem 1.05rem;
  border-bottom: 1px solid var(--border);
  align-items: start;
  transition: background 0.18s ease;
}
.vg-edge:hover { background: var(--surface-soft); }
.vg-edge:last-child { border-bottom: none; }
.vg-edge strong {
  font-family: "Space Grotesk", sans-serif !important;
  color: var(--heading) !important;
  font-size: 0.95rem;
  font-weight: 600;
}
.vg-edge p {
  margin: 0;
  color: var(--muted) !important;
  font-size: 0.85rem;
  line-height: 1.45;
}

/* ── Tabs ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 0.15rem;
  border-bottom: 1px solid var(--border) !important;
  padding-bottom: 0;
  background: transparent !important;
  margin-bottom: 0.35rem;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  font-family: "Inter", sans-serif !important;
  font-weight: 600;
  font-size: 0.92rem !important;
  color: var(--muted) !important;
  background: transparent !important;
  border-radius: 0 !important;
  padding: 0.65rem 1rem !important;
  transition: color 0.18s ease;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
  color: var(--heading) !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--accent) !important;
  box-shadow: inset 0 -2px 0 var(--accent) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] {
  display: none !important;
}

/* ── Buttons ── */
div[data-testid="stForm"] button,
.stButton > button[kind="primary"],
button[kind="primaryFormSubmit"] {
  background: #5B5CE2 !important;
  background-color: #5B5CE2 !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 12px !important;
  font-weight: 700 !important;
  font-family: "Inter", sans-serif !important;
  letter-spacing: 0.01em;
  box-shadow: var(--shadow-btn);
  transition: background 0.18s ease, transform 0.15s ease, box-shadow 0.18s ease;
}
div[data-testid="stForm"] button:hover,
.stButton > button[kind="primary"]:hover,
button[kind="primaryFormSubmit"]:hover {
  background: #4A4BD4 !important;
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(91, 92, 226, 0.34);
}
div[data-testid="stForm"] button *,
.stButton > button[kind="primary"] *,
button[kind="primaryFormSubmit"] * {
  color: #FFFFFF !important;
}
.stButton > button[kind="secondary"] {
  background: #FFFFFF !important;
  color: #172033 !important;
  border: 1px solid #E4E7F0 !important;
  border-radius: 12px !important;
  font-weight: 600 !important;
}
.stButton > button[kind="secondary"]:hover {
  border-color: #5B5CE2 !important;
  color: #5B5CE2 !important;
}

[data-testid="stDataFrame"],
.stCodeBlock,
pre,
code,
[data-testid="stJson"] {
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  background: #FFFFFF !important;
  color: var(--body) !important;
}

@keyframes vg-rise {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
  .vg-metric-grid, .vg-stat-row, .vg-edge, .vg-edge-head { grid-template-columns: 1fr; }
  .vg-edge-head { display: none; }
  .block-container { padding-top: 3.15rem !important; }
  .vg-hero { padding: 1.5rem 1.35rem 1.4rem; }
}

/* Final override: Audit History filter chips — readable indigo on lavender */
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] span[data-tag],
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] span[data-tag] span,
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] span[data-tag] button,
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] span[data-tag] svg,
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] span[data-tag] * {
  background-color: #EEF0FF !important;
  color: #5B5CE2 !important;
  fill: #5B5CE2 !important;
  -webkit-text-fill-color: #5B5CE2 !important;
  font-weight: 600 !important;
}
[data-testid="stAppViewContainer"] [data-testid="stMultiSelect"] span[data-tag] {
  background: #EEF0FF !important;
  border: 1px solid rgba(91, 92, 226, 0.35) !important;
}
"""


def inject_styles() -> None:
    """Inject the light Indigo design system into the parent Streamlit document."""
    css_json = json.dumps(CSS)
    components.html(
        f"""
        <script>
        (() => {{
          const doc = window.parent.document;
          const id = "vg-vendorguard-styles";
          doc.querySelectorAll("#" + id + ", #vg-chip-contrast-fix, #vg-multiselect-chip-fix").forEach((n) => n.remove());

          const style = doc.createElement("style");
          style.id = id;
          style.setAttribute("data-vg-css-ver", "indigo-light-v2");
          style.textContent = {css_json};
          doc.head.appendChild(style);

          // One-time cleanup of prior dual-theme sessions
          doc.documentElement.removeAttribute("data-vg-theme");
          if (doc.body) doc.body.removeAttribute("data-vg-theme");
          const toggle = doc.getElementById("vg-theme-toggle");
          if (toggle) toggle.remove();
          try {{ window.parent.localStorage.removeItem("vg-theme"); }} catch (e) {{}}
        }})();
        </script>
        """,
        height=0,
    )
