import os
import pandas as pd
import streamlit as st
import plotly.express as px

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="NSW Road Safety Analytics Hub",
    page_icon="🛣️",
    layout="wide"
)

# ==================================================
# DATA PATHS
# ==================================================
CSV_PATH = "data/nsw_crash_data_clean.csv"
XLSX_PATH = "data/nsw_crash_data.xlsx"

# ==================================================
# LIGHT THEME DESIGN
# ==================================================
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #eef7ff 0%, #f4fffb 100%);
    color: #111827;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #c7dfff 0%, #d9fff4 100%);
}

/* SIDEBAR TEXT */
[data-testid="stSidebar"] * {
    color: #0f172a !important;
    font-weight: 600;
}

/* HEADINGS */
h1, h2, h3, h4 {
    color: #0f172a;
}

/* SECTION TITLES */
.section-title {
    font-size: 32px;
    font-weight: 800;
    color: #0f172a;
    margin-top: 25px;
    margin-bottom: 12px;
}

/* INFO BOX */
.info-box {
    background-color: #ffffff;
    padding: 20px;
    border-left: 7px solid #0ea5e9;
    border-radius: 18px;
    margin: 18px 0px;
    color: #111827;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
}

/* WARNING BOX */
.warning-box {
    background-color: #fff7ed;
    padding: 20px;
    border-left: 7px solid #f97316;
    border-radius: 18px;
    margin: 18px 0px;
    color: #111827;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
}

/* ACTION BOX */
.action-box {
    background-color: #ecfdf5;
    padding: 20px;
    border-left: 7px solid #10b981;
    border-radius: 18px;
    margin: 18px 0px;
    color: #111827;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.08);
}

/* KPI CARDS */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%);
    padding: 22px;
    border-radius: 20px;
    box-shadow: 0px 8px 20px rgba(37,99,235,0.25);
}

/* KPI LABEL */
div[data-testid="stMetricLabel"] {
    color: white !important;
    font-size: 18px !important;
    font-weight: 700 !important;
}

/* KPI VALUE */
div[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 42px !important;
    font-weight: 800 !important;
}

/* SIDEBAR MULTISELECT */
.stMultiSelect div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 14px !important;
}

/* GENERAL TEXT */
p, label, span {
    color: #111827 !important;
}

