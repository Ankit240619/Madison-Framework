"""
Madison Transparency Agent - Streamlit Dashboard
Replicates the n8n workflow logic for CPU anomaly detection + news correlation.
"""

import streamlit as st
import pandas as pd
import requests
import feedparser
import json
import math
import re
from datetime import datetime
from io import StringIO

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

import plotly.graph_objects as go

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Madison Transparency Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #5A6C7E;
        margin-bottom: 1.5rem;
    }
    .status-healthy {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px 20px;
        border-radius: 6px;
        margin: 10px 0;
    }
    .status-warning {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px 20px;
        border-radius: 6px;
        margin: 10px 0;
    }
    .status-critical {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        padding: 15px 20px;
        border-radius: 6px;
        margin: 10px 0;
    }
    .news-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Helper: Get API Keys from Secrets
# ──────────────────────────────────────────────

def get_secret(key: str, default: str = "") -> str:
    """Retrieve a secret from Streamlit secrets, env vars, or return default."""
    try:
        return st.secrets[key]
    except Exception:
        import os
        return os.environ.get(key, default)


# ──────────────────────────────────────────────
# Data Fetching Functions (mirrors n8n nodes)
# ──────────────────────────────────────────────

@st.cache_data(ttl=600, show_spinner=False)
def fetch_nab_csv(url: str, sample_step: int = 200) -> list[dict]:
    """
    Download NAB CPU CSV and sample every Nth record into unified schema.
    Mirrors: HTTP Request -> Code in JavaScript node.
    """
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        csv_text = resp.text
        lines = csv_text.strip().split("\n")
        headers = lines[0].split(",")

        records = []
        errors = []
        idx = 0
        for i in range(1, len(lines), sample_step):
            line = lines[i].strip()
            if not line:
                continue
            parts = line.split(",")
            try:
                timestamp = parts[0]
                value = float(parts[1])
                records.append({
                    "record_id": f"nab_cpu_{idx + 1}",
                    "source": "kaggle",
                    "source_name": "NAB - Numenta Anomaly Benchmark",
                    "record_type": "metric",
                    "timestamp": timestamp,
                    "metric_name": "cpu_utilization",
                    "metric_value": value,
                    "description": "AWS CPU utilization metric",
                    "category": "infrastructure",
                })
                idx += 1
            except (IndexError, ValueError) as e:
                errors.append(f"Row {i}: {e}")
        return records
    except Exception as e:
        st.error(f"Error fetching NAB CSV: {e}")
        return []


@st.cache_data(ttl=600, show_spinner=False)
def fetch_rss(feed_url: str, source_name: str, prefix: str) -> list[dict]:
    """
    Parse an RSS feed and return unified-schema news records.
    Mirrors: RSS Read -> Code in JavaScript1 / Code in JavaScript3 nodes.
    """
    try:
        feed = feedparser.parse(feed_url)
        records = []
        for idx, entry in enumerate(feed.entries):
            title = getattr(entry, "title", None)
            link = getattr(entry, "link", None)
            if not title or not link:
                continue
            pub = getattr(entry, "published", getattr(entry, "updated", ""))
            try:
                iso_ts = datetime.strptime(pub[:25], "%a, %d %b %Y %H:%M:%S").isoformat() + "Z"
            except Exception:
                iso_ts = pub
            snippet = getattr(entry, "summary", "")[:200]
            records.append({
                "record_id": f"{prefix}_{idx + 1}",
                "source": "rss",
                "source_name": source_name,
                "record_type": "news",
                "timestamp": iso_ts,
                "title": title,
                "description": snippet,
                "url": link,
                "category": "tech_news",
            })
        return records
    except Exception as e:
        st.error(f"Error fetching RSS ({source_name}): {e}")
        return []


@st.cache_data(ttl=600, show_spinner=False)
def fetch_newsapi(query: str, api_key: str) -> list[dict]:
    """
    Call NewsAPI and return unified-schema news records.
    Mirrors: HTTP Request1 -> Code in JavaScript2 node.
    """
    if not api_key:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 30,
            "apiKey": api_key,
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            st.warning(f"NewsAPI returned status: {data.get('status')} — {data.get('message', '')}")
            return []

        records = []
        for idx, art in enumerate(data.get("articles", [])[:30]):
            title = art.get("title", "")
            link = art.get("url", "")
            if not title or not link or title == "[Removed]":
                continue
            pub = art.get("publishedAt", "")
            records.append({
                "record_id": f"newsapi_{idx + 1}",
                "source": "newsapi",
                "source_name": art.get("source", {}).get("name", "Unknown"),
                "record_type": "news",
                "timestamp": pub,
                "title": title,
                "description": (art.get("description") or "")[:200],
                "url": link,
                "category": "business_tech",
            })
        return records
    except Exception as e:
        st.error(f"Error fetching NewsAPI: {e}")
        return []


