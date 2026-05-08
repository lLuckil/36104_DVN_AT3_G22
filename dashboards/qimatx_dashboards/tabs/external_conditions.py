import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    LIGHT_COL,
    ROAD_SURFACE_COL,
    SPEED_COL,
    STREET_LIGHTING_COL,
    SURFACE_COL,
    TYPE_LOCATION_COL,
    WEATHER_COL,
    make_condition_summary,
    make_count_df,
)


def render_external_conditions_tab(filtered_df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="section-title">4. External conditions and crash context</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="warning-box">
        <b>Important interpretation:</b> These charts show conditions recorded during crashes.
        They do not prove causation because the dataset does not include exposure data such as total traffic volume,
        weather duration, or total road usage by condition.
        </div>
        """,
        unsafe_allow_html=True,
    )

    available_factors = [
        col
        for col in [
            WEATHER_COL,
            LIGHT_COL,
            SURFACE_COL,
            ROAD_SURFACE_COL,
            STREET_LIGHTING_COL,
            SPEED_COL,
            TYPE_LOCATION_COL,
        ]
        if col in filtered_df.columns
    ]

    if not available_factors:
        st.warning("No external condition columns were found.")
        return

    condition_choice = st.selectbox(
        "Choose external factor to inspect",
        options=available_factors,
        format_func=lambda x: x.replace("_", " ").replace("-", " ").title(),
    )

    condition_summary = make_condition_summary(
        filtered_df,
        condition_choice,
        min_records=10,
    )

    c1, c2 = st.columns([1, 1])

    with c1:
        fig_condition = px.bar(
            condition_summary.sort_values("crash_count", ascending=True),
            x="crash_count",
            y=condition_choice,
            orientation="h",
            text="crash_count",
            title=f"Crash count by {condition_choice.replace('_', ' ')}",
        )

        fig_condition.update_layout(
            template="plotly_dark",
            xaxis_title="Crash count",
            yaxis_title=condition_choice.replace("_", " ").title(),
            title_x=0.02,
            height=520,
        )

        st.plotly_chart(fig_condition, use_container_width=True)

    with c2:
        fig_rate = px.bar(
            condition_summary.sort_values("casualty_rate_%", ascending=True),
            x="casualty_rate_%",
            y=condition_choice,
            orientation="h",
            text="casualty_rate_%",
            title="Casualty crash rate by condition",
        )

        fig_rate.update_layout(
            template="plotly_dark",
            xaxis_title="Casualty crash rate (%)",
            yaxis_title=condition_choice.replace("_", " ").title(),
            title_x=0.02,
            height=520,
        )

        st.plotly_chart(fig_rate, use_container_width=True)

    st.markdown("#### External condition summary table")

    st.dataframe(
        condition_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Quick comparison across main external factors")

    main_factors = [
        WEATHER_COL,
        LIGHT_COL,
        SURFACE_COL,
        SPEED_COL,
    ]

    cols = st.columns(2)

    for i, factor in enumerate(main_factors):
        if factor in filtered_df.columns:
            with cols[i % 2]:
                temp = make_count_df(
                    filtered_df,
                    factor,
                    top_n=8,
                )

                fig = px.bar(
                    temp,
                    x="crash_count",
                    y=factor,
                    orientation="h",
                    text="crash_count",
                    title=factor.replace("_", " ").title(),
                )

                fig.update_layout(
                    template="plotly_dark",
                    yaxis=dict(autorange="reversed"),
                    xaxis_title="Crash count",
                    yaxis_title="",
                    title_x=0.02,
                    height=380,
                )

                st.plotly_chart(fig, use_container_width=True)