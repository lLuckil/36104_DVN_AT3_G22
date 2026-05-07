import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="NSW Crash Risk Intelligence",
    page_icon="🚦",
    layout="wide"
)

# ==================================================
# PATHS
# ==================================================
CSV_PATH = "data/nsw_crash_data_clean.csv"
XLSX_PATH = "data/nsw_crash_data.xlsx"

# ==================================================
# DESIGN SYSTEM
# ==================================================
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
.metric-card {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #374151;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}
.insight-box {
    background-color: #111827;
    padding: 18px;
    border-left: 6px solid #ef4444;
    border-radius: 12px;
    margin-top: 12px;
    margin-bottom: 20px;
}
.action-box {
    background-color: #102a1f;
    padding: 18px;
    border-left: 6px solid #22c55e;
    border-radius: 12px;
    margin-top: 12px;
}
.warning-box {
    background-color: #2b1d12;
    padding: 18px;
    border-left: 6px solid #f59e0b;
    border-radius: 12px;
}
.section-title {
    font-size: 34px;
    font-weight: 800;
    margin-top: 20px;
}
.small-caption {
    color: #9ca3af;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data(show_spinner="Loading NSW crash intelligence data...")
def load_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, low_memory=False)
    else:
        df = pd.read_excel(XLSX_PATH, engine="openpyxl")
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )
        df.to_csv(CSV_PATH, index=False)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    return df


df = load_data()

# ==================================================
# REQUIRED COLUMN SETUP
# ==================================================
YEAR_COL = "year_of_crash"
MONTH_COL = "month_of_crash"
DAY_COL = "day_of_week_of_crash"
TIME_COL = "two-hour_intervals"
REGION_COL = "lga"
SEVERITY_COL = "degree_of_crash"
LAT_COL = "latitude"
LON_COL = "longitude"

# Fallbacks
if YEAR_COL not in df.columns:
    YEAR_COL = "reporting_year"

# Clean numeric coordinates
if LAT_COL in df.columns and LON_COL in df.columns:
    df[LAT_COL] = pd.to_numeric(df[LAT_COL], errors="coerce")
    df[LON_COL] = pd.to_numeric(df[LON_COL], errors="coerce")

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.markdown("## 🔎 Investigation Controls")
st.sidebar.caption("Use filters to change the investigation context.")

df_filtered = df.copy()

if YEAR_COL in df.columns:
    years = sorted(df[YEAR_COL].dropna().unique())
    selected_years = st.sidebar.multiselect(
        "Select crash year(s)",
        options=years,
        default=years
    )
    if selected_years:
        df_filtered = df_filtered[df_filtered[YEAR_COL].isin(selected_years)]

if REGION_COL in df.columns:
    top_regions = (
        df_filtered[REGION_COL]
        .dropna()
        .value_counts()
        .head(30)
        .index
        .tolist()
    )
    selected_regions = st.sidebar.multiselect(
        "Select region / LGA",
        options=top_regions,
        default=top_regions[:10]
    )
    if selected_regions:
        df_filtered = df_filtered[df_filtered[REGION_COL].isin(selected_regions)]

if SEVERITY_COL in df.columns:
    severity_values = sorted(df_filtered[SEVERITY_COL].dropna().astype(str).unique())
    selected_severity = st.sidebar.multiselect(
        "Select crash outcome",
        options=severity_values,
        default=severity_values
    )
    if selected_severity:
        df_filtered = df_filtered[
            df_filtered[SEVERITY_COL].astype(str).isin(selected_severity)
        ]

st.sidebar.markdown("---")
st.sidebar.markdown("### Advanced Feature")
scenario_reduction = st.sidebar.slider(
    "What-if intervention: expected crash reduction",
    min_value=0,
    max_value=30,
    value=10,
    step=5
)

# ==================================================
# HERO SECTION
# ==================================================
st.markdown("# 🚦 NSW Road Crash Risk Intelligence")
st.markdown("## For Transport Safety Policy Advisors, NSW Government")