# ──────────────────────────────────────────────
# Statistics / Anomaly Detection (mirrors Prepare AI Input node)
# ──────────────────────────────────────────────

def compute_statistics(metrics: list[dict], sigma_multiplier: float = 1.5) -> dict:
    """
    Compute avg, min, max, std dev, anomaly threshold.
    Mirrors: Prepare AI Input node.
    """
    values = [m["metric_value"] for m in metrics]
    n = len(values)
    if n == 0:
        return {}
    avg = sum(values) / n
    min_v = min(values)
    max_v = max(values)
    sq_diffs = [(v - avg) ** 2 for v in values]
    std_dev = math.sqrt(sum(sq_diffs) / n)
    threshold = avg + (sigma_multiplier * std_dev)

    anomalies = [m for m in metrics if m["metric_value"] > threshold]

    return {
        "total_records": n,
        "metric_name": metrics[0].get("metric_name", "cpu_utilization"),
        "average": round(avg, 2),
        "min": round(min_v, 2),
        "max": round(max_v, 2),
        "std_dev": round(std_dev, 2),
        "anomaly_threshold": round(threshold, 2),
        "potential_anomalies_count": len(anomalies),
        "potential_anomalies": anomalies[:10],
    }


# ──────────────────────────────────────────────
# AI Calls (mirrors AI Anomaly Detector & AI Insights Narrator nodes)
# ──────────────────────────────────────────────

def call_anomaly_detector(client, metrics_summary: dict) -> str:
    """
    Send metrics summary to GPT-4o-mini for anomaly classification.
    Uses the EXACT same prompt from the n8n AI Anomaly Detector node.
    """
    anomalies_json = json.dumps(metrics_summary.get("potential_anomalies", []), indent=2, default=str)

    prompt = f"""You are a KPI Anomaly Detection Agent for the Madison Transparency system. Analyze the following CPU utilization metrics and identify anomalies.

## Metrics Summary:
- Total Records: {metrics_summary['total_records']}
- Metric: {metrics_summary['metric_name']}
- Average: {metrics_summary['average']}%
- Min: {metrics_summary['min']}%
- Max: {metrics_summary['max']}%
- Std Deviation: {metrics_summary['std_dev']}
- Anomaly Threshold (1.5 σ): {metrics_summary['anomaly_threshold']}%
- Potential Anomalies Found: {metrics_summary['potential_anomalies_count']}

## Potential Anomaly Records:
{anomalies_json}

## Your Task:
1. Analyze the metrics and confirm which are true anomalies
2. Classify each anomaly severity: CRITICAL (>80%), HIGH (60-80%), MEDIUM (40-60%)
3. Identify any patterns (time-based, consecutive spikes, etc.)

Respond in this JSON format:
{{
  "analysis_summary": "Brief overview of findings",
  "confirmed_anomalies": [
    {{
      "record_id": "xxx",
      "timestamp": "xxx",
      "value": xxx,
      "severity": "CRITICAL/HIGH/MEDIUM",
      "reason": "Why this is anomalous"
    }}
  ],
  "patterns_detected": ["pattern1", "pattern2"],
  "risk_level": "HIGH/MEDIUM/LOW",
  "recommended_actions": ["action1", "action2"]
}}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": str(e), "analysis_summary": "AI analysis unavailable"})


def call_insights_narrator(client, anomaly_text: str, news_context: list[dict]) -> str:
    """
    Generate executive summary from anomaly results + news context.
    Uses the EXACT same prompt from the n8n AI Insights Narrator node.
    """
    news_json = json.dumps(news_context[:10], indent=2, default=str)

    prompt = f"""You are the Insight Narrator for the Madison Transparency Agent. Your job is to generate clear, business-friendly explanations of KPI anomalies.

## Anomaly Analysis Results:
{anomaly_text}

## Recent News Context:
{news_json}

## Your Task:
Generate a professional executive summary that:
1. Summarizes the key findings in plain English (no technical jargon)
2. Correlates anomalies with any relevant news if applicable
3. Provides actionable recommendations for stakeholders
4. Rates overall system health: HEALTHY / WARNING / CRITICAL

Respond in this format:

# Madison Transparency Agent - Executive Summary

## Overall System Health: [HEALTHY/WARNING/CRITICAL]

## Key Findings
[2-3 bullet points summarizing the most important discoveries]

## Anomaly Details
[Brief description of each critical/high anomaly in business terms]

## Potential Business Context
[Any correlations with news or market events]

## Recommended Actions
[3-5 specific, actionable recommendations]

## Next Steps
[What should stakeholders do immediately]"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"# Error\n\nInsight generation failed: {e}"


# ──────────────────────────────────────────────
# Report Generation (mirrors Format final output node)
# ──────────────────────────────────────────────

def generate_html_report(metrics_summary: dict, executive_summary: str, anomaly_analysis: str, report_date: str) -> str:
    """Generate a styled HTML report matching the n8n workflow output."""
    health = "WARNING"
    health_color = "#FFC107"
    if metrics_summary.get("potential_anomalies_count", 0) == 0:
        health = "HEALTHY"
        health_color = "#28a745"
    elif metrics_summary.get("potential_anomalies_count", 0) > 5:
        health = "CRITICAL"
        health_color = "#dc3545"

    return f"""<!DOCTYPE html>
<html>
<head>
<title>Madison Transparency Agent Report</title>
<style>
body{{font-family:Arial,sans-serif;max-width:800px;margin:0 auto;padding:20px;background:#f5f5f5}}
.container{{background:white;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
h1{{color:#1E3A5F;border-bottom:2px solid #1E3A5F;padding-bottom:10px}}
h2{{color:#2E5A8F}}
.health{{background-color:{health_color}22;padding:15px;border-radius:5px;border-left:4px solid {health_color};margin:15px 0}}
.stat{{background:#E8F4FD;padding:10px;margin:5px 0;border-radius:4px}}
.action{{background:#E8F5E9;padding:10px;margin:5px 0;border-radius:4px}}
pre{{background:#f4f4f4;padding:12px;border-radius:6px;overflow-x:auto;font-size:0.85em}}
</style>
</head>
<body>
<div class="container">
<h1>Madison Transparency Agent</h1>
<p>Report Generated: {report_date}</p>
<div class="health"><strong>System Health: {health}</strong><br>{metrics_summary.get('potential_anomalies_count',0)} anomalies detected in {metrics_summary.get('total_records',0)} records</div>

<h2>Key Metrics</h2>
<div class="stat">Records Analyzed: {metrics_summary.get('total_records',0)}</div>
<div class="stat">Average CPU: {metrics_summary.get('average',0)}%</div>
<div class="stat">Min CPU: {metrics_summary.get('min',0)}% | Max CPU: {metrics_summary.get('max',0)}%</div>
<div class="stat">Std Deviation: {metrics_summary.get('std_dev',0)}</div>
<div class="stat">Anomaly Threshold: {metrics_summary.get('anomaly_threshold',0)}%</div>
<div class="stat">Anomalies Found: {metrics_summary.get('potential_anomalies_count',0)}</div>

<h2>Executive Summary</h2>
<pre>{executive_summary}</pre>

<h2>Anomaly Analysis</h2>
<pre>{anomaly_analysis}</pre>

<p><em>Powered by Madison Transparency Agent + OpenAI GPT-4o-mini</em></p>
</div>
</body>
</html>"""


def generate_json_report(metrics_summary: dict, executive_summary: str, anomaly_analysis: str, source_counts: dict) -> dict:
    """Generate JSON report matching the n8n workflow output."""
    parsed_anomalies = {}
    try:
        match = re.search(r"\{[\s\S]*\}", anomaly_analysis)
        if match:
            parsed_anomalies = json.loads(match.group(0))
    except Exception:
        parsed_anomalies = {"raw_analysis": anomaly_analysis}

    return {
        "report_metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "agent_name": "Madison Transparency Agent",
            "ai_model": "GPT-4o-mini",
        },
        "executive_summary": executive_summary,
        "anomaly_analysis": parsed_anomalies,
        "metrics_summary": metrics_summary,
        "data_sources": source_counts,
    }


# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Madison Transparency Agent")
    st.caption("AI-powered KPI anomaly detection and executive reporting tool.")

    with st.expander("About", expanded=False):
        st.markdown("""
**What it does:** Fetches CPU utilization metrics from the NAB benchmark dataset, 
correlates them with the latest tech news, uses GPT-4o-mini to detect anomalies and 
generate an executive summary.

**Who it's for:** DevOps engineers, site-reliability teams, and business stakeholders 
who need transparent, AI-explained infrastructure monitoring.

**Tech Stack:**
- n8n workflow automation (original pipeline)
- OpenAI GPT-4o-mini (anomaly classification + narrative)
- Streamlit (interactive dashboard)
- Pandas & Plotly (data processing + visualization)
        """)

    st.divider()
    st.markdown("**Built by:** Ankit Deopurkar")
    st.markdown("[GitHub](https://github.com/ankitdeopurkar) | [LinkedIn](https://linkedin.com/in/ankitdeopurkar)")

# ──────────────────────────────────────────────
# Main Content: Input Section
# ──────────────────────────────────────────────

st.markdown('<div class="main-header">Madison Transparency Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered CPU anomaly detection with news-correlated executive insights</div>', unsafe_allow_html=True)

# ---- Input Controls ----
with st.expander("Configuration", expanded=True):
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Data Sources")
        enable_nab = st.checkbox("NAB CPU Metrics (Kaggle)", value=True, help="Numenta Anomaly Benchmark dataset")
        enable_techcrunch = st.checkbox("TechCrunch RSS", value=True, help="Latest TechCrunch articles")
        enable_venturebeat = st.checkbox("VentureBeat AI RSS", value=True, help="VentureBeat AI category feed")
        enable_newsapi = st.checkbox("NewsAPI Articles", value=True, help="News articles via NewsAPI")

    with col_right:
        st.subheader("Parameters")
        sigma_mult = st.slider(
            "Anomaly Threshold Multiplier (σ)",
            min_value=1.0, max_value=3.0, value=1.5, step=0.1,
            help="Number of standard deviations above the mean to flag an anomaly. Default 1.5σ matches the n8n workflow."
        )
        csv_url = st.text_input(
            "NAB CSV URL",
            value="https://raw.githubusercontent.com/numenta/NAB/master/data/realKnownCause/cpu_utilization_asg_misconfiguration.csv",
            placeholder="https://raw.githubusercontent.com/numenta/NAB/master/data/...",
            help="URL of a CSV with timestamp,value columns"
        )
        news_query = st.text_input(
            "NewsAPI Search Query",
            value="AI analytics metrics",
            placeholder="e.g. AI analytics metrics",
            help="Search query for NewsAPI articles"
        )
        email_field = st.text_input(
            "Email (optional)",
            value="",
            placeholder="your@email.com",
            help="Enter email to receive the report (future feature)"
        )

# Validation
sources_selected = any([enable_nab, enable_techcrunch, enable_venturebeat, enable_newsapi])
if not sources_selected:
    st.warning("Please select at least one data source.")

# ──────────────────────────────────────────────
# Run Analysis
# ──────────────────────────────────────────────

run_btn = st.button("Run Analysis", type="primary", disabled=not sources_selected, use_container_width=True)

