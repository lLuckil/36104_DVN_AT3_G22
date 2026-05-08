import streamlit as st

from utils import (
    LGA_COL,
    SCHOOL_ZONE_LOCATION_COL,
    YEAR_COL,
    apply_sidebar_filters,
    format_int,
    is_yes_series,
    load_data,
    render_css,
)

from tabs.overview import render_overview_tab
from tabs.hotspots import render_hotspots_tab
from tabs.time_risk import render_time_risk_tab
from tabs.external_conditions import render_external_conditions_tab
from tabs.decision_summary import render_decision_summary_tab


st.set_page_config(
    page_title="NSW Crash Risk Intelligence 2024+",
    page_icon="🚦",
    layout="wide",
)

render_css()

df = load_data()
filtered_df, scenario_reduction = apply_sidebar_filters(df)

st.title("🚦 NSW Crash Risk Intelligence Dashboard")
st.subheader("2024 onward focus for Transport for NSW road safety decision-making")

st.markdown(
    """
    <div class="insight-box">
    <b>Purpose:</b> This dashboard focuses on 2024 onward crash records, then helps users inspect
    overall crash burden, hotspot LGAs, high-risk times, school-zone exposure, and external road conditions.
    Because the selected dataset mainly covers 2024, monthly and seasonal patterns are more useful than yearly trend charts.
    </div>
    """,
    unsafe_allow_html=True,
)

total_crashes = len(filtered_df)
fatal_count = int(filtered_df["is_fatal"].sum()) if "is_fatal" in filtered_df.columns else 0
injury_count = int(filtered_df["is_injury"].sum()) if "is_injury" in filtered_df.columns else 0
lga_count = filtered_df[LGA_COL].nunique() if LGA_COL in filtered_df.columns else 0

school_zone_count = 0
if SCHOOL_ZONE_LOCATION_COL in filtered_df.columns:
    school_zone_count = int(is_yes_series(filtered_df[SCHOOL_ZONE_LOCATION_COL]).sum())

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total crashes", format_int(total_crashes))
k2.metric("Fatal crashes", format_int(fatal_count))
k3.metric("Injury crashes", format_int(injury_count))
k4.metric("LGAs analysed", format_int(lga_count))
k5.metric("School-zone crashes", format_int(school_zone_count))

st.divider()

tab_overview, tab_hotspot, tab_time, tab_external, tab_action = st.tabs(
    [
        "1. Overall crash overview",
        "2. Hotspots + school zones",
        "3. Day and time risk",
        "4. External conditions",
        "5. Decision summary",
    ]
)

with tab_overview:
    render_overview_tab(filtered_df)

with tab_hotspot:
    render_hotspots_tab(filtered_df)

with tab_time:
    render_time_risk_tab(filtered_df)

with tab_external:
    render_external_conditions_tab(filtered_df)

with tab_action:
    render_decision_summary_tab(filtered_df, scenario_reduction)

with st.expander("Developer check: filtered dataset and columns"):
    st.write("Filtered shape:", filtered_df.shape)

    if YEAR_COL in filtered_df.columns:
        st.write("Years included:", sorted(filtered_df[YEAR_COL].dropna().unique().tolist()))

    st.write(filtered_df.head())
    st.write(filtered_df.columns.tolist())