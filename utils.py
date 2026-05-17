import os
import re
from typing import Optional, Tuple

import pandas as pd
import streamlit as st


CSV_PATH = "data/nsw_crash_data_clean.csv"
FILTERED_OUTPUT_PATH = "data/nsw_crash_data_2024_onward.csv"

YEAR_COL = "year_of_crash"
MONTH_COL = "month_of_crash"
DAY_COL = "day_of_week_of_crash"
TIME_COL = "two-hour_intervals"
LGA_COL = "lga"
SEVERITY_COL = "degree_of_crash"
DETAIL_SEVERITY_COL = "degree_of_crash_-_detailed"
LAT_COL = "latitude"
LON_COL = "longitude"
SCHOOL_ZONE_LOCATION_COL = "school_zone_location"
SCHOOL_ZONE_ACTIVE_COL = "school_zone_active"
WEATHER_COL = "weather"
LIGHT_COL = "natural_lighting"
SURFACE_COL = "surface_condition"
ROAD_SURFACE_COL = "road_surface"
STREET_LIGHTING_COL = "street_lighting"
SPEED_COL = "speed_limit"
TYPE_LOCATION_COL = "type_of_location"

MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

MONTH_TO_NUM = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}

DAY_ORDER = [
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
]

TIME_ORDER = [
    "00:01 - 01:59",
    "02:00 - 03:59",
    "04:00 - 05:59",
    "06:00 - 07:59",
    "08:00 - 09:59",
    "10:00 - 11:59",
    "12:00 - 13:59",
    "14:00 - 15:59",
    "16:00 - 17:59",
    "18:00 - 19:59",
    "20:00 - 21:59",
    "22:00 - Midnight",
    "Unknown",
]


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise column names for easier coding.
    """
    df = df.copy()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    return df


def get_season(month_number: Optional[float]) -> str:
    """
    Australian seasons:
    Summer = Dec-Feb
    Autumn = Mar-May
    Winter = Jun-Aug
    Spring = Sep-Nov
    """
    if pd.isna(month_number):
        return "Unknown"

    month_number = int(month_number)

    if month_number in [12, 1, 2]:
        return "Summer"

    if month_number in [3, 4, 5]:
        return "Autumn"

    if month_number in [6, 7, 8]:
        return "Winter"

    if month_number in [9, 10, 11]:
        return "Spring"

    return "Unknown"


def extract_start_hour(interval: str) -> Optional[int]:
    """
    Extract starting hour from two-hour interval labels.
    Example: '08:00 - 09:59' -> 8
    """
    if pd.isna(interval):
        return None

    match = re.match(r"^(\d{2}):", str(interval))

    if match:
        return int(match.group(1))

    return None


def get_time_band(interval: str) -> str:
    """
    Create policy-friendly time bands from two-hour intervals.
    """
    hour = extract_start_hour(interval)

    if hour is None:
        return "Unknown"

    if hour in [6, 8]:
        return "AM peak / school commute"

    if hour in [16, 18]:
        return "PM peak / evening commute"

    if hour in [10, 12, 14]:
        return "Midday / afternoon"

    if hour in [20, 22]:
        return "Evening / night"

    if hour in [0, 2, 4]:
        return "Late night / early morning"

    return "Other"


def is_peak_time(interval: str) -> bool:
    """
    Broad Australian commute/school travel windows:
    06:00-09:59 and 16:00-19:59.
    """
    return get_time_band(interval) in [
        "AM peak / school commute",
        "PM peak / evening commute",
    ]


def is_yes_series(series: pd.Series) -> pd.Series:
    """
    Convert values such as Yes / Y / True / 1 into boolean True.
    """
    return (
        series.fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(["yes", "y", "true", "1"])
    )


def add_engineered_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add reusable fields used by dashboard charts.
    """
    df = df.copy()

    numeric_cols = [
        YEAR_COL,
        LAT_COL,
        LON_COL,
        "no._killed",
        "no._seriously_injured",
        "no._moderately_injured",
        "no._minor-other_injured",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if MONTH_COL in df.columns:
        df["month_num"] = df[MONTH_COL].map(MONTH_TO_NUM)

        df["month_label"] = pd.Categorical(
            df[MONTH_COL],
            categories=MONTH_ORDER,
            ordered=True,
        )

        df["season"] = df["month_num"].apply(get_season)

    if DAY_COL in df.columns:
        df["day_label"] = pd.Categorical(
            df[DAY_COL],
            categories=DAY_ORDER,
            ordered=True,
        )

    if TIME_COL in df.columns:
        df["time_label"] = pd.Categorical(
            df[TIME_COL],
            categories=TIME_ORDER,
            ordered=True,
        )

        df["time_band"] = df[TIME_COL].apply(get_time_band)
        df["is_peak_commute"] = df[TIME_COL].apply(is_peak_time)

    if SEVERITY_COL in df.columns:
        sev = df[SEVERITY_COL].astype(str).str.lower()

        df["is_fatal"] = sev.str.contains("fatal", na=False)
        df["is_injury"] = sev.str.contains("injury", na=False)
        df["is_casualty"] = df["is_fatal"] | df["is_injury"]

    else:
        df["is_fatal"] = False
        df["is_injury"] = False
        df["is_casualty"] = False

    return df


def load_data() -> pd.DataFrame:
    """
    Load clean CSV, keep 2024 onward, and add engineered fields.
    This function is intentionally not decorated with st.cache_data so that
    data_check.py can run as a normal Python script without Streamlit runtime warnings.
    """
    if not os.path.exists(CSV_PATH):
        st.error(
            f"Cannot find {CSV_PATH}. Put nsw_crash_data_clean.csv inside the data folder first."
        )
        st.stop()

    df = pd.read_csv(CSV_PATH, low_memory=False)
    df = clean_columns(df)

    if YEAR_COL not in df.columns:
        st.error(f"Cannot find required column: {YEAR_COL}")
        st.stop()

    df[YEAR_COL] = pd.to_numeric(df[YEAR_COL], errors="coerce")

    # Keep 2024 and later only.
    # This removes 2023 and earlier.
    df = df[df[YEAR_COL] >= 2024].copy()

    df = add_engineered_fields(df)

    try:
        os.makedirs(os.path.dirname(FILTERED_OUTPUT_PATH), exist_ok=True)
        df.to_csv(FILTERED_OUTPUT_PATH, index=False)
    except Exception:
        pass

    return df


def apply_sidebar_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, int]:
    """
    Apply dashboard filters and return:
    1. filtered dataframe
    2. selected what-if scenario reduction percentage
    """
    st.sidebar.markdown("## 🔎 Filters")
    st.sidebar.caption("Dataset is already filtered to 2024 onward.")

    filtered_df = df.copy()

    if MONTH_COL in filtered_df.columns:
        selected_months = st.sidebar.multiselect(
            "Month",
            options=MONTH_ORDER,
            default=MONTH_ORDER,
        )

        filtered_df = filtered_df[filtered_df[MONTH_COL].isin(selected_months)]

    if LGA_COL in filtered_df.columns:
        lga_options = sorted(filtered_df[LGA_COL].dropna().astype(str).unique())

        selected_lgas = st.sidebar.multiselect(
            "LGA / Area",
            options=lga_options,
            default=[],
        )

        if selected_lgas:
            filtered_df = filtered_df[
                filtered_df[LGA_COL].astype(str).isin(selected_lgas)
            ]

    if SEVERITY_COL in filtered_df.columns:
        severity_options = sorted(
            filtered_df[SEVERITY_COL].dropna().astype(str).unique()
        )

        selected_severity = st.sidebar.multiselect(
            "Crash outcome",
            options=severity_options,
            default=severity_options,
        )

        filtered_df = filtered_df[
            filtered_df[SEVERITY_COL].astype(str).isin(selected_severity)
        ]

    if SCHOOL_ZONE_LOCATION_COL in filtered_df.columns:
        school_options = sorted(
            filtered_df[SCHOOL_ZONE_LOCATION_COL].dropna().astype(str).unique()
        )

        selected_school = st.sidebar.multiselect(
            "School zone location",
            options=school_options,
            default=school_options,
        )

        filtered_df = filtered_df[
            filtered_df[SCHOOL_ZONE_LOCATION_COL].astype(str).isin(selected_school)
        ]

    if SPEED_COL in filtered_df.columns:
        speed_options = sorted(filtered_df[SPEED_COL].dropna().astype(str).unique())

        selected_speed = st.sidebar.multiselect(
            "Speed limit",
            options=speed_options,
            default=[],
        )

        if selected_speed:
            filtered_df = filtered_df[
                filtered_df[SPEED_COL].astype(str).isin(selected_speed)
            ]

    st.sidebar.markdown("---")

    scenario_reduction = 20
    return filtered_df, scenario_reduction


