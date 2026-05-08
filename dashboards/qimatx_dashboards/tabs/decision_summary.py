import pandas as pd
import streamlit as st

from utils import format_int


def render_decision_summary_tab(
    filtered_df: pd.DataFrame,
    scenario_reduction: int,
) -> None:
    st.markdown(
        '<div class="section-title">5. Decision summary and intervention logic</div>',
        unsafe_allow_html=True,
    )

    total_crashes = len(filtered_df)
    estimated_prevented = int(total_crashes * scenario_reduction / 100)
    remaining_crashes = total_crashes - estimated_prevented

    s1, s2, s3 = st.columns(3)

    s1.metric("Current crash load", format_int(total_crashes))

    s2.metric(
        f"Estimated prevented / improved ({scenario_reduction}%)",
        format_int(estimated_prevented),
    )

    s3.metric("Projected remaining", format_int(remaining_crashes))

    st.markdown(
        f"""
        <div class="action-box">
        <h3>What-if scenario interpretation</h3>
        A <b>{scenario_reduction}%</b> improvement scenario is useful as an ambitious target for hotspot-based intervention.
        It should not be read only as “fewer crashes”. It can also represent a broader road-network benefit:
        safer intersections, better signal timing, smoother travel flow, fewer disruption points, and more reliable routes for drivers,
        buses, pedestrians, and school-zone users.
        <br><br>
        Under the current filters, this scenario suggests approximately <b>{estimated_prevented:,}</b> crashes or disruption events could be prevented or reduced,
        leaving around <b>{remaining_crashes:,}</b> remaining incidents in the selected view.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="action-box">
        <h3>Recommended dashboard story</h3>
        <ol>
            <li><b>Start with overall burden:</b> show how many crashes, fatalities, injuries, and school-zone cases exist in 2024 onward data.</li>
            <li><b>Move to place-based risk:</b> identify LGAs with the highest crash count and check school-zone involvement.</li>
            <li><b>Then inspect timing:</b> test whether crashes concentrate during weekday commute and school travel windows.</li>
            <li><b>Finally check external context:</b> weather, lighting, surface, speed limit, and location type can guide targeted interventions.</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="insight-box">
        <b>Suggested call to action:</b> Prioritise the LGAs and time windows where crash volume,
        casualty rate, school-zone exposure, and repeated temporal concentration overlap.
        This turns the dashboard from descriptive reporting into a practical decision-support tool for safer and more efficient movement across NSW roads.
        </div>
        """,
        unsafe_allow_html=True,
    )