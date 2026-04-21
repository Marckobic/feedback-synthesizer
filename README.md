# Customer Feedback Synthesizer — AI Agent

> AI PM Portfolio Project · Built by Mark

An AI agent that transforms unstructured customer reviews into a prioritized product opportunity backlog — reducing analysis time by 80%.

**[🚀 Live Demo →](https://feedback-synthesizergit-paqd5xqee53zstpuuvgzdc.streamlit.app)**

---

## What It Does

1. Reads customer reviews from any CSV (App Store, G2, Trustpilot, Intercom)
2. Sends them to GPT-4o for semantic theme clustering
3. Scores each cluster by severity, frequency, and strategic impact
4. Outputs a 3-sheet Excel report ready for sprint planning

## Output

| Sheet | Contents |
|-------|----------|
| 📊 Dashboard | Clusters ranked by opportunity score |
| 🎯 Opportunity Backlog | User stories, KPIs, recommended actions |
| 📋 Raw Data | All reviews with cluster assignment |

## Run Locally

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...

# Web app
streamlit run app.py

# CLI (outputs Excel directly)
python feedback_synthesizer.py sample_reviews.csv
```

## Input CSV Format

Required columns: `id`, `source`, `rating`, `text`, `date`

```csv
id,source,rating,text,date
1,App Store,2,Setup took forever. No guidance.,2024-11-03
2,G2,4,Great concept but needs bank sync.,2024-11-05
```

## Cost

~$0.05–0.15 per run with GPT-4o (50–100 reviews). Runs in under 30 seconds.

## Tech Stack

- **Python** — core agent logic
- **OpenAI GPT-4o** — semantic clustering + opportunity scoring
- **openpyxl** — Excel report generation
- **Streamlit** — web interface

---

*Part of my AI PM portfolio. See also: [FinSight.ai](https://finsight-ai-tawny.vercel.app)*