st.markdown("""
<div class="insight-box">
<b>Detective Narrative Arc:</b> This dashboard investigates where crashes happen, when risk concentrates,
which outcomes dominate, and what interventions should be prioritised.
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# KPI CARDS
# ==================================================
total_crashes = len(df_filtered)

fatal_count = 0
if SEVERITY_COL in df_filtered.columns:
    fatal_count = df_filtered[
        df_filtered[SEVERITY_COL].astype(str).str.lower().str.contains("fatal", na=False)
    ].shape[0]

injury_count = 0
if SEVERITY_COL in df_filtered.columns:
    injury_count = df_filtered[
        df_filtered[SEVERITY_COL].astype(str).str.lower().str.contains("injury", na=False)
    ].shape[0]

region_count = df_filtered[REGION_COL].nunique() if REGION_COL in df_filtered.columns else 0

st.markdown('<div class="section-title">1️⃣ Crime Scene Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Crashes", f"{total_crashes:,}")

with c2:
    st.metric("Fatal Crashes", f"{fatal_count:,}")

with c3:
    st.metric("Injury Crashes", f"{injury_count:,}")

with c4:
    st.metric("Regions Analysed", f"{region_count:,}")

st.markdown("""
<div class="insight-box">
<b>Executive insight:</b> The filtered crash records define the current investigation scope.
The focus is not only crash volume, but where risk is repeated and severe enough to justify intervention.
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# VISUAL 1: YEAR TREND
# ==================================================
st.markdown('<div class="section-title">2️⃣ First Clue: Crash Trend Over Time</div>', unsafe_allow_html=True)

if YEAR_COL in df_filtered.columns:
    yearly_df = (
        df_filtered.groupby(YEAR_COL)
        .size()
        .reset_index(name="crash_count")
        .sort_values(YEAR_COL)
    )

    fig = px.line(
        yearly_df,
        x=YEAR_COL,
        y="crash_count",
        markers=True,
        text="crash_count",
        title="Crash Volume Trend by Year"
    )
    fig.update_traces(line=dict(width=4), textposition="top center")
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Year",
        yaxis_title="Number of Crashes",
        title_x=0.02
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
<b>Detective clue:</b> A persistent or rising crash trend suggests that road safety risk is not isolated.
It indicates a continuing pattern requiring policy attention.
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# VISUAL 2: HOTSPOT AREAS
# ==================================================
st.markdown('<div class="section-title">3️⃣ Hotspot Evidence: Highest Burden Areas</div>', unsafe_allow_html=True)

if REGION_COL in df_filtered.columns:
    hotspot_df = (
        df_filtered[REGION_COL]
        .dropna()
        .value_counts()
        .head(15)
        .reset_index()
    )
    hotspot_df.columns = [REGION_COL, "crash_count"]

    fig = px.bar(
        hotspot_df,
        x="crash_count",
        y=REGION_COL,
        orientation="h",
        text="crash_count",
        title="Top 15 Crash Hotspot LGAs"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        template="plotly_dark",
        yaxis=dict(autorange="reversed"),
        xaxis_title="Number of Crashes",
        yaxis_title="LGA",
        title_x=0.02
    )
    st.plotly_chart(fig, use_container_width=True)

    top_lga = hotspot_df.iloc[0][REGION_COL]
    top_value = hotspot_df.iloc[0]["crash_count"]

    st.markdown(f"""
    <div class="warning-box">
    <b>Priority signal:</b> <b>{top_lga}</b> currently records the highest crash burden in the selected view
    with <b>{top_value:,}</b> crashes. This area should be investigated first for infrastructure and enforcement review.
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==================================================
# VISUAL 3: TEMPORAL RISK PATTERN
# ==================================================
st.markdown('<div class="section-title">4️⃣ Time Pattern: When Does Risk Concentrate?</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    if DAY_COL in df_filtered.columns:
        day_order = [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        ]
        day_df = (
            df_filtered[DAY_COL]
            .dropna()
            .value_counts()
            .reindex(day_order)
            .dropna()
            .reset_index()
        )
        day_df.columns = [DAY_COL, "crash_count"]

        fig_day = px.bar(
            day_df,
            x=DAY_COL,
            y="crash_count",
            title="Crash Distribution by Day of Week",
            text="crash_count"
        )
        fig_day.update_layout(
            template="plotly_dark",
            xaxis_title="Day",
            yaxis_title="Crashes",
            title_x=0.02
        )
        st.plotly_chart(fig_day, use_container_width=True)

with right:
    if TIME_COL in df_filtered.columns:
        time_df = (
            df_filtered[TIME_COL]
            .dropna()
            .value_counts()
            .reset_index()
        )
        time_df.columns = [TIME_COL, "crash_count"]

        fig_time = px.bar(
            time_df,
            x=TIME_COL,
            y="crash_count",
            title="Crash Distribution by Two-Hour Interval",
            text="crash_count"
        )
        fig_time.update_layout(
            template="plotly_dark",
            xaxis_title="Time Interval",
            yaxis_title="Crashes",
            title_x=0.02
        )
        fig_time.update_xaxes(tickangle=45)
        st.plotly_chart(fig_time, use_container_width=True)

st.markdown("""
<div class="insight-box">
<b>Policy relevance:</b> Time-based risk patterns support targeted enforcement, campaign scheduling,
and safer staffing decisions during high-risk periods.
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# VISUAL 4: SEVERITY PROFILE
# ==================================================
st.markdown('<div class="section-title">5️⃣ Risk Profile: Crash Outcome Severity</div>', unsafe_allow_html=True)

if SEVERITY_COL in df_filtered.columns:
    severity_df = (
        df_filtered[SEVERITY_COL]
        .dropna()
        .astype(str)
        .value_counts()
        .reset_index()
    )
    severity_df.columns = [SEVERITY_COL, "count"]

    fig = px.pie(
        severity_df,
        names=SEVERITY_COL,
        values="count",
        hole=0.45,
        title="Crash Outcome Composition"
    )
    fig.update_layout(template="plotly_dark", title_x=0.02)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("""
<div class="insight-box">
<b>Truth-teller insight:</b> Severity changes the policy priority. A lower-volume region with fatal outcomes
may require more urgent intervention than a higher-volume region dominated by non-casualty crashes.
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# VISUAL 5: MAP
# ==================================================
st.markdown('<div class="section-title">6️⃣ Spatial Evidence: Crash Location Map</div>', unsafe_allow_html=True)

if LAT_COL in df_filtered.columns and LON_COL in df_filtered.columns:
    map_df = df_filtered[[LAT_COL, LON_COL, SEVERITY_COL, REGION_COL]].dropna().copy()
    map_df = map_df.rename(columns={LAT_COL: "lat", LON_COL: "lon"})

    if len(map_df) > 5000:
        map_df = map_df.sample(5000, random_state=42)

    st.caption("Map is limited to 5,000 sampled points for performance.")

    st.map(
        map_df,
        latitude="lat",
        longitude="lon",
        size=20
    )

st.markdown("""
<div class="insight-box">
<b>Spatial clue:</b> Crash clustering provides visual evidence for hotspot prioritisation and helps policymakers
move from abstract numbers to place-based action.
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# ADVANCED FEATURE: WHAT-IF SIMULATION
# ==================================================
st.markdown('<div class="section-title">7️⃣ What-if Intervention Simulator</div>', unsafe_allow_html=True)

estimated_prevented = int(total_crashes * (scenario_reduction / 100))
remaining_crashes = total_crashes - estimated_prevented

s1, s2, s3 = st.columns(3)

with s1:
    st.metric("Current Crash Load", f"{total_crashes:,}")

with s2:
    st.metric(
        f"Estimated Prevented Crashes ({scenario_reduction}%)",
        f"{estimated_prevented:,}"
    )

with s3:
    st.metric("Projected Remaining Crashes", f"{remaining_crashes:,}")

st.markdown(f"""
<div class="action-box">
<b>Scenario interpretation:</b> If targeted interventions reduced crashes by <b>{scenario_reduction}%</b>,
approximately <b>{estimated_prevented:,}</b> crash incidents could be prevented within the selected investigation scope.
This helps convert the dashboard from descriptive analysis into a decision-support tool.
</div>
""", unsafe_allow_html=True)

st.divider()

# ==================================================
# FINAL RECOMMENDATION
# ==================================================
st.markdown('<div class="section-title">8️⃣ Case Conclusion: Priority Intervention Logic</div>', unsafe_allow_html=True)

st.markdown("""
<div class="action-box">
<h3>Recommended policy decision rule</h3>

Prioritise an area when it shows:

<ol>
<li><b>High crash volume</b></li>
<li><b>Repeated risk across time</b></li>
<li><b>High-severity outcomes</b></li>
<li><b>Clear spatial concentration</b></li>
</ol>

Recommended interventions include:
<ul>
<li>road safety audits,</li>
<li>speed and signal reviews,</li>
<li>public awareness campaigns,</li>
<li>targeted enforcement,</li>
<li>infrastructure redesign.</li>
</ul>

<b>Final message:</b> The strongest road safety response is not broad action everywhere,
but targeted action where repeated evidence shows the highest risk.
</div>
""", unsafe_allow_html=True)

# ==================================================
# OPTIONAL DEVELOPER CHECK
# ==================================================
with st.expander("Developer check: dataset columns"):
    st.write(df.columns.tolist())
    st.write(df.head())