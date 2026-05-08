from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import pandas as pd
import streamlit as st


DEFAULT_CRASH_PATH = Path(__file__).resolve().parent / "data" / "nsw_crash_data.xlsx"
DEFAULT_POPULATION_PATH = Path(__file__).resolve().parent / "data" / "abs_population_lga_2024.csv"
MISSING_LABEL = "Not recorded / Not applicable"

MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]

TWO_HOUR_ORDER = [
    "Midnight - 01:59",
    "02:00 - 03:59",
    "04:00 - 05:59",
    "06:00 - 07:59",
    "08:00 - 09:59",
    "10:00 - 11:59",
    "Noon - 13:59",
    "14:00 - 15:59",
    "16:00 - 17:59",
    "18:00 - 19:59",
    "20:00 - 21:59",
    "22:00 - Midnight",
]

SPARSE_CATEGORICAL_COLUMNS = [
    "Identifying feature",
    "Route no.",
    "Primary permanent feature",
    "Primary temporary feature",
    "Primary hazardous feature",
    "DCA supplement",
    "Other TU type",
]

LGA_NAME_ALIASES = {
    "armidaleregional": "armidale",
    "bathurstregional": "bathurst",
    "dubboregional": "dubbo",
    "midwesternregional": "midwestern",
    "queanbeyanpalerangregional": "queanbeyanpalerang",
    "snowymonaroregional": "snowymonaro",
    "tamworthregional": "tamworth",
    "unincorporated": "unincorporatednsw",
}


@dataclass(frozen=True)
class DataBundle:
    crash_df: pd.DataFrame
    crash_missing_profile: pd.DataFrame
    population_df: pd.DataFrame
    crash_path: Path


def _ordered_text(series: pd.Series, categories: list[str]) -> pd.Series:
    return pd.Categorical(series.astype("string"), categories=categories, ordered=True)


def normalize_lga_name(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).lower().replace("(nsw)", "")
    compact = re.sub(r"[^a-z0-9]+", "", text)
    return LGA_NAME_ALIASES.get(compact, compact)


def _add_crash_derivatives(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()

    for column in SPARSE_CATEGORICAL_COLUMNS:
        if column in enriched.columns:
            enriched[column] = enriched[column].astype("string").fillna(MISSING_LABEL)

    enriched["Month of crash"] = _ordered_text(enriched["Month of crash"], MONTH_ORDER)
    enriched["Day of week of crash"] = _ordered_text(enriched["Day of week of crash"], WEEKDAY_ORDER)
    enriched["Two-hour intervals"] = _ordered_text(enriched["Two-hour intervals"], TWO_HOUR_ORDER)

    enriched["Total casualties"] = (
        enriched["No. killed"]
        + enriched["No. seriously injured"]
        + enriched["No. moderately injured"]
        + enriched["No. minor-other injured"]
    )
    enriched["Killed or seriously injured"] = enriched["No. killed"] + enriched["No. seriously injured"]
    enriched["Severity score"] = (
        enriched["No. killed"] * 4
        + enriched["No. seriously injured"] * 3
        + enriched["No. moderately injured"] * 2
        + enriched["No. minor-other injured"]
    )
    enriched["Weekend"] = enriched["Day of week of crash"].isin(["Saturday", "Sunday"])
    enriched["Has casualties"] = enriched["Total casualties"] > 0

    return enriched


def build_missing_profile(df: pd.DataFrame) -> pd.DataFrame:
    profile = pd.DataFrame(
        {
            "field": df.columns,
            "missing_count": df.isna().sum().values,
            "missing_percent": (df.isna().mean().values * 100).round(2),
        }
    )
    return profile.sort_values(["missing_count", "field"], ascending=[False, True]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_raw_crash_data(crash_path_text: str) -> pd.DataFrame:
    crash_path = Path(crash_path_text)
    df = pd.read_excel(crash_path)
    return df[df["Year of crash"] >= 2024].copy()


@st.cache_data(show_spinner=False)
def load_crash_data(crash_path_text: str) -> pd.DataFrame:
    return _add_crash_derivatives(load_raw_crash_data(crash_path_text))


@st.cache_data(show_spinner=False)
def load_population_data(population_path_text: str) -> pd.DataFrame:
    population_path = Path(population_path_text)
    population_df = pd.read_csv(population_path)
    population_df["lga_key"] = population_df["LGA name"].map(normalize_lga_name)
    population_df = population_df.drop_duplicates(subset=["lga_key"]).reset_index(drop=True)
    return population_df


def enrich_crash_with_population(crash_df: pd.DataFrame, population_df: pd.DataFrame) -> pd.DataFrame:
    enriched = crash_df.copy()
    enriched["lga_key"] = enriched["LGA"].map(normalize_lga_name)
    return enriched.merge(
        population_df[["lga_key", "Population 2024"]],
        on="lga_key",
        how="left",
    )


def load_bundle(crash_path_text: str, population_path_text: str) -> DataBundle:
    crash_path = Path(crash_path_text)
    raw_crash_df = load_raw_crash_data(str(crash_path))
    population_df = load_population_data(population_path_text)

    return DataBundle(
        crash_df=enrich_crash_with_population(load_crash_data(str(crash_path)), population_df),
        crash_missing_profile=build_missing_profile(raw_crash_df),
        population_df=population_df,
        crash_path=crash_path,
    )
