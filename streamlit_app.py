import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="SOC Analyst AI",
    page_icon="shield",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://localhost:8000"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d1117;
    color: #e6edf3;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2.5rem; max-width: 1400px; }

.soc-header {
    border-bottom: 1px solid #21262d;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.soc-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: #58a6ff;
    letter-spacing: 0.1em;
}
.soc-status {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.72rem;
    color: #3fb950;
    letter-spacing: 0.15em;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid #21262d;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    color: #8b949e;
    padding: 0.65rem 1.5rem;
    background: transparent;
    border: none;
    text-transform: uppercase;
}
.stTabs [aria-selected="true"] {
    color: #58a6ff;
    border-bottom: 2px solid #58a6ff;
}

.stat-box {
    background: #161b22;
    border: 1px solid #21262d;
    border-top: 2px solid #58a6ff;
    padding: 1rem 1.25rem;
    border-radius: 4px;
}
.stat-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    color: #58a6ff;
    line-height: 1;
}
.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    color: #8b949e;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-top: 0.35rem;
}

.threat-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-left: 3px solid #58a6ff;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
    border-radius: 4px;
}
.threat-critical { border-left-color: #f85149; }
.threat-high     { border-left-color: #d29922; }
.threat-medium   { border-left-color: #58a6ff; }
.threat-low      { border-left-color: #3fb950; }

.severity-critical { color: #f85149; font-weight: 600; }
.severity-high     { color: #d29922; font-weight: 600; }
.severity-medium   { color: #58a6ff; font-weight: 600; }
.severity-low      { color: #3fb950; font-weight: 600; }

.report-box {
    background: #0d1117;
    border: 1px solid #21262d;
    border-left: 3px solid #21262d;
    padding: 1rem 1.25rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #c9d1d9;
    line-height: 1.7;
    white-space: pre-wrap;
    margin-top: 0.5rem;
    border-radius: 4px;
}

.section-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    color: #8b949e;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
    margin-top: 1.5rem;
}

.chat-msg-user {
    background: #1c2128;
    border: 1px solid #21262d;
    border-right: 3px solid #58a6ff;
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.5rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #e6edf3;
    border-radius: 4px;
    text-align: right;
}
.chat-msg-agent {
    background: #161b22;
    border: 1px solid #21262d;
    border-left: 3px solid #3fb950;
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.5rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    color: #c9d1d9;
    border-radius: 4px;
    line-height: 1.6;
}

.error-box {
    background: #1a0d0d;
    border: 1px solid #3d1a1a;
    border-left: 3px solid #f85149;
    padding: 0.75rem 1rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #f85149;
    border-radius: 4px;
}

.stButton > button {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    background: transparent;
    border: 1px solid #58a6ff;
    color: #58a6ff;
    padding: 0.55rem 1.25rem;
    border-radius: 4px;
    width: 100%;
    font-weight: 500;
}
.stButton > button:hover {
    background: #58a6ff;
    color: #0d1117;
}
.stSpinner > div { border-top-color: #58a6ff !important; }

[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
}
.stTextInput > div > div > input {
    background: #161b22;
    border: 1px solid #21262d;
    color: #e6edf3;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
}
.stSelectbox > div > div {
    background: #161b22;
    border: 1px solid #21262d;
    color: #e6edf3;
}
.stFileUploader {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    plot_bgcolor  = "#0d1117",
    paper_bgcolor = "#0d1117",
    font          = dict(family="Inter", color="#8b949e", size=11),
    xaxis         = dict(gridcolor="#21262d", linecolor="#21262d",
                         tickfont=dict(color="#c9d1d9")),
    yaxis         = dict(gridcolor="#21262d", linecolor="#21262d",
                         tickfont=dict(color="#c9d1d9")),
    margin        = dict(l=0, r=0, t=30, b=0),
    legend        = dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#c9d1d9"))
)

SEVERITY_COLORS = {
    "Critical": "#f85149",
    "High":     "#d29922",
    "Medium":   "#58a6ff",
    "Low":      "#3fb950"
}

if "results"      not in st.session_state: st.session_state.results      = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "session_id"   not in st.session_state:
    st.session_state.session_id = f"session_{datetime.now().strftime('%H%M%S')}"

# ══════════════════════════════════════════════════════════════
# SIDEBAR — CHAT
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:1rem;
                font-weight:700;color:#58a6ff;letter-spacing:0.1em;
                padding-bottom:0.75rem;border-bottom:1px solid #21262d;
                margin-bottom:1rem;">
        SOC ANALYST
    </div>
    <div style="font-family:'Inter',sans-serif;font-size:0.82rem;
                color:#8b949e;margin-bottom:1.25rem;line-height:1.6;">
        Ask about threats, attack types, risk scores or security concepts.
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-msg-user">{msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-msg-agent">{msg["content"]}</div>',
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    user_input = st.text_input("Message", placeholder="Ask the analyst...",
                               label_visibility="collapsed", key="chat_input")

    col_send, col_clear = st.columns(2)
    with col_send:  send  = st.button("SEND",  use_container_width=True)
    with col_clear: clear = st.button("CLEAR", use_container_width=True)

    if send and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner(""):
            try:
                resp = requests.post(f"{API_URL}/chat",
                    json={"message": user_input,
                          "session_id": st.session_state.session_id},
                    timeout=120)
                reply = resp.json()["response"] if resp.status_code == 200 \
                        else f"Error {resp.status_code}"
            except Exception as e:
                reply = f"Connection error: {str(e)}"
        st.session_state.chat_history.append({"role": "agent", "content": reply})
        st.rerun()

    if clear:
        st.session_state.chat_history = []
        st.rerun()

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.markdown("""
<div class="soc-header">
    <div class="soc-title">SOC ANALYST AI</div>
    <div class="soc-status">SYSTEM ONLINE</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["ANALYZE", "HISTORY"])

# ══════════════════════════════════════════════════════════════
# TAB 1 — ANALYZE
# ══════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        st.markdown('<div class="section-label">Upload Traffic Log</div>',
                    unsafe_allow_html=True)
        uploaded = st.file_uploader("Upload", type=["csv","txt"],
                                    label_visibility="collapsed")
        run_btn  = st.button("RUN ANALYSIS", use_container_width=True)

        st.markdown("""
        <div style="margin-top:1.5rem">
            <div class="section-label">Model Info</div>
            <div style="font-family:'Inter',sans-serif;font-size:0.82rem;
                        color:#8b949e;line-height:2.0;">
                <span style="color:#c9d1d9;font-weight:500;">Model 1:</span>
                Autoencoder (TF)<br>
                <span style="color:#c9d1d9;font-weight:500;">Model 2:</span>
                Random Forest (sklearn)<br>
                <span style="color:#c9d1d9;font-weight:500;">LLM:</span>
                Llama 3.2:1b via Ollama<br>
                <span style="color:#c9d1d9;font-weight:500;">Dataset:</span>
                NSL-KDD (125,973 samples)<br>
                <span style="color:#c9d1d9;font-weight:500;">Threshold:</span>
                99th percentile<br>
                <span style="color:#c9d1d9;font-weight:500;">F1 Score:</span>
                83.38% weighted
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        if run_btn and uploaded:
            with st.spinner("Scanning traffic log..."):
                try:
                    resp = requests.post(f"{API_URL}/analyze",
                        files={"file": (uploaded.name,
                                        uploaded.getvalue(), "text/csv")},
                        timeout=600)
                    if resp.status_code == 200:
                        st.session_state.results = resp.json()
                    else:
                        st.markdown(
                            f'<div class="error-box">API error {resp.status_code}</div>',
                            unsafe_allow_html=True)
                except requests.exceptions.ConnectionError:
                    st.markdown(
                        '<div class="error-box">Cannot connect to API on port 8000</div>',
                        unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="error-box">{str(e)}</div>',
                                unsafe_allow_html=True)

        if st.session_state.results:
            results = st.session_state.results
            df_r    = pd.DataFrame(results)

            total    = len(results)
            critical = len(df_r[df_r["severity"] == "Critical"])
            high     = len(df_r[df_r["severity"] == "High"])
            avg_risk = int(df_r["risk_score"].mean())

            c1, c2, c3, c4 = st.columns(4)
            for col, val, label, color in [
                (c1, total,           "Threats Detected", "#58a6ff"),
                (c2, critical,        "Critical",         "#f85149"),
                (c3, high,            "High",             "#d29922"),
                (c4, f"{avg_risk}/100","Avg Risk Score",  "#3fb950")
            ]:
                with col:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value" style="color:{color}">{val}</div>
                        <div class="stat-label">{label}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            ch1, ch2 = st.columns(2)
            with ch1:
                st.markdown('<div class="section-label">Attack Frequency</div>',
                            unsafe_allow_html=True)
                freq   = df_r["attack_type"].value_counts()
                colors = ["#f85149","#d29922","#58a6ff","#3fb950","#8b949e"]
                fig1   = go.Figure(go.Bar(
                    x=freq.index, y=freq.values,
                    marker_color=colors[:len(freq)],
                    marker_line_width=0,
                    text=freq.values,
                    textposition="outside",
                    textfont=dict(color="#c9d1d9", size=11)
                ))
                fig1.update_layout(**PLOT_LAYOUT, height=230)
                st.plotly_chart(fig1, use_container_width=True)

            with ch2:
                st.markdown('<div class="section-label">Severity Distribution</div>',
                            unsafe_allow_html=True)
                sev   = df_r["severity"].value_counts()
                scols = [SEVERITY_COLORS.get(s, "#8b949e") for s in sev.index]
                fig2  = go.Figure(go.Pie(
                    labels=sev.index, values=sev.values,
                    marker=dict(colors=scols,
                                line=dict(color="#0d1117", width=2)),
                    textfont=dict(family="Inter", size=11, color="#e6edf3"),
                    hole=0.4
                ))
                fig2.update_layout(**PLOT_LAYOUT, height=230)
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown('<div class="section-label">Risk Score Timeline</div>',
                        unsafe_allow_html=True)
            fig3 = go.Figure(go.Scatter(
                y=df_r["risk_score"],
                mode="lines+markers",
                line=dict(color="#58a6ff", width=2),
                marker=dict(
                    color=[SEVERITY_COLORS.get(s,"#8b949e")
                           for s in df_r["severity"]],
                    size=7, line=dict(color="#0d1117", width=1)
                ),
                fill="tozeroy",
                fillcolor="rgba(88,166,255,0.08)"
            ))
            fig3.update_yaxes(range=[0, 105])
            fig3.update_layout(**PLOT_LAYOUT, height=190)
            st.plotly_chart(fig3, use_container_width=True)

            st.markdown('<div class="section-label">Detected Threats</div>',
                        unsafe_allow_html=True)

            fcol, _ = st.columns([1, 3])
            with fcol:
                types    = ["ALL"] + sorted(df_r["attack_type"].unique().tolist())
                selected = st.selectbox("Filter by type", types,
                                        label_visibility="collapsed")

            filtered = results if selected == "ALL" else \
                       [r for r in results if r["attack_type"] == selected]

            for r in filtered[:30]:
                sev_cls = f"threat-{r['severity'].lower()}"
                sev_col = f"severity-{r['severity'].lower()}"
                with st.expander(
                    f"{r['attack_type']}  |  Risk: {r['risk_score']}/100  |  "
                    f"Confidence: {r['confidence']*100:.1f}%  |  {r['severity']}",
                    expanded=False
                ):
                    st.markdown(f"""
                    <div class="threat-card {sev_cls}">
                        <span style="color:#8b949e;font-size:0.78rem;">ATTACK TYPE</span>
                        <span style="color:#e6edf3;font-weight:600;
                                     margin-left:0.5rem;">{r['attack_type']}</span>
                        &nbsp;&nbsp;&nbsp;
                        <span style="color:#8b949e;font-size:0.78rem;">SEVERITY</span>
                        <span class="{sev_col}" style="margin-left:0.5rem;">
                            {r['severity']}
                        </span>
                        &nbsp;&nbsp;&nbsp;
                        <span style="color:#8b949e;font-size:0.78rem;">RISK</span>
                        <span style="color:#e6edf3;font-weight:600;
                                     margin-left:0.5rem;">{r['risk_score']}/100</span>
                        &nbsp;&nbsp;&nbsp;
                        <span style="color:#8b949e;font-size:0.78rem;">ANOMALY SCORE</span>
                        <span style="color:#e6edf3;margin-left:0.5rem;">
                            {r['anomaly_score']:.4f}
                        </span>
                    </div>
                    <div class="section-label" style="margin-top:0.75rem;">
                        Incident Report
                    </div>
                    <div class="report-box">{r['report']}</div>
                    """, unsafe_allow_html=True)

        elif not run_btn:
            st.markdown("""
            <div style="display:flex;align-items:center;justify-content:center;
                        height:260px;border:1px dashed #21262d;border-radius:4px;">
                <div style="text-align:center">
                    <div style="font-family:'Share Tech Mono',monospace;
                                font-size:1.8rem;color:#21262d;margin-bottom:0.5rem;">
                        +
                    </div>
                    <div style="font-family:'Inter',sans-serif;font-size:0.85rem;
                                color:#8b949e;">
                        Upload a traffic log and run analysis
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# TAB 2 — HISTORY
# ══════════════════════════════════════════════════════════════
with tab2:
    try:
        resp = requests.get(f"{API_URL}/history", timeout=30)
        if resp.status_code == 200:
            incidents = resp.json()["incidents"]
            if incidents:
                df_h = pd.DataFrame(incidents, columns=[
                    "id","attack_type","confidence","anomaly_score",
                    "risk_score","severity","report","timestamp"
                ])

                total_h    = len(df_h)
                critical_h = len(df_h[df_h["severity"] == "Critical"])
                avg_risk_h = int(df_h["risk_score"].mean())
                top_attack = df_h["attack_type"].mode()[0]

                c1, c2, c3, c4 = st.columns(4)
                for col, val, label, color in [
                    (c1, total_h,            "Total Incidents", "#58a6ff"),
                    (c2, critical_h,         "Critical",        "#f85149"),
                    (c3, f"{avg_risk_h}/100","Avg Risk Score",  "#d29922"),
                    (c4, top_attack,         "Top Attack Type", "#3fb950")
                ]:
                    with col:
                        st.markdown(f"""
                        <div class="stat-box">
                            <div class="stat-value"
                                 style="color:{color};font-size:1.4rem">{val}</div>
                            <div class="stat-label">{label}</div>
                        </div>""", unsafe_allow_html=True)

                st.markdown("<div style='height:1.5rem'></div>",
                            unsafe_allow_html=True)

                f1col, f2col, _ = st.columns([1, 1, 2])
                with f1col:
                    tf = st.selectbox("Attack Type",
                        ["ALL"] + sorted(df_h["attack_type"].unique().tolist()))
                with f2col:
                    sf = st.selectbox("Severity",
                        ["ALL","Critical","High","Medium","Low"])

                df_show = df_h.copy()
                if tf != "ALL": df_show = df_show[df_show["attack_type"] == tf]
                if sf != "ALL": df_show = df_show[df_show["severity"]    == sf]

                df_show = df_show.copy()
                df_show["confidence"]    = df_show["confidence"].apply(
                    lambda x: f"{x*100:.1f}%")
                df_show["anomaly_score"] = df_show["anomaly_score"].apply(
                    lambda x: f"{x:.4f}")
                df_show = df_show.drop(["id","report"], axis=1)

                st.markdown('<div class="section-label">Incident Log</div>',
                            unsafe_allow_html=True)
                st.dataframe(df_show, use_container_width=True, hide_index=True)

                st.markdown('<div class="section-label">Attack Frequency Over Time</div>',
                            unsafe_allow_html=True)
                df_h["timestamp"] = pd.to_datetime(df_h["timestamp"])
                df_time = df_h.groupby(
                    [df_h["timestamp"].dt.floor("h"), "attack_type"]
                ).size().reset_index(name="count")

                colors_map = {
                    "DoS":    "#f85149",
                    "Probe":  "#d29922",
                    "R2L":    "#58a6ff",
                    "U2R":    "#3fb950",
                    "normal": "#8b949e"
                }
                fig4 = go.Figure()
                for attack in df_time["attack_type"].unique():
                    sub = df_time[df_time["attack_type"] == attack]
                    fig4.add_trace(go.Scatter(
                        x=sub["timestamp"], y=sub["count"],
                        name=attack, mode="lines+markers",
                        line=dict(color=colors_map.get(attack,"#8b949e"),
                                  width=2),
                        marker=dict(size=6,
                                    line=dict(color="#0d1117", width=1))
                    ))
                fig4.update_layout(**PLOT_LAYOUT, height=280)
                st.plotly_chart(fig4, use_container_width=True)

            else:
                st.markdown("""
                <div style="display:flex;align-items:center;justify-content:center;
                            height:200px;border:1px dashed #21262d;border-radius:4px;">
                    <div style="font-family:'Inter',sans-serif;font-size:0.85rem;
                                color:#8b949e;">No incidents recorded yet</div>
                </div>""", unsafe_allow_html=True)

    except requests.exceptions.ReadTimeout:
        st.markdown('<div class="error-box">Request timed out — try again</div>',
                    unsafe_allow_html=True)
    except requests.exceptions.ConnectionError:
        st.markdown('<div class="error-box">Cannot connect to API on port 8000</div>',
                    unsafe_allow_html=True)