import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    MONTH_COL,
    SEVERITY_COL,
    TYPE_LOCATION_COL,
    make_count_df,
)


def render_overview_tab(filtered_df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="section-title">1. Overall crash overview</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.15, 0.85])

    with c1:
        if MONTH_COL in filtered_df.columns and "month_label" in filtered_df.columns:
            monthly_df = (
                filtered_df.groupby("month_label", observed=False)
                .size()
                .reset_index(name="crash_count")
                .dropna()
            )

            fig_month = px.line(
                monthly_df,
                x="month_label",
                y="crash_count",
                markers=True,
                text="crash_count",
                title="Monthly crash trend, 2024 onward",
            )

            fig_month.update_traces(
                line=dict(width=4),
                textposition="top center",
            )

            fig_month.update_layout(
                template="plotly_dark",
                xaxis_title="Month",
                yaxis_title="Crash count",
                title_x=0.02,
                height=430,
            )

            fig_month.update_xaxes(automargin=True)
            fig_month.update_yaxes(automargin=True)

            st.plotly_chart(fig_month, use_container_width=True)

    with c2:
        if SEVERITY_COL in filtered_df.columns:
            severity_df = make_count_df(filtered_df, SEVERITY_COL)

            fig_sev = px.pie(
                severity_df,
                names=SEVERITY_COL,
                values="crash_count",
                hole=0.45,
                title="Crash outcome composition",
            )

            fig_sev.update_layout(
                template="plotly_dark",
                title_x=0.02,
                height=430,
            )

            st.plotly_chart(fig_sev, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        if "season" in filtered_df.columns:
            season_order = ["Summer", "Autumn", "Winter", "Spring", "Unknown"]

            season_df = make_count_df(filtered_df, "season")

            season_df["season"] = pd.Categorical(
                season_df["season"],
                categories=season_order,
                ordered=True,
            )

            season_df = season_df.sort_values("season")

            fig_season = px.bar(
                season_df,
                x="season",
                y="crash_count",
                text="crash_count",
                title="Crash distribution by Australian season",
            )

            fig_season.update_layout(
                template="plotly_dark",
                xaxis_title="Season",
                yaxis_title="Crash count",
                title_x=0.02,
                height=430,
            )

            st.plotly_chart(fig_season, use_container_width=True)

    with c4:
        if TYPE_LOCATION_COL in filtered_df.columns:
            type_df = make_count_df(filtered_df, TYPE_LOCATION_COL, top_n=10)

            fig_type = px.bar(
                type_df,
                x="crash_count",
                y=TYPE_LOCATION_COL,
                orientation="h",
                text="crash_count",
                title="Top crash location types",
            )

            fig_type.update_layout(
                template="plotly_dark",
                yaxis=dict(autorange="reversed"),
                xaxis_title="Crash count",
                yaxis_title="Location type",
                title_x=0.02,
                height=430,
                margin=dict(l=20, r=20, t=60, b=40),
            )

            st.plotly_chart(fig_type, use_container_width=True)