if run_btn:
    # ---- Phase 1: Data Fetching ----
    all_records: list[dict] = []
    source_counts: dict = {}

    with st.status("Fetching data sources...", expanded=True) as status:

        if enable_nab:
            st.write("Downloading NAB CPU utilization CSV...")
            nab_records = fetch_nab_csv(csv_url)
            all_records.extend(nab_records)
            source_counts["kaggle_nab"] = len(nab_records)
            st.write(f"  -> {len(nab_records)} metric records loaded")

        if enable_techcrunch:
            st.write("Fetching TechCrunch RSS feed...")
            tc_records = fetch_rss("https://techcrunch.com/feed/", "TechCrunch", "rss_techcrunch")
            all_records.extend(tc_records)
            source_counts["techcrunch_rss"] = len(tc_records)
            st.write(f"  -> {len(tc_records)} news articles loaded")

        if enable_venturebeat:
            st.write("Fetching VentureBeat AI RSS feed...")
            vb_records = fetch_rss("https://venturebeat.com/category/ai/feed/", "VentureBeat AI", "rss_venturebeat")
            all_records.extend(vb_records)
            source_counts["venturebeat_rss"] = len(vb_records)
            st.write(f"  -> {len(vb_records)} news articles loaded")

        if enable_newsapi:
            newsapi_key = get_secret("NEWSAPI_KEY")
            if newsapi_key:
                st.write("Fetching NewsAPI articles...")
                news_records = fetch_newsapi(news_query, newsapi_key)
                all_records.extend(news_records)
                source_counts["newsapi"] = len(news_records)
                st.write(f"  -> {len(news_records)} news articles loaded")
            else:
                st.write("NewsAPI key not configured — skipping.")
                source_counts["newsapi"] = 0

        source_counts["total"] = len(all_records)
        status.update(label=f"Data fetching complete — {len(all_records)} total records", state="complete")

    # Separate metrics and news
    metrics = [r for r in all_records if r.get("record_type") == "metric"]
    news = [r for r in all_records if r.get("record_type") == "news"]

    if not metrics:
        st.error("No metric records were loaded. Enable the NAB CSV source and try again.")
        st.stop()

    # ---- Phase 2: Compute Statistics ----
    with st.spinner("Computing statistics and detecting anomalies..."):
        stats = compute_statistics(metrics, sigma_mult)

    # ---- Phase 3: AI Analysis ----
    openai_key = get_secret("OPENAI_API_KEY")
    anomaly_text = ""
    executive_summary = ""

    if openai_key and OpenAI:
        client = OpenAI(api_key=openai_key)
        with st.status("Running AI analysis...", expanded=True) as ai_status:
            st.write("GPT-4o-mini: Classifying anomalies...")
            anomaly_text = call_anomaly_detector(client, stats)
            st.write("GPT-4o-mini: Generating executive summary...")
            news_context = [{"source": n["source_name"], "title": n["title"], "date": n["timestamp"]} for n in news[:10]]
            executive_summary = call_insights_narrator(client, anomaly_text, news_context)
            ai_status.update(label="AI analysis complete", state="complete")
    else:
        st.info("OpenAI API key not configured. Showing statistical analysis only (no AI narrative).")
        anomaly_text = json.dumps({
            "analysis_summary": "AI analysis unavailable — no API key configured.",
            "confirmed_anomalies": [
                {
                    "record_id": a["record_id"],
                    "timestamp": a["timestamp"],
                    "value": a["metric_value"],
                    "severity": "CRITICAL" if a["metric_value"] > 80 else ("HIGH" if a["metric_value"] > 60 else "MEDIUM"),
                    "reason": f"Value {a['metric_value']}% exceeds threshold {stats['anomaly_threshold']}%"
                }
                for a in stats.get("potential_anomalies", [])
            ],
            "risk_level": "HIGH" if stats.get("potential_anomalies_count", 0) > 3 else "MEDIUM",
        }, indent=2)
        executive_summary = f"""# Madison Transparency Agent - Executive Summary

## Overall System Health: {"CRITICAL" if stats.get("potential_anomalies_count", 0) > 5 else "WARNING" if stats.get("potential_anomalies_count", 0) > 0 else "HEALTHY"}

## Key Findings
- Analyzed {stats['total_records']} CPU utilization records from the NAB benchmark dataset.
- Detected {stats['potential_anomalies_count']} potential anomalies above the {stats['anomaly_threshold']}% threshold ({sigma_mult}σ).
- CPU utilization ranged from {stats['min']}% to {stats['max']}% with an average of {stats['average']}%.

## Recommended Actions
1. Investigate timestamps where CPU exceeded {stats['anomaly_threshold']}%.
2. Set up real-time alerting for values above {round(stats['anomaly_threshold'] * 0.9, 1)}%.
3. Review workload scaling policies.
"""

    # ──────────────────────────────────────────────
    # Output Dashboard
    # ──────────────────────────────────────────────

    report_date = datetime.now().strftime("%A, %B %d, %Y")

    # --- System Health Banner ---
    anomaly_count = stats.get("potential_anomalies_count", 0)
    if anomaly_count == 0:
        health_label, health_class = "HEALTHY", "status-healthy"
    elif anomaly_count <= 5:
        health_label, health_class = "WARNING", "status-warning"
    else:
        health_label, health_class = "CRITICAL", "status-critical"

    st.markdown(f"""
    <div class="{health_class}">
        <strong style="font-size:1.3rem;">System Health: {health_label}</strong><br>
        {anomaly_count} anomalies detected across {stats['total_records']} records &mdash; threshold at {stats['anomaly_threshold']}% ({sigma_mult}σ)
    </div>
    """, unsafe_allow_html=True)

    # --- Metric Cards ---
    st.subheader("Key Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Average CPU", f"{stats['average']}%")
    m2.metric("Min / Max", f"{stats['min']}% / {stats['max']}%")
    m3.metric("Std Deviation", f"{stats['std_dev']}")
    m4.metric("Anomalies", f"{anomaly_count}", delta=f"threshold {stats['anomaly_threshold']}%", delta_color="inverse")

    # --- CPU Utilization Chart ---
    st.subheader("CPU Utilization Over Time")

    df_metrics = pd.DataFrame(metrics)
    df_metrics["timestamp"] = pd.to_datetime(df_metrics["timestamp"], errors="coerce")
    df_metrics = df_metrics.sort_values("timestamp")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_metrics["timestamp"],
        y=df_metrics["metric_value"],
        mode="lines+markers",
        name="CPU Utilization",
        line=dict(color="#1E3A5F", width=2),
        marker=dict(size=5),
    ))
    fig.add_hline(
        y=stats["anomaly_threshold"],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Threshold ({stats['anomaly_threshold']}%)",
        annotation_position="top right",
    )
    fig.add_hline(
        y=stats["average"],
        line_dash="dot",
        line_color="green",
        annotation_text=f"Average ({stats['average']}%)",
        annotation_position="bottom right",
    )

    # Highlight anomaly points
    anomaly_df = df_metrics[df_metrics["metric_value"] > stats["anomaly_threshold"]]
    if not anomaly_df.empty:
        fig.add_trace(go.Scatter(
            x=anomaly_df["timestamp"],
            y=anomaly_df["metric_value"],
            mode="markers",
            name="Anomaly",
            marker=dict(color="red", size=10, symbol="diamond"),
        ))

    fig.update_layout(
        xaxis_title="Timestamp",
        yaxis_title="CPU Utilization (%)",
        template="plotly_white",
        height=420,
        margin=dict(l=40, r=40, t=30, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Anomaly Table ---
    if stats.get("potential_anomalies"):
        st.subheader("Detected Anomalies")
        anom_data = []
        for a in stats["potential_anomalies"]:
            severity = "CRITICAL" if a["metric_value"] > 80 else ("HIGH" if a["metric_value"] > 60 else "MEDIUM")
            anom_data.append({
                "Record ID": a["record_id"],
                "Timestamp": a["timestamp"],
                "CPU (%)": round(a["metric_value"], 2),
                "Severity": severity,
            })
        df_anom = pd.DataFrame(anom_data)

        def color_severity(val):
            colors = {"CRITICAL": "background-color: #f8d7da", "HIGH": "background-color: #fff3cd", "MEDIUM": "background-color: #d1ecf1"}
            return colors.get(val, "")

        st.dataframe(
            df_anom.style.applymap(color_severity, subset=["Severity"]),
            use_container_width=True,
            hide_index=True,
        )

    # --- Executive Summary ---
    st.subheader("Executive Summary")
    st.markdown(executive_summary)

    # --- News Context ---
    if news:
        with st.expander(f"News Context ({len(news)} articles)", expanded=False):
            for n in news[:15]:
                st.markdown(f"""
<div class="news-card">
    <strong>{n['title']}</strong><br>
    <small>{n['source_name']} &mdash; {n['timestamp'][:10] if n.get('timestamp') else 'N/A'}</small><br>
    <span style="color:#555">{n.get('description','')[:150]}</span>
    {"<br><a href='" + n['url'] + "' target='_blank'>Read more</a>" if n.get('url') else ""}
</div>
                """, unsafe_allow_html=True)

    # --- Downloads ---
    st.subheader("Download Reports")
    d1, d2, d3 = st.columns(3)

    html_report = generate_html_report(stats, executive_summary, anomaly_text, report_date)
    json_report = generate_json_report(stats, executive_summary, anomaly_text, source_counts)
    md_report = executive_summary

    with d1:
        st.download_button(
            label="Download HTML Report",
            data=html_report,
            file_name="madison_report.html",
            mime="text/html",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            label="Download JSON Data",
            data=json.dumps(json_report, indent=2, default=str),
            file_name="madison_report.json",
            mime="application/json",
            use_container_width=True,
        )
    with d3:
        st.download_button(
            label="Download Markdown Report",
            data=md_report,
            file_name="madison_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # Store in session state for persistence
    st.session_state["last_stats"] = stats
    st.session_state["last_executive_summary"] = executive_summary
    st.session_state["last_anomaly_text"] = anomaly_text

# Show previous results if available
elif "last_stats" in st.session_state:
    st.info("Showing results from last analysis. Click **Run Analysis** to refresh.")