def format_int(value) -> str:
    """
    Python 3.9 compatible number formatter.
    """
    try:
        return f"{int(value):,}"
    except Exception:
        return "0"


def make_count_df(
    df: pd.DataFrame,
    col: str,
    top_n: Optional[int] = None,
) -> pd.DataFrame:
    out = df[col].fillna("Unknown").astype(str).value_counts().reset_index()
    out.columns = [col, "crash_count"]

    if top_n:
        out = out.head(top_n)

    return out


def make_condition_summary(
    df: pd.DataFrame,
    col: str,
    min_records: int = 20,
) -> pd.DataFrame:
    temp = df.copy()
    temp[col] = temp[col].fillna("Unknown").astype(str)

    summary = (
        temp.groupby(col)
        .agg(
            crash_count=(col, "size"),
            fatal_crashes=("is_fatal", "sum"),
            casualty_crashes=("is_casualty", "sum"),
        )
        .reset_index()
    )

    summary["casualty_rate_%"] = (
        summary["casualty_crashes"] / summary["crash_count"] * 100
    ).round(1)

    summary["fatal_rate_%"] = (
        summary["fatal_crashes"] / summary["crash_count"] * 100
    ).round(2)

    summary = summary[summary["crash_count"] >= min_records]

    return summary.sort_values("crash_count", ascending=False)


def render_css() -> None:
    st.markdown(
        """
        <style>
        .main {
            background-color: #0E1117;
        }

        .section-title {
            font-size: 30px;
            font-weight: 800;
            margin-top: 14px;
            margin-bottom: 8px;
        }

        .insight-box {
            background-color: #111827;
            padding: 16px;
            border-left: 6px solid #ef4444;
            border-radius: 12px;
            margin-top: 10px;
            margin-bottom: 18px;
        }

        .action-box {
            background-color: #102a1f;
            padding: 16px;
            border-left: 6px solid #22c55e;
            border-radius: 12px;
            margin-top: 10px;
            margin-bottom: 18px;
        }

        .warning-box {
            background-color: #2b1d12;
            padding: 16px;
            border-left: 6px solid #f59e0b;
            border-radius: 12px;
            margin-top: 10px;
            margin-bottom: 18px;
        }

        .small-caption {
            color: #9ca3af;
            font-size: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )