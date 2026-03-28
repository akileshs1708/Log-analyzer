#!/usr/bin/env python3
"""
Streamlit Dashboard – Hadoop Web Server Log Analysis
Visualizes all 13 MapReduce job results with rich interactive charts.
Run: streamlit run streamlit_app/app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, glob
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hadoop Log Analytics",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme constants ────────────────────────────────────────────────────────────
DARK_BG    = "#0d1117"
CARD_BG    = "#161b22"
BORDER     = "#30363d"
ACCENT     = "#58a6ff"
ACCENT2    = "#f78166"
ACCENT3    = "#3fb950"
ACCENT4    = "#d2a8ff"
TEXT_MAIN  = "#e6edf3"
TEXT_DIM   = "#8b949e"

PALETTE = [ACCENT, ACCENT2, ACCENT3, ACCENT4,
           "#ffa657", "#79c0ff", "#ff7b72", "#56d364",
           "#e3b341", "#bc8cff"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'IBM Plex Mono', monospace", color=TEXT_MAIN, size=12),
    margin=dict(l=12, r=12, t=36, b=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER),
    xaxis=dict(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER),
    yaxis=dict(gridcolor=BORDER, linecolor=BORDER, zerolinecolor=BORDER),
)

# ── CSS injection ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: {DARK_BG};
    color: {TEXT_MAIN};
}}
.stApp {{ background-color: {DARK_BG}; }}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: {CARD_BG} !important;
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] * {{ color: {TEXT_MAIN} !important; }}

/* Metric cards */
[data-testid="stMetric"] {{
    background: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 16px 20px;
}}
[data-testid="stMetricValue"] {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.8rem !important;
    color: {ACCENT} !important;
}}
[data-testid="stMetricLabel"] {{
    color: {TEXT_DIM} !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
[data-testid="stMetricDelta"] {{ color: {ACCENT3} !important; }}

/* Tabs */
[data-testid="stTabs"] button {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: {TEXT_DIM} !important;
    border-bottom: 2px solid transparent;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {ACCENT} !important;
    border-bottom: 2px solid {ACCENT} !important;
}}

/* Dataframes */
[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 6px; }}

/* Section headers */
.section-header {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: {TEXT_DIM};
    margin: 24px 0 8px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid {BORDER};
}}
.hero-title {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2.2rem;
    font-weight: 600;
    color: {TEXT_MAIN};
    letter-spacing: -0.02em;
}}
.hero-sub {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: {TEXT_DIM};
    margin-top: 4px;
}}
.badge {{
    display: inline-block;
    background: rgba(88,166,255,0.12);
    border: 1px solid rgba(88,166,255,0.3);
    color: {ACCENT};
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    padding: 2px 10px;
    border-radius: 12px;
    margin-right: 6px;
}}
.risk-high   {{ color: {ACCENT2}; font-weight: 600; }}
.risk-medium {{ color: #ffa657; font-weight: 600; }}
.risk-low    {{ color: {ACCENT3}; }}
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
RESULTS_DIR = Path(__file__).parent.parent / "results"

@st.cache_data(ttl=60)
def load_tsv(filename, cols):
    path = RESULTS_DIR / filename
    if not path.exists():
        return pd.DataFrame(columns=cols)
    return pd.read_csv(path, sep="\t", header=None, names=cols)

def fmt_bytes(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

def bar(df, x, y, title, color=ACCENT, horizontal=False, top_n=20):
    df = df.head(top_n)
    if horizontal:
        fig = px.bar(df, x=y, y=x, orientation="h", title=title,
                     color_discrete_sequence=[color])
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(**PLOTLY_LAYOUT)
    else:
        fig = px.bar(df, x=x, y=y, title=title,
                     color_discrete_sequence=[color])
        fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_traces(marker_line_width=0)
    return fig

def pie(df, names, values, title):
    fig = px.pie(df, names=names, values=values, title=title,
                 color_discrete_sequence=PALETTE, hole=0.45)
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_traces(textposition="outside", textinfo="percent+label",
                      marker=dict(line=dict(color=DARK_BG, width=2)))
    return fig

def line(df, x, y, title, color=ACCENT):
    fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=[color])
    fig.update_traces(line_width=2)
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig

# ── Load all datasets ──────────────────────────────────────────────────────────
df_ip     = load_tsv("q01_ip_requests.tsv",     ["ip", "requests"])
df_url    = load_tsv("q02_url_requests.tsv",     ["url", "requests"])
df_time   = load_tsv("q03_time_requests.tsv",    ["key", "requests"])
df_status = load_tsv("q04_status_codes.tsv",     ["status", "count"])
df_bw     = load_tsv("q05_bandwidth.tsv",        ["url", "bytes"])
df_err    = load_tsv("q06_error_urls.tsv",       ["url", "status", "count"])
df_meth   = load_tsv("q07_http_methods.tsv",     ["method", "count"])
df_brow   = load_tsv("q08_browsers.tsv",         ["browser", "count"])
df_dev    = load_tsv("q09_devices.tsv",          ["device", "count"])
df_resp   = load_tsv("q10_response_time.tsv",    ["url", "avg_ms", "req_count"])
df_ref    = load_tsv("q11_referrers.tsv",        ["domain", "count"])
df_hour   = load_tsv("q12_hourly_pattern.tsv",   ["hour", "count"])
df_susp   = load_tsv("q13_suspicious_ips.tsv",   ["ip", "errors", "sensitive", "bots", "risk"])

# Split q03 into days and hours
df_days = df_time[df_time["key"].str.startswith("day:")].copy()
df_days["date"] = df_days["key"].str.replace("day:", "")
df_days = df_days.sort_values("date")

df_hours_ts = df_time[df_time["key"].str.startswith("hour:")].copy()
df_hours_ts["datetime"] = df_hours_ts["key"].str.replace("hour:", "")
df_hours_ts = df_hours_ts.sort_values("datetime")

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_reqs    = df_ip["requests"].sum() if not df_ip.empty else 0
unique_ips    = len(df_ip)
total_bytes   = df_bw["bytes"].sum() if not df_bw.empty else 0
error_reqs    = df_status[df_status["status"].astype(str).str.startswith(("4","5"))]["count"].sum() if not df_status.empty else 0
error_rate    = (error_reqs / total_reqs * 100) if total_reqs else 0
top_url       = df_url.iloc[0]["url"] if not df_url.empty else "—"
top_url_reqs  = df_url.iloc[0]["requests"] if not df_url.empty else 0
avg_resp      = df_resp["avg_ms"].mean() if not df_resp.empty else 0
suspicious    = len(df_susp[df_susp["risk"] >= 10]) if not df_susp.empty else 0

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 16px 0 8px 0;'>
        <div style='font-family: IBM Plex Mono, monospace; font-size:1.1rem; font-weight:600; color:#e6edf3;'>
            🪵 LogAnalytics
        </div>
        <div style='font-size:0.72rem; color:#8b949e; margin-top:4px;'>
            Hadoop MapReduce · Python
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-header'>Navigation</div>", unsafe_allow_html=True)
    page = st.radio("Select Page", [
        "📊 Overview",
        "🌐 Traffic Analysis",
        "⚠️ Errors & Status",
        "👤 Clients & Devices",
        "⚡ Performance",
        "🔴 Security",
        "📁 Raw Results",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<div class='section-header'>Dataset</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 0.78rem; color: {TEXT_DIM};'>
    <div>📄 access.log</div>
    <div style='margin-top:4px;'>Entries: <span style='color:{ACCENT};'>{total_reqs:,}</span></div>
    <div>Unique IPs: <span style='color:{ACCENT};'>{unique_ips:,}</span></div>
    <div>Bandwidth: <span style='color:{ACCENT};'>{fmt_bytes(total_bytes)}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-header'>MapReduce Jobs</div>", unsafe_allow_html=True)
    jobs_list = [
        ("Q01","Requests/IP"),("Q02","Top URLs"),("Q03","Time Series"),
        ("Q04","Status Codes"),("Q05","Bandwidth"),("Q06","Error URLs"),
        ("Q07","HTTP Methods"),("Q08","Browsers"),("Q09","Devices"),
        ("Q10","Response Time"),("Q11","Referrers"),("Q12","Hourly Pattern"),
        ("Q13","Security"),
    ]
    for qid, qname in jobs_list:
        st.markdown(
            f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
            f"color:{TEXT_DIM};padding:2px 0;'>"
            f"<span style='color:{ACCENT};'>{qid}</span> {qname}</div>",
            unsafe_allow_html=True
        )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    st.markdown("""
    <div class='hero-title'>Web Server Log Analytics</div>
    <div class='hero-sub'>Apache access.log · Hadoop MapReduce · 13 Analysis Jobs</div>
    <br/>
    """, unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Total Requests",  f"{total_reqs:,}")
    k2.metric("Unique IPs",      f"{unique_ips:,}")
    k3.metric("Bandwidth",       fmt_bytes(total_bytes))
    k4.metric("Error Rate",      f"{error_rate:.1f}%",   delta=f"-{error_rate:.1f}%" if error_rate < 15 else None)
    k5.metric("Avg Response",    f"{avg_resp:.0f} ms")
    k6.metric("Suspicious IPs",  f"{suspicious}",        delta_color="inverse")

    st.markdown("<br/>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 2])

    with c1:
        st.markdown("<div class='section-header'>Daily Traffic Volume (Q03)</div>", unsafe_allow_html=True)
        if not df_days.empty:
            fig = line(df_days, "date", "requests", "Requests per Day", ACCENT)
            fig.update_layout(height=280)
            st.plotly_chart(fig, width="stretch")

    with c2:
        st.markdown("<div class='section-header'>HTTP Status Distribution (Q04)</div>", unsafe_allow_html=True)
        if not df_status.empty:
            df_status["label"] = df_status["status"].astype(str)
            fig = pie(df_status, "label", "count", "Status Codes")
            fig.update_layout(height=280)
            st.plotly_chart(fig, width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("<div class='section-header'>Top 10 IPs by Request Count (Q01)</div>", unsafe_allow_html=True)
        if not df_ip.empty:
            fig = bar(df_ip, "ip", "requests", "Top IPs", ACCENT2, horizontal=True, top_n=10)
            fig.update_layout(height=300)
            st.plotly_chart(fig, width="stretch")

    with c4:
        st.markdown("<div class='section-header'>Top 10 Requested URLs (Q02)</div>", unsafe_allow_html=True)
        if not df_url.empty:
            fig = bar(df_url, "url", "requests", "Top URLs", ACCENT3, horizontal=True, top_n=10)
            fig.update_layout(height=300)
            st.plotly_chart(fig, width="stretch")

    # Summary table
    st.markdown("<div class='section-header'>All 13 MapReduce Jobs – Summary</div>", unsafe_allow_html=True)
    summary = pd.DataFrame([
        {"#": "Q01", "Question": "How many requests per IP address?",             "Output Rows": len(df_ip),     "Top Result": f"{df_ip.iloc[0]['ip']} ({df_ip.iloc[0]['requests']:,} reqs)" if not df_ip.empty else "—"},
        {"#": "Q02", "Question": "Most requested URLs?",                           "Output Rows": len(df_url),    "Top Result": f"{df_url.iloc[0]['url']} ({df_url.iloc[0]['requests']:,})" if not df_url.empty else "—"},
        {"#": "Q03", "Question": "Requests per day and per hour?",                 "Output Rows": len(df_time),   "Top Result": f"{len(df_days)} days, {len(df_hours_ts)} hourly slots"},
        {"#": "Q04", "Question": "HTTP status code distribution?",                 "Output Rows": len(df_status), "Top Result": f"200 OK: {df_status[df_status['status']==200]['count'].sum():,}" if not df_status.empty else "—"},
        {"#": "Q05", "Question": "Which URLs consume most bandwidth?",             "Output Rows": len(df_bw),     "Top Result": f"{df_bw.iloc[0]['url']} ({fmt_bytes(df_bw.iloc[0]['bytes'])})" if not df_bw.empty else "—"},
        {"#": "Q06", "Question": "Which URLs generate most errors (4xx/5xx)?",     "Output Rows": len(df_err),    "Top Result": f"{df_err.iloc[0]['url']} → {df_err.iloc[0]['status']}" if not df_err.empty else "—"},
        {"#": "Q07", "Question": "HTTP method distribution (GET/POST/...)?",       "Output Rows": len(df_meth),   "Top Result": f"{df_meth.iloc[0]['method']}: {df_meth.iloc[0]['count']:,}" if not df_meth.empty else "—"},
        {"#": "Q08", "Question": "Which browsers are most used?",                  "Output Rows": len(df_brow),   "Top Result": f"{df_brow.iloc[0]['browser']}: {df_brow.iloc[0]['count']:,}" if not df_brow.empty else "—"},
        {"#": "Q09", "Question": "Device type breakdown (Desktop/Mobile/Bot)?",    "Output Rows": len(df_dev),    "Top Result": f"{df_dev.iloc[0]['device']}: {df_dev.iloc[0]['count']:,}" if not df_dev.empty else "—"},
        {"#": "Q10", "Question": "Average response time per URL?",                 "Output Rows": len(df_resp),   "Top Result": f"{df_resp.iloc[0]['url']} → {df_resp.iloc[0]['avg_ms']:.0f} ms" if not df_resp.empty else "—"},
        {"#": "Q11", "Question": "Top referrer domains (traffic sources)?",        "Output Rows": len(df_ref),    "Top Result": f"{df_ref.iloc[0]['domain']}: {df_ref.iloc[0]['count']:,}" if not df_ref.empty else "—"},
        {"#": "Q12", "Question": "Hourly traffic pattern across the day (0–23)?",  "Output Rows": len(df_hour),   "Top Result": f"Peak hour: {df_hour.loc[df_hour['count'].idxmax(),'hour']}:00" if not df_hour.empty else "—"},
        {"#": "Q13", "Question": "Which IPs show suspicious / attack behavior?",   "Output Rows": len(df_susp),   "Top Result": f"{suspicious} high-risk IPs detected"},
    ])
    st.dataframe(summary, width="stretch", hide_index=True,
                 column_config={"#": st.column_config.TextColumn(width=50)})


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TRAFFIC ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🌐 Traffic Analysis":
    st.markdown("<div class='hero-title'>Traffic Analysis</div><br/>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Q01 · IP Requests", "Q02 · Top URLs", "Q03 · Time Series", "Q05 · Bandwidth"])

    with tab1:
        st.markdown("<div class='section-header'>Q01 – Requests per IP Address</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 2])
        with c1:
            topn = st.slider("Show top N IPs", 5, 50, 20, key="ip_n")
            fig = bar(df_ip, "ip", "requests", f"Top {topn} IPs by Request Count",
                      ACCENT, horizontal=True, top_n=topn)
            fig.update_layout(height=max(300, topn * 22))
            st.plotly_chart(fig, width="stretch")
        with c2:
            st.markdown("**Full IP table**")
            st.dataframe(df_ip.head(100), width="stretch", hide_index=True)

    with tab2:
        st.markdown("<div class='section-header'>Q02 – Most Requested URLs</div>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 2])
        with c1:
            fig = bar(df_url, "url", "requests", "Top URLs by Request Count",
                      ACCENT3, horizontal=True, top_n=20)
            fig.update_layout(height=500)
            st.plotly_chart(fig, width="stretch")
        with c2:
            st.dataframe(df_url, width="stretch", hide_index=True)

    with tab3:
        st.markdown("<div class='section-header'>Q03 – Requests per Day & Hour</div>", unsafe_allow_html=True)

        st.markdown("**Daily Traffic**")
        fig = line(df_days, "date", "requests", "Requests per Day")
        fig.update_layout(height=260)
        st.plotly_chart(fig, width="stretch")

        st.markdown("**Hourly Traffic (all dates)**")
        if not df_hours_ts.empty:
            fig2 = px.line(df_hours_ts.head(500), x="datetime", y="requests",
                           title="Requests per Hour (sample)",
                           color_discrete_sequence=[ACCENT4])
            fig2.update_layout(**PLOTLY_LAYOUT, height=260)
            st.plotly_chart(fig2, width="stretch")

        st.dataframe(df_days, width="stretch", hide_index=True)

    with tab4:
        st.markdown("<div class='section-header'>Q05 – Bandwidth per URL</div>", unsafe_allow_html=True)
        df_bw2 = df_bw.copy()
        df_bw2["bytes_mb"] = df_bw2["bytes"] / (1024 * 1024)
        df_bw2["label"] = df_bw2["bytes"].apply(fmt_bytes)
        c1, c2 = st.columns([3, 2])
        with c1:
            fig = bar(df_bw2, "url", "bytes_mb", "Bandwidth per URL (MB)",
                      "#ffa657", horizontal=True)
            fig.update_layout(height=400)
            st.plotly_chart(fig, width="stretch")
        with c2:
            st.dataframe(df_bw2[["url","label"]]
                         .rename(columns={"label":"bandwidth"}),
                         width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ERRORS & STATUS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚠️ Errors & Status":
    st.markdown("<div class='hero-title'>Errors & HTTP Status</div><br/>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Q04 · Status Codes", "Q06 · Error URLs"])

    with tab1:
        st.markdown("<div class='section-header'>Q04 – HTTP Status Code Distribution</div>", unsafe_allow_html=True)
        df_s = df_status.copy()
        df_s["class"] = df_s["status"].astype(str).str[0] + "xx"
        df_s["label"] = df_s["status"].astype(str)

        c1, c2 = st.columns(2)
        with c1:
            fig = pie(df_s, "label", "count", "Status Code Breakdown")
            fig.update_layout(height=360)
            st.plotly_chart(fig, width="stretch")
        with c2:
            # Grouped by class
            df_class = df_s.groupby("class")["count"].sum().reset_index()
            fig2 = pie(df_class, "class", "count", "By Status Class")
            fig2.update_layout(height=360)
            st.plotly_chart(fig2, width="stretch")

        st.dataframe(df_s[["status","count","class"]], width="stretch", hide_index=True)

    with tab2:
        st.markdown("<div class='section-header'>Q06 – Top Error-Generating URLs</div>", unsafe_allow_html=True)
        if not df_err.empty:
            status_filter = st.multiselect("Filter by status code",
                                           df_err["status"].unique().tolist(),
                                           default=df_err["status"].unique().tolist())
            df_err_f = df_err[df_err["status"].isin(status_filter)]

            fig = px.bar(df_err_f.head(20), x="count", y="url", color="status",
                         orientation="h", title="Top Error URLs",
                         color_discrete_sequence=PALETTE)
            fig.update_layout(**PLOTLY_LAYOUT, height=450)
            st.plotly_chart(fig, width="stretch")
            st.dataframe(df_err_f, width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CLIENTS & DEVICES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Clients & Devices":
    st.markdown("<div class='hero-title'>Clients & Devices</div><br/>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Q07 · HTTP Methods", "Q08 · Browsers", "Q09 · Devices", "Q11 · Referrers"
    ])

    with tab1:
        st.markdown("<div class='section-header'>Q07 – HTTP Method Distribution</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            fig = pie(df_meth, "method", "count", "HTTP Methods")
            fig.update_layout(height=380)
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig2 = bar(df_meth.sort_values("count", ascending=False),
                       "method", "count", "HTTP Methods", ACCENT)
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, width="stretch")
        st.dataframe(df_meth, width="stretch", hide_index=True)

    with tab2:
        st.markdown("<div class='section-header'>Q08 – Browser Family Distribution</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            fig = pie(df_brow, "browser", "count", "Browser Families")
            fig.update_layout(height=380)
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig2 = bar(df_brow, "browser", "count", "Browser Counts", ACCENT4)
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, width="stretch")
        st.dataframe(df_brow, width="stretch", hide_index=True)

    with tab3:
        st.markdown("<div class='section-header'>Q09 – Device Type Breakdown</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            fig = pie(df_dev, "device", "count", "Device Types")
            fig.update_layout(height=380)
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig2 = bar(df_dev, "device", "count", "Device Counts", ACCENT3)
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, width="stretch")
        st.dataframe(df_dev, width="stretch", hide_index=True)

    with tab4:
        st.markdown("<div class='section-header'>Q11 – Top Traffic Sources (Referrers)</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            fig = pie(df_ref, "domain", "count", "Referrer Domains")
            fig.update_layout(height=380)
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig2 = bar(df_ref, "domain", "count", "Referrer Counts", "#e3b341", horizontal=True)
            fig2.update_layout(height=380)
            st.plotly_chart(fig2, width="stretch")
        st.dataframe(df_ref, width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚡ Performance":
    st.markdown("<div class='hero-title'>Performance Analysis</div><br/>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Q10 · Response Times", "Q12 · Hourly Pattern"])

    with tab1:
        st.markdown("<div class='section-header'>Q10 – Average Response Time per URL</div>", unsafe_allow_html=True)

        if not df_resp.empty:
            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Overall Avg",    f"{df_resp['avg_ms'].mean():.0f} ms")
            k2.metric("Slowest URL",    f"{df_resp['avg_ms'].max():.0f} ms")
            k3.metric("Fastest URL",    f"{df_resp['avg_ms'].min():.0f} ms")
            k4.metric("URLs Analyzed",  f"{len(df_resp)}")

            c1, c2 = st.columns([3, 2])
            with c1:
                fig = bar(df_resp.sort_values("avg_ms", ascending=False),
                          "url", "avg_ms", "Slowest URLs (Avg ms)", ACCENT2, horizontal=True)
                fig.update_layout(height=400)
                st.plotly_chart(fig, width="stretch")
            with c2:
                # Scatter: requests vs response time
                fig2 = px.scatter(df_resp, x="req_count", y="avg_ms", text="url",
                                  title="Request Count vs Avg Response",
                                  color="avg_ms",
                                  color_continuous_scale=["#3fb950", "#ffa657", "#f78166"])
                fig2.update_traces(textposition="top center", textfont_size=9)
                fig2.update_layout(**PLOTLY_LAYOUT, height=400,
                                   coloraxis_showscale=False)
                st.plotly_chart(fig2, width="stretch")

            st.dataframe(df_resp.sort_values("avg_ms", ascending=False),
                         width="stretch", hide_index=True)

    with tab2:
        st.markdown("<div class='section-header'>Q12 – Traffic by Hour of Day (0–23)</div>", unsafe_allow_html=True)
        if not df_hour.empty:
            peak_hour = df_hour.loc[df_hour["count"].idxmax(), "hour"]
            low_hour  = df_hour.loc[df_hour["count"].idxmin(), "hour"]

            k1, k2, k3 = st.columns(3)
            k1.metric("Peak Hour",    f"{peak_hour}:00")
            k2.metric("Lowest Hour",  f"{low_hour}:00")
            k3.metric("Peak Requests",f"{df_hour['count'].max():,}")

            # Polar / radar chart for 24h pattern
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[f"{h}:00" for h in df_hour["hour"]],
                y=df_hour["count"],
                marker=dict(
                    color=df_hour["count"],
                    colorscale=[[0, "#1c2a1e"], [0.5, ACCENT3], [1.0, ACCENT]],
                    line_width=0,
                ),
                name="Requests"
            ))
            fig.update_layout(**PLOTLY_LAYOUT,
                              title="Requests by Hour of Day",
                              height=340)
            st.plotly_chart(fig, width="stretch")

            # Heatmap-style area
            fig2 = go.Figure(go.Scatter(
                x=[f"{h}:00" for h in df_hour["hour"]],
                y=df_hour["count"],
                fill="tozeroy",
                line=dict(color=ACCENT, width=2),
                fillcolor=f"rgba(88,166,255,0.15)",
            ))
            fig2.update_layout(**PLOTLY_LAYOUT, title="Traffic Curve (Area)", height=260)
            st.plotly_chart(fig2, width="stretch")

            st.dataframe(df_hour, width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SECURITY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔴 Security":
    st.markdown("<div class='hero-title'>Security Analysis</div><br/>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>Q13 – Suspicious IP Detection</div>", unsafe_allow_html=True)

    if not df_susp.empty:
        # Risk tiers
        high   = df_susp[df_susp["risk"] >= 50]
        medium = df_susp[(df_susp["risk"] >= 10) & (df_susp["risk"] < 50)]
        low    = df_susp[df_susp["risk"] < 10]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🔴 High Risk IPs",   len(high))
        k2.metric("🟠 Medium Risk IPs", len(medium))
        k3.metric("🟢 Low Risk IPs",    len(low))
        k4.metric("Total Flagged",       len(df_susp))

        c1, c2 = st.columns([3, 2])

        with c1:
            top_risk = df_susp.sort_values("risk", ascending=False).head(20)
            fig = go.Figure()
            fig.add_trace(go.Bar(name="Error Hits",     x=top_risk["ip"], y=top_risk["errors"],    marker_color=ACCENT2))
            fig.add_trace(go.Bar(name="Sensitive Paths",x=top_risk["ip"], y=top_risk["sensitive"],  marker_color="#ffa657"))
            fig.add_trace(go.Bar(name="Bot Signals",    x=top_risk["ip"], y=top_risk["bots"],       marker_color=ACCENT4))
            fig.update_xaxes(tickangle=45, gridcolor=BORDER)
            fig.update_layout(**PLOTLY_LAYOUT,
                            barmode="stack",
                            title="Top 20 Suspicious IPs – Signal Breakdown",
                            height=380)
            st.plotly_chart(fig, width="stretch")

        with c2:
            fig2 = px.scatter(df_susp, x="errors", y="sensitive", size="risk",
                              color="risk",
                              hover_data=["ip", "bots"],
                              color_continuous_scale=["#3fb950", "#ffa657", "#f78166"],
                              title="Error Count vs Sensitive Path Hits",
                              size_max=30)
            fig2.update_layout(**PLOTLY_LAYOUT, height=380, coloraxis_showscale=False)
            st.plotly_chart(fig2, width="stretch")

        # Risk table with coloring
        st.markdown("**All Flagged IPs (sorted by risk score)**")

        def risk_label(r):
            if r >= 50: return "🔴 HIGH"
            if r >= 10: return "🟠 MEDIUM"
            return "🟢 LOW"

        df_display = df_susp.sort_values("risk", ascending=False).copy()
        df_display["risk_level"] = df_display["risk"].apply(risk_label)
        st.dataframe(
            df_display[["ip","errors","sensitive","bots","risk","risk_level"]],
            width="stretch",
            hide_index=True,
            column_config={
                "risk": st.column_config.ProgressColumn(
                    "Risk Score", min_value=0, max_value=int(df_susp["risk"].max() or 100)
                ),
            }
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RAW RESULTS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📁 Raw Results":
    st.markdown("<div class='hero-title'>Raw MapReduce Results</div><br/>", unsafe_allow_html=True)

    files = sorted(RESULTS_DIR.glob("*.tsv"))
    if not files:
        st.warning(f"No result files found in {RESULTS_DIR}. Run the MapReduce jobs first.")
    else:
        selected_file = st.selectbox(
            "Select result file",
            [f.name for f in files],
            format_func=lambda n: n.replace(".tsv", "").replace("_", " ").upper()
        )
        fpath = RESULTS_DIR / selected_file
        df_raw = pd.read_csv(fpath, sep="\t", header=None)
        df_raw.columns = [f"col_{i+1}" for i in range(df_raw.shape[1])]

        k1, k2, k3 = st.columns(3)
        k1.metric("Rows",    f"{len(df_raw):,}")
        k2.metric("Columns", f"{df_raw.shape[1]}")
        k3.metric("File",    selected_file)

        st.dataframe(df_raw, width="stretch", hide_index=True)

        # Download button
        csv = df_raw.to_csv(index=False)
        st.download_button(
            "⬇ Download as CSV",
            data=csv,
            file_name=selected_file.replace(".tsv", ".csv"),
            mime="text/csv"
        )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='margin-top:48px; border-top:1px solid {BORDER}; padding-top:16px;
     font-family:IBM Plex Mono,monospace; font-size:0.72rem; color:{TEXT_DIM};
     display:flex; justify-content:space-between;'>
  <span>Hadoop Web Log Analytics · Python MapReduce · 13 Jobs</span>
  <span>HDFS · YARN · Hadoop Streaming · Streamlit · Plotly</span>
</div>
""", unsafe_allow_html=True)
