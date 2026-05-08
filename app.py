from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dashboard_data import (
    DEFAULT_CRASH_PATH,
    DEFAULT_POPULATION_PATH,
    MONTH_ORDER,
    MISSING_LABEL,
    SPARSE_CATEGORICAL_COLUMNS,
    TWO_HOUR_ORDER,
    WEEKDAY_ORDER,
    load_bundle,
)


st.set_page_config(
    page_title="NSW Road Safety Dashboard",
    page_icon=":bar_chart:",
    layout="wide",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0a0a0a;
            --panel: rgba(18, 18, 18, 0.92);
            --panel-strong: rgba(24, 24, 24, 0.98);
            --ink: #f3f3f3;
            --muted: #b6b6b6;
            --accent: #b74928;
            --accent-soft: rgba(183, 73, 40, 0.14);
            --line: rgba(255, 255, 255, 0.10);
        }

        .stApp {
            background: var(--bg);
            color: var(--ink);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stSidebar"] {
            background: #050505;
            border-right: 1px solid var(--line);
        }

        .hero {
            padding: 1.25rem 1.4rem;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: #121212;
            box-shadow: none;
        }

        .hero h1 {
            margin: 0;
            font-size: 2.2rem;
            line-height: 1.05;
            color: var(--ink);
        }

        .hero p {
            margin: 0.7rem 0 0;
            color: var(--muted);
            font-size: 1rem;
            max-width: 62rem;
        }

        .note {
            padding: 0.85rem 1rem;
            border-left: 4px solid var(--accent);
            background: var(--panel);
            border-radius: 6px;
            color: var(--muted);
        }

        div[data-testid="stMetric"] {
            background: var(--panel-strong);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 0.8rem 0.9rem;
        }

        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricValue"] {
            color: var(--ink);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.6rem;
        }

        .stTabs [data-baseweb="tab"] {
            color: var(--muted);
            background: transparent;
            border-bottom: 2px solid transparent;
            padding-left: 0;
            padding-right: 0;
        }

        .stTabs [aria-selected="true"] {
            color: var(--ink);
            border-bottom-color: var(--accent);
        }

        .stTextInput input,
        .stMultiSelect [data-baseweb="select"] > div,
        .stSelectbox [data-baseweb="select"] > div,
        .stNumberInput input {
            background: #111111 !important;
            color: var(--ink) !important;
            border: 1px solid var(--line) !important;
        }

        .stSlider [data-baseweb="slider"] {
            padding-top: 0.6rem;
        }

        label, .stMarkdown, .stCaption, .st-emotion-cache-10trblm, .st-emotion-cache-16idsys p {
            color: var(--ink);
        }

        .stSelectbox div, .stMultiSelect div, .stTextInput div {
            color: var(--ink);
        }

        .stDataFrame, .stTable {
            background: #111111;
        }

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def fmt_int(value: int | float) -> str:
    return f"{int(value):,}"


def render_header(crash_path: Path) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>NSW Road Safety Dashboard</h1>
            <p>
                Interactive exploration of NSW road crashes from 2024 onward, with a focus on severity,
                timing, geography, and road environment conditions. ABS 2024 LGA population is joined to the
                crash dataset so the dashboard can compare both raw crash counts and population-adjusted burden.
            </p>
            <p><strong>Crash source:</strong> {crash_path.name}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filter_crash_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.subheader("Filters")

    severity_options = sorted(df["Degree of crash"].dropna().unique().tolist())
    selected_severity = st.sidebar.multiselect("Degree of crash", severity_options, default=severity_options)

    lga_options = sorted(df["LGA"].dropna().unique().tolist())
    selected_lgas = st.sidebar.multiselect("LGA", lga_options, default=[])

    urbanisation_options = sorted(df["Urbanisation"].dropna().unique().tolist())
    selected_urbanisation = st.sidebar.multiselect("Urbanisation", urbanisation_options, default=urbanisation_options)

    weather_options = sorted(df["Weather"].dropna().unique().tolist())
    selected_weather = st.sidebar.multiselect("Weather", weather_options, default=weather_options)

    max_killed = int(df["No. killed"].max())
    killed_range = st.sidebar.slider("Deaths per crash", 0, max_killed, (0, max_killed))

    weekend_only = st.sidebar.toggle("Weekend only", value=False)

    filtered = df[
        df["Degree of crash"].isin(selected_severity)
        & df["Urbanisation"].isin(selected_urbanisation)
        & df["Weather"].isin(selected_weather)
        & df["No. killed"].between(killed_range[0], killed_range[1])
    ].copy()

    if selected_lgas:
        filtered = filtered[filtered["LGA"].isin(selected_lgas)].copy()

    if weekend_only:
        filtered = filtered[filtered["Weekend"]].copy()

    return filtered


def plot_bar(data: pd.DataFrame, x: str, y: str, color: str | None, title: str, category_orders: dict | None = None) -> None:
    fig = px.bar(
        data,
        x=x,
        y=y,
        color=color,
        title=title,
        category_orders=category_orders,
        color_discrete_sequence=["#b74928", "#316f57", "#d89f3d", "#64818e"],
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=8, r=8, t=56, b=8),
        legend_title_text="",
        font=dict(color="#f3f3f3"),
        title_font=dict(color="#f3f3f3"),
    )
    fig.update_xaxes(color="#d6d6d6", gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(color="#d6d6d6", gridcolor="rgba(255,255,255,0.18)")
    st.plotly_chart(fig, use_container_width=True)


def plot_map(data: pd.DataFrame) -> None:
    map_df = data.dropna(subset=["Latitude", "Longitude"]).copy()
    if map_df.empty:
        st.info("No crash locations available for the current filter set.")
        return

    sample_size = min(len(map_df), 4000)
    map_df = map_df.sample(sample_size, random_state=42) if len(map_df) > sample_size else map_df

    fig = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        color="Degree of crash",
        hover_name="LGA",
        hover_data={
            "Town": True,
            "Month of crash": True,
            "Two-hour intervals": True,
            "Total casualties": True,
            "Latitude": False,
            "Longitude": False,
        },
        zoom=4.6,
        height=520,
        color_discrete_sequence=["#b74928", "#316f57", "#d89f3d", "#64818e"],
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        margin=dict(l=0, r=0, t=0, b=0),
        legend_title_text="",
        font=dict(color="#f3f3f3"),
    )
    st.plotly_chart(fig, use_container_width=True)


def build_lga_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["LGA", "Population 2024"], dropna=False, observed=False)
        .agg(
            Crashes=("Crash ID", "count"),
            Killed=("No. killed", "sum"),
            Seriously_injured=("No. seriously injured", "sum"),
            Casualties=("Total casualties", "sum"),
        )
        .reset_index()
    )
    summary["Crash rate per 100k"] = 100000 * summary["Crashes"] / summary["Population 2024"]
    summary["Fatality rate per 100k"] = 100000 * summary["Killed"] / summary["Population 2024"]
    summary["Casualty rate per 100k"] = 100000 * summary["Casualties"] / summary["Population 2024"]
    return summary


def render_kpis(df: pd.DataFrame) -> None:
    total_crashes = len(df)
    total_killed = int(df["No. killed"].sum())
    total_serious = int(df["No. seriously injured"].sum())
    total_casualties = int(df["Total casualties"].sum())
    fatal_share = 0 if total_crashes == 0 else 100 * (df["Degree of crash"].eq("Fatal").sum() / total_crashes)

    cols = st.columns(5)
    cols[0].metric("Crashes", fmt_int(total_crashes))
    cols[1].metric("People killed", fmt_int(total_killed))
    cols[2].metric("Seriously injured", fmt_int(total_serious))
    cols[3].metric("Total casualties", fmt_int(total_casualties))
    cols[4].metric("Fatal crash share", f"{fatal_share:.1f}%")


def render_overview(df: pd.DataFrame) -> None:
    lga_summary = build_lga_summary(df)
    matched_rows = int(df["Population 2024"].notna().sum())
    matched_share = 100 * matched_rows / len(df)

    render_kpis(df)
    st.markdown(
        f"""
        <div class="note">
            Sparse fields from the source workbook are kept in the dataset. When they are blank, the dashboard
            treats them as not recorded or not applicable instead of silently removing them from analysis.
            ABS population enrichment currently matches {matched_share:.1f}% of filtered crash records for
            population-adjusted LGA analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns((1.1, 1))
    with col1:
        monthly = (
            df.groupby("Month of crash", observed=False)
            .agg(Crashes=("Crash ID", "count"), Casualties=("Total casualties", "sum"))
            .reset_index()
        )
        plot_bar(
            monthly,
            x="Month of crash",
            y="Crashes",
            color=None,
            title="Crash volume by month",
            category_orders={"Month of crash": MONTH_ORDER},
        )
    with col2:
        severity = (
            df.groupby("Degree of crash", observed=False)
            .agg(Crashes=("Crash ID", "count"), Casualties=("Total casualties", "sum"))
            .reset_index()
            .sort_values("Crashes", ascending=False)
        )
        plot_bar(severity, x="Degree of crash", y="Crashes", color="Degree of crash", title="Severity distribution")

    col3, col4 = st.columns(2)
    with col3:
        top_counts = lga_summary.sort_values(["Crashes", "Casualties"], ascending=False).head(15)
        plot_bar(top_counts, x="LGA", y="Crashes", color=None, title="Top 15 LGAs by crash count")
    with col4:
        top_rates = (
            lga_summary.dropna(subset=["Population 2024", "Crash rate per 100k"])
            .query("`Population 2024` >= 10000")
            .sort_values(["Crash rate per 100k", "Crashes"], ascending=False)
            .head(15)
        )
        plot_bar(top_rates, x="LGA", y="Crash rate per 100k", color=None, title="Top 15 LGAs by crash rate per 100k")


def render_time_and_severity(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        weekday = (
            df.groupby("Day of week of crash", observed=False)
            .agg(Crashes=("Crash ID", "count"))
            .reset_index()
        )
        plot_bar(
            weekday,
            x="Day of week of crash",
            y="Crashes",
            color=None,
            title="Crash count by weekday",
            category_orders={"Day of week of crash": WEEKDAY_ORDER},
        )

    with col2:
        two_hour = (
            df.groupby(["Two-hour intervals", "Degree of crash"], observed=False)
            .agg(Crashes=("Crash ID", "count"))
            .reset_index()
        )
        plot_bar(
            two_hour,
            x="Two-hour intervals",
            y="Crashes",
            color="Degree of crash",
            title="Crash timing by two-hour interval",
            category_orders={"Two-hour intervals": TWO_HOUR_ORDER},
        )

    monthly_casualties = (
        df.groupby("Month of crash", observed=False)
        .agg(
            Killed=("No. killed", "sum"),
            Seriously_injured=("No. seriously injured", "sum"),
            Moderately_injured=("No. moderately injured", "sum"),
            Minor_other=("No. minor-other injured", "sum"),
        )
        .reset_index()
    )
    melted = monthly_casualties.melt("Month of crash", var_name="Outcome", value_name="People")
    plot_bar(
        melted,
        x="Month of crash",
        y="People",
        color="Outcome",
        title="Casualty outcomes by month",
        category_orders={"Month of crash": MONTH_ORDER},
    )


def render_geography(df: pd.DataFrame) -> None:
    lga_summary = build_lga_summary(df)

    st.subheader("Crash map")
    plot_map(df)

    col1, col2 = st.columns(2)

    with col1:
        urban = (
            df.groupby(["Urbanisation", "Degree of crash"], observed=False)
            .agg(Crashes=("Crash ID", "count"))
            .reset_index()
        )
        plot_bar(urban, x="Urbanisation", y="Crashes", color="Degree of crash", title="Urbanisation mix")

    with col2:
        lga_rates = (
            lga_summary.dropna(subset=["Population 2024", "Casualty rate per 100k"])
            .query("`Population 2024` >= 10000")
            .sort_values(["Casualty rate per 100k", "Casualties"], ascending=False)
            .head(15)
        )
        plot_bar(lga_rates, x="LGA", y="Casualty rate per 100k", color=None, title="Highest casualty rate by LGA")

    fatal_rates = (
        lga_summary.dropna(subset=["Population 2024", "Fatality rate per 100k"])
        .query("`Population 2024` >= 10000")
        .sort_values(["Fatality rate per 100k", "Killed"], ascending=False)
        .head(15)
    )
    plot_bar(fatal_rates, x="LGA", y="Fatality rate per 100k", color=None, title="Highest fatality rate by LGA")

    towns = (
            df.groupby("Town", observed=False)
            .agg(Crashes=("Crash ID", "count"), Casualties=("Total casualties", "sum"))
            .reset_index()
            .sort_values(["Crashes", "Casualties"], ascending=False)
            .head(15)
    )
    plot_bar(towns, x="Town", y="Crashes", color=None, title="Top towns by crash count")


def render_road_factors(df: pd.DataFrame) -> None:
    col1, col2 = st.columns(2)

    with col1:
        weather = (
            df.groupby("Weather", observed=False)
            .agg(Crashes=("Crash ID", "count"))
            .reset_index()
            .sort_values("Crashes", ascending=False)
            .head(12)
        )
        plot_bar(weather, x="Weather", y="Crashes", color=None, title="Weather conditions")

    with col2:
        speed = (
            df.groupby("Speed limit", observed=False)
            .agg(Crashes=("Crash ID", "count"), Casualties=("Total casualties", "sum"))
            .reset_index()
            .sort_values("Crashes", ascending=False)
        )
        plot_bar(speed, x="Speed limit", y="Crashes", color=None, title="Crashes by speed limit")

    col3, col4 = st.columns(2)

    with col3:
        lighting = (
            df.groupby("Natural lighting", observed=False)
            .agg(Crashes=("Crash ID", "count"))
            .reset_index()
            .sort_values("Crashes", ascending=False)
        )
        plot_bar(lighting, x="Natural lighting", y="Crashes", color=None, title="Natural lighting conditions")

    with col4:
        dca = (
            df.groupby("DCA - description", observed=False)
            .agg(Crashes=("Crash ID", "count"))
            .reset_index()
            .sort_values("Crashes", ascending=False)
            .head(12)
        )
        plot_bar(dca, x="DCA - description", y="Crashes", color=None, title="Top crash movement patterns")

    st.subheader("Sparse source fields")
    sparse_field = st.selectbox("Inspect sparse field", SPARSE_CATEGORICAL_COLUMNS, index=0)
    sparse_summary = (
        df.groupby(sparse_field, observed=False)
        .agg(Crashes=("Crash ID", "count"), Casualties=("Total casualties", "sum"))
        .reset_index()
        .sort_values(["Crashes", "Casualties"], ascending=False)
        .head(15)
    )
    plot_bar(sparse_summary, x=sparse_field, y="Crashes", color=None, title=f"Top values for {sparse_field}")


def render_data_quality(quality: pd.DataFrame) -> None:
    st.dataframe(quality, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="note">
            The dashboard keeps the sparse crash-factor columns because the manual strongly suggests many blanks
            are structural. They appear only when those conditions are present or relevant, so dropping them now
            would remove potentially meaningful slices from later analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    apply_theme()

    crash_path_text = str(DEFAULT_CRASH_PATH)
    population_path_text = str(DEFAULT_POPULATION_PATH)

    bundle = load_bundle(crash_path_text, population_path_text)
    crash_df = filter_crash_data(bundle.crash_df)

    render_header(bundle.crash_path)

    if crash_df.empty:
        st.warning("The current filters return no crash records. Adjust the sidebar filters to continue.")
        return

    tabs = st.tabs(["Overview", "Time and Severity", "Geography", "Road Factors", "Data Quality"])

    with tabs[0]:
        render_overview(crash_df)
    with tabs[1]:
        render_time_and_severity(crash_df)
    with tabs[2]:
        render_geography(crash_df)
    with tabs[3]:
        render_road_factors(crash_df)
    with tabs[4]:
        render_data_quality(bundle.crash_missing_profile)


if __name__ == "__main__":
    main()
