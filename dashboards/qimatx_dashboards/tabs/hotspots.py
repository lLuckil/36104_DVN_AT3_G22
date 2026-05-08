import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    LAT_COL,
    LGA_COL,
    LON_COL,
    SCHOOL_ZONE_ACTIVE_COL,
    SCHOOL_ZONE_LOCATION_COL,
    SEVERITY_COL,
    TIME_COL,
    format_int,
    is_yes_series,
)


def build_lga_summary(filtered_df: pd.DataFrame) -> pd.DataFrame:
    agg_dict = {
        "total_crashes": (LGA_COL, "size"),
        "fatal_crashes": ("is_fatal", "sum"),
        "injury_crashes": ("is_injury", "sum"),
        "casualty_crashes": ("is_casualty", "sum"),
    }

    if SCHOOL_ZONE_LOCATION_COL in filtered_df.columns:
        agg_dict["school_zone_crashes"] = (
            SCHOOL_ZONE_LOCATION_COL,
            lambda s: is_yes_series(s).sum(),
        )
    else:
        agg_dict["school_zone_crashes"] = (LGA_COL, lambda s: 0)

    if SCHOOL_ZONE_ACTIVE_COL in filtered_df.columns:
        agg_dict["active_school_zone_crashes"] = (
            SCHOOL_ZONE_ACTIVE_COL,
            lambda s: is_yes_series(s).sum(),
        )
    else:
        agg_dict["active_school_zone_crashes"] = (LGA_COL, lambda s: 0)

    summary = (
        filtered_df.groupby(LGA_COL)
        .agg(**agg_dict)
        .reset_index()
        .sort_values("total_crashes", ascending=False)
    )

    summary["casualty_rate_%"] = (
        summary["casualty_crashes"] / summary["total_crashes"] * 100
    ).round(1)

    summary["school_zone_share_%"] = (
        summary["school_zone_crashes"] / summary["total_crashes"] * 100
    ).round(1)

    return summary


def render_hotspots_tab(filtered_df: pd.DataFrame) -> None:
    st.markdown(
        '<div class="section-title">2. Hotspot LGAs and school-zone check</div>',
        unsafe_allow_html=True,
    )

    if LGA_COL not in filtered_df.columns:
        st.warning("LGA column was not found in this dataset.")
        return

    lga_summary = build_lga_summary(filtered_df)

    if lga_summary.empty:
        st.info("No records after filters.")
        return

    top_n = st.slider("Number of hotspot LGAs to show", 5, 30, 15, 5)
    top_lga_summary = lga_summary.head(top_n)

    c1, c2 = st.columns([1.1, 0.9])

    with c1:
        fig_lga = px.bar(
            top_lga_summary.sort_values("total_crashes", ascending=True),
            x="total_crashes",
            y=LGA_COL,
            orientation="h",
            text="total_crashes",
            title=f"Top {top_n} LGAs by crash count",
        )

        fig_lga.update_layout(
            template="plotly_dark",
            xaxis_title="Total crashes",
            yaxis_title="LGA",
            title_x=0.02,
            height=560,
            margin=dict(l=20, r=20, t=60, b=40),
        )

        st.plotly_chart(fig_lga, use_container_width=True)

    with c2:
        top_lga = top_lga_summary.iloc[0][LGA_COL]
        top_value = int(top_lga_summary.iloc[0]["total_crashes"])
        top_school = int(top_lga_summary.iloc[0]["school_zone_crashes"])

        st.markdown(
            f"""
            <div class="warning-box">
            <b>Highest hotspot:</b> {top_lga}<br>
            <b>Total crashes:</b> {top_value:,}<br>
            <b>School-zone crashes:</b> {top_school:,}<br><br>
            This area should be reviewed first for road design, speed limit, enforcement, signal timing,
            and school-zone safety checks.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### Hotspot statistics table")

    st.dataframe(
        top_lga_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Inspect one hotspot area")

    inspect_lga = st.selectbox(
        "Choose an LGA to inspect",
        options=lga_summary[LGA_COL].tolist(),
        index=0,
    )

    inspect_df = filtered_df[filtered_df[LGA_COL] == inspect_lga].copy()

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Selected LGA crashes", format_int(len(inspect_df)))
    m2.metric("Fatal", format_int(int(inspect_df["is_fatal"].sum())))
    m3.metric("Injury", format_int(int(inspect_df["is_injury"].sum())))

    if SCHOOL_ZONE_LOCATION_COL in inspect_df.columns:
        m4.metric(
            "School-zone",
            format_int(int(is_yes_series(inspect_df[SCHOOL_ZONE_LOCATION_COL]).sum())),
        )

    if LAT_COL in inspect_df.columns and LON_COL in inspect_df.columns:
        hover_cols = [
            col
            for col in [
                TIME_COL,
                SCHOOL_ZONE_LOCATION_COL,
                SCHOOL_ZONE_ACTIVE_COL,
            ]
            if col in inspect_df.columns
        ]

        map_df = inspect_df.dropna(subset=[LAT_COL, LON_COL]).copy()

        if len(map_df) > 3000:
            map_df = map_df.sample(3000, random_state=42)

        if not map_df.empty:
            fig_map = px.scatter_mapbox(
                map_df,
                lat=LAT_COL,
                lon=LON_COL,
                color=SEVERITY_COL if SEVERITY_COL in map_df.columns else None,
                hover_data=hover_cols,
                zoom=9,
                height=520,
                title=f"Crash points in {inspect_lga}",
            )

            fig_map.update_layout(
                template="plotly_dark",
                mapbox_style="open-street-map",
                margin={"r": 0, "t": 45, "l": 0, "b": 0},
                title_x=0.02,
            )

            st.plotly_chart(fig_map, use_container_width=True)

        else:
            st.info("No valid latitude/longitude records for this selected LGA.")