</style>
""", unsafe_allow_html=True)
# ==================================================
# LOAD DATA
# ==================================================
@st.cache_data(show_spinner="Loading NSW road crash dataset...")
def load_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH, low_memory=False)
    elif os.path.exists(XLSX_PATH):
        df = pd.read_excel(XLSX_PATH, engine="openpyxl")
    else:
        st.error("Dataset not found. Put nsw_crash_data_clean.csv inside the data folder.")
        st.stop()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

df = load_data()

# ==================================================
# COLUMN SETUP
# ==================================================
YEAR_COL = "year_of_crash"
MONTH_COL = "month_of_crash"
DAY_COL = "day_of_week_of_crash"
TIME_COL = "two-hour_intervals"
REGION_COL = "lga"
SEVERITY_COL = "degree_of_crash"
LAT_COL = "latitude"
LON_COL = "longitude"

if YEAR_COL not in df.columns and "reporting_year" in df.columns:
    YEAR_COL = "reporting_year"

for c in [LAT_COL, LON_COL]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# ==================================================
# SIDEBAR FILTERS
# ==================================================
st.sidebar.markdown("## 🧭 Safety Dashboard Controls")
st.sidebar.caption("Filter the data to explore crash risk patterns.")

df_filtered = df.copy()

if YEAR_COL in df.columns:
    years = sorted(df[YEAR_COL].dropna().unique())
    selected_years = st.sidebar.multiselect(
        "Select crash year(s)",
        options=years,
        default=years
    )
    df_filtered = df_filtered[df_filtered[YEAR_COL].isin(selected_years)]

if REGION_COL in df.columns:
    region_options = (
        df_filtered[REGION_COL]
        .dropna()
        .value_counts()
        .head(30)
        .index
        .tolist()
    )
    selected_regions = st.sidebar.multiselect(
        "Select LGA / Region",
        options=region_options,
        default=region_options[:10]
    )
    if selected_regions:
        df_filtered = df_filtered[df_filtered[REGION_COL].isin(selected_regions)]

if SEVERITY_COL in df.columns:
    severity_options = sorted(df_filtered[SEVERITY_COL].dropna().astype(str).unique())
    selected_severity = st.sidebar.multiselect(
        "Select crash outcome",
        options=severity_options,
        default=severity_options
    )
    df_filtered = df_filtered[df_filtered[SEVERITY_COL].astype(str).isin(selected_severity)]

st.sidebar.markdown("---")
st.sidebar.markdown("### Scenario Slider")
reduction_rate = st.sidebar.slider(
    "Possible crash reduction after safety action (%)",
    0, 30, 10, 5
)

# ==================================================
# HEADER
# ==================================================
st.markdown("# 🛣️ NSW Road Safety Analytics Hub")
st.markdown("### A data story for safer roads, smarter planning, and targeted intervention")
st.caption("Prepared by Saumya Goswami | Role: Analyst & Architect")

st.markdown("""
<div class="info-box">
<b>Dashboard Purpose:</b> This dashboard investigates crash trends, hotspot LGAs,
risk timing, severity patterns, and possible intervention impact across New South Wales.
The aim is to move from raw crash numbers to practical road safety decisions.
</div>
""", unsafe_allow_html=True)

# ==================================================
# KPI CARDS
# ==================================================
total_crashes = len(df_filtered)

fatal_crashes = 0
injury_crashes = 0

if SEVERITY_COL in df_filtered.columns:
    fatal_crashes = df_filtered[
        df_filtered[SEVERITY_COL].astype(str).str.lower().str.contains("fatal", na=False)
    ].shape[0]

    injury_crashes = df_filtered[
        df_filtered[SEVERITY_COL].astype(str).str.lower().str.contains("injury", na=False)
    ].shape[0]

region_count = df_filtered[REGION_COL].nunique() if REGION_COL in df_filtered.columns else 0

st.markdown('<div class="section-title">1️⃣ Road Safety Snapshot</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Crashes", f"{total_crashes:,}")
c2.metric("Fatal Crashes", f"{fatal_crashes:,}")
c3.metric("Injury Crashes", f"{injury_crashes:,}")
c4.metric("LGAs Analysed", f"{region_count:,}")

st.markdown("""
<div class="info-box">
<b>Quick Insight:</b> These headline indicators show the selected crash scope.
The key question is not only how many crashes happened, but where and when safety action should be prioritised.
</div>
""", unsafe_allow_html=True)

# ==================================================
# YEAR TREND
# ==================================================
st.markdown('<div class="section-title">2️⃣ Yearly Crash Movement</div>', unsafe_allow_html=True)

if YEAR_COL in df_filtered.columns:
    yearly_df = (
        df_filtered.groupby(YEAR_COL)
        .size()
        .reset_index(name="crash_count")
        .sort_values(YEAR_COL)
    )

    fig_year = px.area(
        yearly_df,
        x=YEAR_COL,
        y="crash_count",
        markers=True,
        title="Crash Trend by Year",
        template="plotly_white",
        color_discrete_sequence=["#0ea5e9"]
    )
    fig_year.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Crashes",
        title_x=0.02
    )
    st.plotly_chart(fig_year, use_container_width=True)

st.markdown("""
<div class="info-box">
<b>Analyst Note:</b> Yearly trends help identify whether crash risk is reducing,
increasing, or staying consistent across the selected period.
</div>
""", unsafe_allow_html=True)

# ==================================================
# HOTSPOT ANALYSIS
# ==================================================
st.markdown('<div class="section-title">3️⃣ High-Risk LGA Ranking</div>', unsafe_allow_html=True)

if REGION_COL in df_filtered.columns:
    hotspot_df = (
        df_filtered[REGION_COL]
        .dropna()
        .value_counts()
        .head(15)
        .reset_index()
    )
    hotspot_df.columns = [REGION_COL, "crash_count"]

    fig_hotspot = px.bar(
        hotspot_df,
        x="crash_count",
        y=REGION_COL,
        orientation="h",
        text="crash_count",
        title="Top 15 LGAs by Crash Count",
        template="plotly_white",
        color="crash_count",
        color_continuous_scale="Teal"
    )
    fig_hotspot.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title="Number of Crashes",
        yaxis_title="LGA",
        title_x=0.02
    )
    st.plotly_chart(fig_hotspot, use_container_width=True)

    if len(hotspot_df) > 0:
        top_lga = hotspot_df.iloc[0][REGION_COL]
        top_value = hotspot_df.iloc[0]["crash_count"]

        st.markdown(f"""
        <div class="warning-box">
        <b>Priority Signal:</b> <b>{top_lga}</b> records the highest crash volume
        in the selected view with <b>{top_value:,}</b> crashes. This indicates a strong need for targeted safety review.
        </div>
        """, unsafe_allow_html=True)

# ==================================================
# TEMPORAL ANALYSIS
# ==================================================
st.markdown('<div class="section-title">4️⃣ Time and Day Risk Pattern</div>', unsafe_allow_html=True)

left, right = st.columns(2)

with left:
    if DAY_COL in df_filtered.columns:
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
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
            text="crash_count",
            title="Crashes by Day of Week",
            template="plotly_white",
            color_discrete_sequence=["#6366f1"]
        )
        fig_day.update_layout(
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
            text="crash_count",
            title="Crashes by Two-Hour Interval",
            template="plotly_white",
            color_discrete_sequence=["#f97316"]
        )
        fig_time.update_layout(
            xaxis_title="Time Interval",
            yaxis_title="Crashes",
            title_x=0.02
        )
        fig_time.update_xaxes(tickangle=45)
        st.plotly_chart(fig_time, use_container_width=True)

st.markdown("""
<div class="info-box">
<b>Planning Insight:</b> Time and day patterns are useful for scheduling enforcement,
awareness campaigns, and emergency response resources during higher-risk periods.
</div>
""", unsafe_allow_html=True)

# ==================================================
# MONTHLY PATTERN - EXTRA SECTION
# ==================================================
st.markdown('<div class="section-title">5️⃣ Monthly Crash Seasonality</div>', unsafe_allow_html=True)

if MONTH_COL in df_filtered.columns:
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    month_df = (
        df_filtered[MONTH_COL]
        .dropna()
        .value_counts()
        .reindex(month_order)
        .dropna()
        .reset_index()
    )
    month_df.columns = [MONTH_COL, "crash_count"]

    fig_month = px.line(
        month_df,
        x=MONTH_COL,
        y="crash_count",
        markers=True,
        title="Monthly Crash Distribution",
        template="plotly_white",
        color_discrete_sequence=["#10b981"]
    )
    fig_month.update_layout(
        xaxis_title="Month",
        yaxis_title="Crashes",
        title_x=0.02
    )
    fig_month.update_xaxes(tickangle=35)
    st.plotly_chart(fig_month, use_container_width=True)

st.markdown("""
<div class="info-box">
<b>Extra Analysis:</b> Monthly crash patterns can highlight seasonal safety risks,
holiday travel pressure, or periods where safety campaigns may be more useful.
</div>
""", unsafe_allow_html=True)

# ==================================================
# SEVERITY PROFILE
# ==================================================
st.markdown('<div class="section-title">6️⃣ Crash Severity Mix</div>', unsafe_allow_html=True)

if SEVERITY_COL in df_filtered.columns:
    severity_df = (
        df_filtered[SEVERITY_COL]
        .dropna()
        .astype(str)
        .value_counts()
        .reset_index()
    )
    severity_df.columns = [SEVERITY_COL, "count"]

    fig_severity = px.pie(
        severity_df,
        names=SEVERITY_COL,
        values="count",
        hole=0.55,
        title="Crash Outcome Composition",
        template="plotly_white",
        color_discrete_sequence=["#0ea5e9", "#14b8a6", "#f97316", "#6366f1"]
    )
    fig_severity.update_layout(title_x=0.02)
    st.plotly_chart(fig_severity, use_container_width=True)

st.markdown("""
<div class="warning-box">
<b>Risk Interpretation:</b> Severity changes priority. An area with fewer crashes but more fatal or serious outcomes
may need stronger intervention than an area with many low-severity incidents.
</div>
""", unsafe_allow_html=True)

# ==================================================
# INJURY IMPACT ANALYSIS - EXTRA SECTION
# ==================================================
st.markdown('<div class="section-title">7️⃣ Human Impact Indicator</div>', unsafe_allow_html=True)

injury_cols = ["no._killed", "no._seriously_injured", "no._moderately_injured", "no._minor-other_injured"]
existing_injury_cols = [c for c in injury_cols if c in df_filtered.columns]

if existing_injury_cols:
    impact_data = {}
    for col in existing_injury_cols:
        impact_data[col.replace("no._", "").replace("_", " ").title()] = pd.to_numeric(
            df_filtered[col], errors="coerce"
        ).sum()

    impact_df = pd.DataFrame({
        "Impact Type": list(impact_data.keys()),
        "People Affected": list(impact_data.values())
    })

    fig_impact = px.bar(
        impact_df,
        x="Impact Type",
        y="People Affected",
        text="People Affected",
        title="People Killed or Injured in Selected Crashes",
        template="plotly_white",
        color_discrete_sequence=["#ef4444"]
    )
    fig_impact.update_layout(
        xaxis_title="Impact Type",
        yaxis_title="Number of People",
        title_x=0.02
    )
    st.plotly_chart(fig_impact, use_container_width=True)
else:
    st.info("Human impact columns are not available in this filtered dataset.")

st.markdown("""
<div class="warning-box">
<b>Human-Centred Message:</b> Behind every crash record is a person, family, or community affected.
This makes road safety more than a transport issue; it is a public wellbeing issue.
</div>
""", unsafe_allow_html=True)

# ==================================================
# MAP
# ==================================================
st.markdown('<div class="section-title">8️⃣ Place-Based Crash Map</div>', unsafe_allow_html=True)

if LAT_COL in df_filtered.columns and LON_COL in df_filtered.columns:
    map_df = df_filtered[[LAT_COL, LON_COL, SEVERITY_COL, REGION_COL]].dropna().copy()
    map_df = map_df.rename(columns={LAT_COL: "lat", LON_COL: "lon"})

    if len(map_df) > 5000:
        map_df = map_df.sample(5000, random_state=42)

    st.caption("Map displays up to 5,000 crash points for performance.")

    st.map(
        map_df,
        latitude="lat",
        longitude="lon",
        size=20
    )

st.markdown("""
<div class="info-box">
<b>Spatial Insight:</b> Mapping helps convert crash data into place-based action,
showing where targeted safety improvements may be most valuable.
</div>
""", unsafe_allow_html=True)

# ==================================================
# WHAT-IF SCENARIO
# ==================================================
st.markdown('<div class="section-title">9️⃣ What-if Safety Improvement Scenario</div>', unsafe_allow_html=True)

prevented = int(total_crashes * reduction_rate / 100)
remaining = total_crashes - prevented

s1, s2, s3 = st.columns(3)
s1.metric("Current Crash Load", f"{total_crashes:,}")
s2.metric(f"Potentially Prevented ({reduction_rate}%)", f"{prevented:,}")
s3.metric("Projected Remaining", f"{remaining:,}")

st.markdown(f"""
<div class="action-box">
<b>Scenario Result:</b> If targeted road safety action reduces crashes by <b>{reduction_rate}%</b>,
around <b>{prevented:,}</b> crashes could be prevented in the selected view.
This supports practical decision-making rather than only descriptive reporting.
</div>
""", unsafe_allow_html=True)

# ==================================================
# FINAL RECOMMENDATIONS
# ==================================================
st.markdown('<div class="section-title">🔟 Strategic Action Plan</div>', unsafe_allow_html=True)

st.markdown("""
<div class="action-box">
<h3>Recommended Road Safety Priorities</h3>

<ul>
<li><b>Focus on high-volume LGAs</b> where crash burden is repeated.</li>
<li><b>Use time-based enforcement</b> during peak crash periods.</li>
<li><b>Prioritise severe outcomes</b>, not only total crash counts.</li>
<li><b>Improve dangerous road corridors</b> through audits and redesign.</li>
<li><b>Use seasonal patterns</b> to time awareness campaigns more effectively.</li>
</ul>

<b>Final Message:</b> NSW road safety strategy should be targeted, evidence-based, and human-centred.
</div>
""", unsafe_allow_html=True)

