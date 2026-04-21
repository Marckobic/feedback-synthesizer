"""
Customer Feedback Synthesizer — Streamlit Web App
Upload a CSV of customer reviews → get a prioritized product backlog (Excel)
"""

import io
import json
import os
import tempfile

import pandas as pd
import streamlit as st
from openai import OpenAI

from feedback_synthesizer import analyze_reviews, build_excel

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Feedback Synthesizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── STYLES ─────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
  .main { background-color: #0f0f0f; }
  .block-container { padding-top: 2rem; max-width: 1100px; }
  h1 { color: #4F46E5 !important; letter-spacing: -1px; }
  h2 { color: #1E1B4B !important; }
  .metric-box {
    background: #EEF2FF;
    border: 1px solid #C7D2FE;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: center;
  }
  .metric-val { font-size: 28px; font-weight: 800; color: #4F46E5; }
  .metric-lbl { font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; }
  .sev-critical { background:#FEE2E2; color:#DC2626; border-radius:6px; padding:2px 8px; font-weight:700; font-size:12px; }
  .sev-high     { background:#FEF3C7; color:#D97706; border-radius:6px; padding:2px 8px; font-weight:700; font-size:12px; }
  .sev-medium   { background:#DBEAFE; color:#2563EB; border-radius:6px; padding:2px 8px; font-weight:700; font-size:12px; }
  .sev-low      { background:#DCFCE7; color:#16A34A; border-radius:6px; padding:2px 8px; font-weight:700; font-size:12px; }
  .score-pill   { background:#4F46E5; color:white; border-radius:20px; padding:2px 10px; font-weight:700; font-size:13px; }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.divider()

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Your key is used only for this session and never stored.",
    )

    st.divider()
    st.markdown("### 📋 CSV Format")
    st.markdown("""
Required columns:
- `id` — unique integer
- `source` — e.g. App Store, G2
- `rating` — integer 1–5
- `text` — review text
- `date` — YYYY-MM-DD
""")

    st.download_button(
        "⬇️ Download Sample CSV",
        data=open(os.path.join(os.path.dirname(__file__), "sample_reviews.csv"), "rb").read(),
        file_name="sample_reviews.csv",
        mime="text/csv",
    )

    st.divider()
    st.markdown("""
<small>Built by **Mark** · [GitHub](https://github.com/Marckobic) · AI PM Portfolio Project</small>
""", unsafe_allow_html=True)

# ── HEADER ─────────────────────────────────────────────────────────────────────

st.title("🔍 Customer Feedback Synthesizer")
st.markdown(
    "Upload customer reviews → AI clusters themes → get a prioritized **product backlog**."
)
st.divider()

# ── FILE UPLOAD ────────────────────────────────────────────────────────────────

uploaded = st.file_uploader(
    "Upload your reviews CSV",
    type=["csv"],
    help="Must have columns: id, source, rating, text, date",
)

if not uploaded:
    st.info("👆 Upload a CSV to get started. Use the sample file in the sidebar to try it out.")
    st.stop()

# ── LOAD & PREVIEW ─────────────────────────────────────────────────────────────

df = pd.read_csv(uploaded)
required = {"id", "source", "rating", "text", "date"}
missing = required - set(df.columns)
if missing:
    st.error(f"Missing columns: {', '.join(missing)}")
    st.stop()

with st.expander(f"📄 Preview — {len(df)} reviews loaded", expanded=False):
    st.dataframe(df.head(10), use_container_width=True)

# ── RUN ANALYSIS ───────────────────────────────────────────────────────────────

if not api_key:
    st.warning("Enter your OpenAI API key in the sidebar to run the analysis.")
    st.stop()

run_btn = st.button("🚀 Analyze Reviews", type="primary", use_container_width=True)

if not run_btn:
    st.stop()

reviews = df.to_dict("records")
for r in reviews:
    r["id"] = int(r["id"])
    r["rating"] = int(r["rating"])
    r["text"] = str(r["text"]).strip()

with st.spinner(f"Analyzing {len(reviews)} reviews with GPT-4o…"):
    try:
        result = analyze_reviews(reviews, api_key)
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        st.stop()

clusters = result["clusters"]
summary  = result["summary"]

# ── KPI ROW ────────────────────────────────────────────────────────────────────

st.divider()
st.subheader("📊 Analysis Summary")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-box">
        <div class="metric-val">{summary['total_reviews']}</div>
        <div class="metric-lbl">Reviews Analyzed</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-box">
        <div class="metric-val">{len(clusters)}</div>
        <div class="metric-lbl">Clusters Found</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-box">
        <div class="metric-val">{summary['critical_count']}</div>
        <div class="metric-lbl">Critical Issues</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-box">
        <div class="metric-val">{summary['avg_rating']} / 5</div>
        <div class="metric-lbl">Avg Rating</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"> **Top insight:** {summary['top_insight']}")

# ── OPPORTUNITY TABLE ──────────────────────────────────────────────────────────

st.divider()
st.subheader("🎯 Opportunity Backlog")

sev_tag = {
    "Critical": '<span class="sev-critical">Critical</span>',
    "High":     '<span class="sev-high">High</span>',
    "Medium":   '<span class="sev-medium">Medium</span>',
    "Low":      '<span class="sev-low">Low</span>',
}

for i, cl in enumerate(clusters, 1):
    with st.expander(
        f"P{i} · {cl['theme']} · Score {cl['opportunity_score']}  "
        f"({cl['frequency']} reviews, avg {cl['avg_rating']}★)",
        expanded=(i <= 3),
    ):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Description:** {cl['description']}")
            st.markdown(f"**User Story:** *{cl['user_story']}*")
            st.markdown(f"**Recommended Action:** {cl['recommended_action']}")
            st.markdown(f"**KPI:** {cl['kpi']}")
            st.markdown(f"**Quote:** *\"{cl['sample_quote']}\"*")
        with col2:
            st.markdown(f"**Severity:** {sev_tag.get(cl['severity'], cl['severity'])}", unsafe_allow_html=True)
            st.markdown(f"**Effort:** {cl['effort']}")
            st.markdown(f"**Reviews:** {cl['frequency']}")
            st.markdown(f"**Avg Rating:** {cl['avg_rating']} ★")

# ── DOWNLOAD EXCEL ─────────────────────────────────────────────────────────────

st.divider()
st.subheader("⬇️ Download Full Report")

with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
    build_excel(clusters, summary, reviews, tmp.name)
    with open(tmp.name, "rb") as f:
        excel_bytes = f.read()

st.download_button(
    label="📥 Download Excel Report (3 sheets)",
    data=excel_bytes,
    file_name="feedback_synthesizer_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
    type="primary",
)

st.caption("Dashboard · Opportunity Backlog · Raw Data with cluster assignments")
