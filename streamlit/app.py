import streamlit as st
from utils.styles import inject_css

st.set_page_config(page_title="F1 Analytics", layout="wide")
inject_css()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');

/* ── HERO ──────────────────────────────────────────── */
.f1-hero {
    padding: 2.5rem 0 1.8rem;
}
.f1-badge {
    display: inline-block;
    background: #E8002D;
    color: #fff;
    font-family: 'Inter', sans-serif;
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    padding: 0.22rem 0.75rem;
    border-radius: 2px;
    margin-bottom: 1.1rem;
}
.f1-heading {
    font-family: 'Inter', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 900;
    line-height: 0.92;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    margin: 0 0 1.1rem;
}
.f1-heading em {
    font-style: normal;
    color: #E8002D;
}
.f1-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 300;
    color: #666;
    max-width: 520px;
    line-height: 1.65;
    margin: 0;
}

/* ── SPEED LINE ─────────────────────────────────────── */
.speed-bar {
    margin: 2rem 0;
    height: 2px;
    background: #181818;
    position: relative;
    overflow: hidden;
    border-radius: 2px;
}
.speed-bar::after {
    content: "";
    position: absolute;
    top: 0; left: -55%;
    width: 55%; height: 100%;
    background: linear-gradient(90deg, transparent, #E8002D 50%, transparent);
    animation: sweep 2.2s ease-in-out infinite;
}
@keyframes sweep {
    0%   { left: -55%; }
    100% { left: 110%; }
}

/* ── STATS ──────────────────────────────────────────── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: #222;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 2.8rem;
}
.s-card {
    background: #161616;
    padding: 1.6rem 1rem 1.4rem;
    text-align: center;
    transition: background 0.18s;
}
.s-card:hover { background: #1E1E1E; }
.s-num {
    display: block;
    font-family: 'Inter', sans-serif;
    font-size: 2.8rem;
    font-weight: 900;
    color: #E8002D;
    line-height: 1;
    animation: numIn 0.5s ease both;
}
.s-card:nth-child(1) .s-num { animation-delay: 0.05s; }
.s-card:nth-child(2) .s-num { animation-delay: 0.15s; }
.s-card:nth-child(3) .s-num { animation-delay: 0.25s; }
.s-card:nth-child(4) .s-num { animation-delay: 0.35s; }
@keyframes numIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.s-lbl {
    display: block;
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    font-weight: 600;
    color: #444;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    margin-top: 0.4rem;
}

/* ── PIPELINE ───────────────────────────────────────── */
.arch-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.58rem;
    font-weight: 700;
    color: #3A3A3A;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin-bottom: 1rem;
}
.pipeline {
    display: flex;
    align-items: center;
    overflow-x: auto;
    padding-bottom: 2px;
    margin-bottom: 0.65rem;
}
.pnode {
    background: #161616;
    border: 1px solid #252525;
    border-radius: 6px;
    padding: 0.9rem 1.15rem;
    text-align: center;
    flex-shrink: 0;
    min-width: 108px;
    transition: border-color 0.2s;
    cursor: default;
}
.pnode:hover { border-color: #E8002D; }
.pnode-phase {
    font-family: 'Inter', sans-serif;
    font-size: 0.52rem;
    font-weight: 700;
    color: #E8002D;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    display: block;
    margin-bottom: 0.3rem;
}
.pnode-name {
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    color: #F0F0F0;
    line-height: 1.25;
    display: block;
}
.pnode-tech {
    font-family: 'Inter', sans-serif;
    font-size: 0.62rem;
    color: #444;
    display: block;
    margin-top: 0.28rem;
    line-height: 1.4;
}
.pconn {
    flex: 1;
    height: 2px;
    background: #202020;
    position: relative;
    overflow: hidden;
    min-width: 28px;
}
.pdot {
    position: absolute;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #E8002D;
    top: -2px;
    opacity: 0;
    animation: pdot 1.8s linear infinite;
}
.pdot:nth-child(2) { animation-delay: 0.6s; }
.pdot:nth-child(3) { animation-delay: 1.2s; }
@keyframes pdot {
    0%   { left: -8px;  opacity: 0; }
    12%  { opacity: 1; }
    88%  { opacity: 1; }
    100% { left: calc(100% + 8px); opacity: 0; }
}
.orch-note {
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    color: #333;
    letter-spacing: 0.02em;
}
.orch-note span { color: #555; font-weight: 600; }

/* ── FOOTER ─────────────────────────────────────────── */
.page-foot {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 2.2rem;
    padding-top: 1.4rem;
    border-top: 1px solid #1A1A1A;
    flex-wrap: wrap;
    gap: 1rem;
}
.foot-hint {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #3A3A3A;
    line-height: 1.5;
}
.foot-hint strong { color: #777; font-weight: 600; }
.gh-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: #161616;
    border: 1px solid #252525;
    border-radius: 4px;
    padding: 0.5rem 1.05rem;
    color: #777 !important;
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    text-decoration: none !important;
    transition: border-color 0.2s, color 0.2s;
    white-space: nowrap;
}
.gh-btn:hover { border-color: #E8002D; color: #fff !important; }
</style>

<!-- HERO -->
<div class="f1-hero">
    <div class="f1-badge">2024 Formula One Season</div>
    <div class="f1-heading">F1 ANALYTICS<br><em>PIPELINE</em></div>
    <p class="f1-sub">
        An end-to-end data engineering portfolio project — ingesting race telemetry
        from multiple APIs, transforming it in BigQuery via dbt, and serving
        live insights through this dashboard.
    </p>
</div>

<div class="speed-bar"></div>

<!-- STATS -->
<div class="stats-grid">
    <div class="s-card">
        <span class="s-num">24</span>
        <span class="s-lbl">Races</span>
    </div>
    <div class="s-card">
        <span class="s-num">20</span>
        <span class="s-lbl">Drivers</span>
    </div>
    <div class="s-card">
        <span class="s-num">10</span>
        <span class="s-lbl">Constructors</span>
    </div>
    <div class="s-card">
        <span class="s-num">3</span>
        <span class="s-lbl">Data Sources</span>
    </div>
</div>

<!-- PIPELINE ARCHITECTURE -->
<div class="arch-label">Pipeline Architecture</div>
<div class="pipeline">

    <div class="pnode">
        <span class="pnode-phase">Ingest</span>
        <span class="pnode-name">FastF1<br>Jolpica</span>
        <span class="pnode-tech">Python · dlt</span>
    </div>

    <div class="pconn">
        <div class="pdot"></div><div class="pdot"></div><div class="pdot"></div>
    </div>

    <div class="pnode">
        <span class="pnode-phase">Store</span>
        <span class="pnode-name">Cloud<br>Storage</span>
        <span class="pnode-tech">GCS · Parquet</span>
    </div>

    <div class="pconn">
        <div class="pdot"></div><div class="pdot"></div><div class="pdot"></div>
    </div>

    <div class="pnode">
        <span class="pnode-phase">Warehouse</span>
        <span class="pnode-name">BigQuery</span>
        <span class="pnode-tech">Raw · Staging<br>Intermediate</span>
    </div>

    <div class="pconn">
        <div class="pdot"></div><div class="pdot"></div><div class="pdot"></div>
    </div>

    <div class="pnode">
        <span class="pnode-phase">Transform</span>
        <span class="pnode-name">dbt Core</span>
        <span class="pnode-tech">Staging → Marts<br>SCD2 Snapshots</span>
    </div>

    <div class="pconn">
        <div class="pdot"></div><div class="pdot"></div><div class="pdot"></div>
    </div>

    <div class="pnode">
        <span class="pnode-phase">Serve</span>
        <span class="pnode-name">Streamlit</span>
        <span class="pnode-tech">Community Cloud<br>Auto-deploy</span>
    </div>

</div>
<div class="orch-note">
    Orchestrated by <span>Apache Airflow 2.9</span> running in
    <span>Docker</span> · weekly schedule · LocalExecutor
</div>

<!-- FOOTER -->
<div class="page-foot">
    <div class="foot-hint">
        <strong>Use the sidebar</strong> to explore race results,
        championship battles, and driver profiles.
    </div>
    <a class="gh-btn"
       href="https://github.com/BModz/f1-analytics-pipeline"
       target="_blank" rel="noopener">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" style="flex-shrink:0">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.38.6.11.82-.26.82-.58
            v-2.03c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76
            -1.09-.74.08-.73.08-.73 1.2.09 1.84 1.24 1.84 1.24 1.07 1.83 2.8 1.3
            3.49.99.11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93
            0-1.31.47-2.38 1.24-3.22-.14-.3-.54-1.52.1-3.18 0 0 1.01-.32
            3.3 1.23a11.5 11.5 0 0 1 3-.4c1.02.005 2.04.14 3 .4
            2.28-1.55 3.29-1.23 3.29-1.23.64 1.66.24 2.88.12 3.18
            .77.84 1.23 1.91 1.23 3.22 0 4.61-2.81 5.63-5.48 5.92
            .43.37.81 1.1.81 2.22v3.29c0 .32.22.7.82.58
            C20.56 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z"/>
        </svg>
        View Source
    </a>
</div>
""", unsafe_allow_html=True)
