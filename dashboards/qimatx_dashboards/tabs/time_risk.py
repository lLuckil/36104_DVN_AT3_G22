import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    DAY_COL,
    DAY_ORDER,
    TIME_COL,
    TIME_ORDER,
    make_count_df,
)


def render_time_risk_tab(filtered_df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="section-title">3. Day and time risk pattern</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        if DAY_COL in filtered_df.columns:
            day_df = make_count_df(filtered_df, DAY_COL)

            day_df[DAY_COL] = pd.Categorical(
                day_df[DAY_COL],
                categories=DAY_ORDER,
                ordered=True,
            )

            day_df = day_df.sort_values(DAY_COL)

            fig_day = px.bar(
                day_df,
                x=DAY_COL,
                y="crash_count",
                text="crash_count",
                title="Crash count by weekday",
            )

            fig_day.update_layout(
                template="plotly_dark",
                xaxis_title="Day of week",
                yaxis_title="Crash count",
                title_x=0.02,
                height=460,
            )

            fig_day.update_xaxes(automargin=True)
            fig_day.update_yaxes(automargin=True)

            st.plotly_chart(fig_day, use_container_width=True)

    with c2:
        if TIME_COL in filtered_df.columns:
            time_df = make_count_df(filtered_df, TIME_COL)

            time_df[TIME_COL] = pd.Categorical(
                time_df[TIME_COL],
                categories=TIME_ORDER,
                ordered=True,
            )

            time_df = time_df.sort_values(TIME_COL)

            fig_time = px.bar(
                time_df,
                x=TIME_COL,
                y="crash_count",
                text="crash_count",
                title="Crash count by two-hour interval",
            )

            fig_time.update_layout(
                template="plotly_dark",
                xaxis_title="Two-hour interval",
                yaxis_title="Crash count",
                title_x=0.02,
                height=520,
                margin=dict(l=10, r=10, t=60, b=150),
            )

            fig_time.update_xaxes(
                tickangle=45,
                automargin=True,
            )

            fig_time.update_yaxes(automargin=True)

            st.plotly_chart(fig_time, use_container_width=True)

    c3, c4 = st.columns([1.15, 0.85])

    with c3:
        if DAY_COL in filtered_df.columns and TIME_COL in filtered_df.columns:
            heat_df = (
                filtered_df.groupby([DAY_COL, TIME_COL])
                .size()
                .reset_index(name="crash_count")
            )

            heat_df[DAY_COL] = pd.Categorical(
                heat_df[DAY_COL],
                categories=DAY_ORDER,
                ordered=True,
            )

            heat_df[TIME_COL] = pd.Categorical(
                heat_df[TIME_COL],
                categories=TIME_ORDER,
                ordered=True,
            )

            heat_pivot = heat_df.pivot(
                index=DAY_COL,
                columns=TIME_COL,
                values="crash_count",
            ).reindex(DAY_ORDER)

            fig_heat = px.imshow(
                heat_pivot,
                text_auto=True,
                aspect="auto",
                title="Crash concentration heatmap: day × time interval",
            )

            fig_heat.update_layout(
                template="plotly_dark",
                xaxis_title="Time interval",
                yaxis_title="Day of week",
                title_x=0.02,
                height=520,
                margin=dict(l=10, r=10, t=60, b=150),
            )

            fig_heat.update_xaxes(
                tickangle=45,
                automargin=True,
            )

            fig_heat.update_yaxes(automargin=True)

            st.plotly_chart(fig_heat, use_container_width=True)

    with c4:
        if "time_band" in filtered_df.columns:
            band_df = make_count_df(filtered_df, "time_band")

            fig_band = px.bar(
                band_df,
                x="crash_count",
                y="time_band",
                orientation="h",
                text="crash_count",
                title="Crash count by policy time band",
            )

            fig_band.update_layout(
                template="plotly_dark",
                yaxis=dict(autorange="reversed"),
                xaxis_title="Crash count",
                yaxis_title="Time band",
                title_x=0.02,
                height=420,
            )

            st.plotly_chart(fig_band, use_container_width=True)

            peak_count = int(filtered_df["is_peak_commute"].sum())
            peak_share = peak_count / len(filtered_df) * 100 if len(filtered_df) else 0

            st.markdown(
                f"""
                <div class="insight-box">
                <b>Peak-hour check:</b> {peak_count:,} crashes ({peak_share:.1f}%) occurred in broad commute/school peak windows
                based on 06:00-09:59 and 16:00-19:59 intervals. This helps test whether crash risk aligns with busy travel periods in Australia.
                </div>
                """,
                unsafe_allow_html=True,
            )