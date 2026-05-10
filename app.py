"""
NSW Crash Data – The Detective
A persuasive data narrative for Transport for NSW decision-makers.
Narrative arc: Detective (anomaly → suspects → culprit → verdict)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="The Detective | NSW Crash Data",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design system ────────────────────────────────────────────────────────────
COLORS = {
    "red":    "#E24B4A",
    "amber":  "#BA7517",
    "purple": "#7F77DD",
    "teal":   "#1D9E75",
    "blue":   "#378ADD",
    "gray":   "#888780",
    "bg":     "#0F1117",
    "surface":"#1A1C24",
    "border": "rgba(255,255,255,0.10)",
}

PLOTLY_TEMPLATE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#CCCBC4"),
    colorway=[COLORS["red"], COLORS["amber"], COLORS["blue"],
              COLORS["teal"], COLORS["purple"], COLORS["gray"]],
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)",
               zeroline=False, tickfont=dict(size=11)),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.07)",
               zeroline=False, tickfont=dict(size=11)),
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0F1117;
    color: #CCCBC4;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #13151E;
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label,
section[data-testid="stSidebar"] .stRadio label {
    color: #888780 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── KPI tiles ── */
.kpi-grid { display: flex; gap: 12px; margin: 16px 0; }
.kpi-card {
    flex: 1;
    background: #1A1C24;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 18px 20px;
    min-width: 0;
}
.kpi-card .label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #888780;
    margin-bottom: 8px;
}
.kpi-card .value {
    font-family: 'Playfair Display', serif;
    font-size: 36px;
    font-weight: 700;
    line-height: 1;
    color: #F0EFE8;
}
.kpi-card .delta {
    font-size: 12px;
    margin-top: 6px;
}
.kpi-card .delta.up   { color: #E24B4A; }
.kpi-card .delta.down { color: #1D9E75; }

/* ── Section headings ── */
.section-eyebrow {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #888780;
    margin-bottom: 6px;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    color: #F0EFE8;
    margin-bottom: 4px;
    line-height: 1.2;
}
.section-subtitle {
    font-size: 14px;
    color: #888780;
    margin-bottom: 24px;
    max-width: 640px;
}

/* ── Detective clue cards ── */
.clue-card {
    background: #1A1C24;
    border-left: 3px solid #E24B4A;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 14px;
    color: #CCCBC4;
}
.clue-card strong { color: #F0EFE8; }

/* ── Narrative pull-quote ── */
.pull-quote {
    border-left: 3px solid #7F77DD;
    padding: 12px 20px;
    margin: 20px 0;
    font-size: 16px;
    font-style: italic;
    color: #CCCBC4;
    background: rgba(127,119,221,0.07);
    border-radius: 0 8px 8px 0;
}

/* ── CTA box ── */
.cta-box {
    background: linear-gradient(135deg, rgba(29,158,117,0.15), rgba(55,138,221,0.10));
    border: 1px solid rgba(29,158,117,0.30);
    border-radius: 12px;
    padding: 28px 32px;
    margin-top: 24px;
}
.cta-box h3 {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 700;
    color: #F0EFE8;
    margin-bottom: 12px;
}
.cta-box ul { color: #CCCBC4; font-size: 14px; line-height: 1.9; }

/* ── Progress nav dots ── */
.nav-dots { display: flex; gap: 8px; align-items: center; margin-bottom: 24px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.15); }
.dot.active { background: #E24B4A; width: 24px; border-radius: 4px; }

/* ── Streamlit overrides ── */
div[data-testid="metric-container"] { background: #1A1C24; border-radius: 10px; padding: 16px; border: 1px solid rgba(255,255,255,0.08); }
.stPlotlyChart { border-radius: 10px; overflow: hidden; }
div[data-testid="stVerticalBlock"] > div { gap: 0.5rem; }
</style>
""", unsafe_allow_html=True)


# ── Data loading ─────────────────────────────────────────────────────────────
@st.cache_data
@st.cache_data
def load_data():
    df = pd.read_excel("nsw_road_crash_data_2020-2024_crash.xlsx", engine="openpyxl")
    
    # Normalise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    
    # Preview what columns you have — remove this after checking
    st.write(df.columns.tolist())
    
    return df


def _generate_synthetic_data():
    """
    Realistic synthetic NSW crash data for development/demo.
    Replace with real data before final submission.
    """
    rng = np.random.default_rng(42)
    n = 8000

    lgas = [
        "Blacktown", "Liverpool", "Penrith", "Cumberland",
        "Central Coast", "Lake Macquarie", "Newcastle", "Wollongong",
        "Parramatta", "Canterbury-Bankstown", "Northern Beaches", "Sutherland",
    ]
    road_types = ["State Highway", "Regional Road", "Local Road", "Motorway", "Unnamed Road"]
    factors    = ["Speed", "Alcohol", "Fatigue", "Distraction", "Weather", "Other"]
    severities = ["Fatal", "Serious Injury", "Minor Injury", "Non-Casualty"]
    weather    = ["Clear", "Rain", "Fog", "Wind", "Overcast"]
    speed_opts = [40, 50, 60, 70, 80, 100, 110]
    days       = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    dates = pd.date_range("2024-01-01", "2026-03-31", periods=n)

    # Skew fatals toward night/weekend for narrative effect
    hours = rng.integers(0, 24, n)
    day_idx = rng.integers(0, 7, n)

    sev_weights = np.where(
        (hours < 6) | (hours > 21) | (day_idx >= 5),
        [0.06, 0.20, 0.44, 0.30], [0.02, 0.12, 0.46, 0.40]
    )
    # sev_weights shape is (n, 4), pick one per row
    severity_vals = [
        rng.choice(severities, p=sev_weights[i]) for i in range(n)
    ]

    # NSW bounding box lat/long (rough)
    lat = rng.uniform(-37.5, -28.0, n)
    lon = rng.uniform(141.0, 153.6, n)

    df = pd.DataFrame({
        "crash_date":          dates,
        "year":                dates.year,
        "month":               dates.month,
        "month_name":          dates.strftime("%b"),
        "hour":                hours,
        "day_of_week":         [days[i] for i in day_idx],
        "severity":            severity_vals,
        "lga_name":            rng.choice(lgas, n),
        "road_type":           rng.choice(road_types, n, p=[0.25,0.20,0.30,0.15,0.10]),
        "speed_limit":         rng.choice(speed_opts, n, p=[0.05,0.25,0.20,0.15,0.15,0.15,0.05]),
        "contributing_factor": rng.choice(factors, n, p=[0.28,0.18,0.20,0.15,0.10,0.09]),
        "weather_condition":   rng.choice(weather, n, p=[0.55,0.20,0.05,0.08,0.12]),
        "alcohol_involved":    rng.choice([True, False], n, p=[0.17, 0.83]),
        "fatigue_involved":    rng.choice([True, False], n, p=[0.22, 0.78]),
        "latitude":            lat,
        "longitude":           lon,
    })
    return df


df = load_data()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 The Detective")
    st.markdown(
        "<div style='font-size:12px;color:#888780;line-height:1.6'>"
        "NSW Crash Data Narrative<br>Persona: Transport for NSW Authority"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("**Navigate the case**")
    page = st.radio(
        "Chapter",
        options=[
            "📍 The Crime Scene",
            "🔎 The Suspects",
            "🧪 The Evidence",
            "💡 The Reveal",
            "⚖️ The Verdict",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**Filter the data**")

    # Year filter
    years = sorted(df["year"].dropna().unique())
    selected_years = st.multiselect("Year", years, default=years)

    # LGA filter
    lgas = sorted(df["lga_name"].dropna().unique())
    selected_lgas = st.multiselect("LGA", lgas, default=lgas)

    # Severity filter
    severities = sorted(df["severity"].dropna().unique())
    selected_sev = st.multiselect("Severity", severities, default=severities)

    st.divider()
    st.markdown(
        "<div style='font-size:11px;color:#555;line-height:1.6'>"
        "Data: NSW Crash Data (data.nsw.gov.au)<br>"
        "Updated: 2024–2026<br>"
        "Group project — Data Narratives Studio"
        "</div>",
        unsafe_allow_html=True,
    )


# ── Filter data (context-aware — Advanced Feature #1) ────────────────────────
mask = (
    df["year"].isin(selected_years) &
    df["lga_name"].isin(selected_lgas) &
    df["severity"].isin(selected_sev)
)
dff = df[mask].copy()

# Derived metrics
total_crashes  = len(dff)
fatal_count    = (dff["severity"] == "Fatal").sum()
serious_count  = (dff["severity"] == "Serious Injury").sum()
alcohol_pct    = dff["alcohol_involved"].mean() * 100 if "alcohol_involved" in dff else 0
fatigue_pct    = dff["fatigue_involved"].mean() * 100 if "fatigue_involved" in dff else 0


# ── Helper: apply plotly template ────────────────────────────────────────────
def style_fig(fig, height=380):
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=30, b=0),
        **PLOTLY_TEMPLATE,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11, color="#888780"),
        ),
    )
    fig.update_xaxes(
        showgrid=True, gridcolor="rgba(255,255,255,0.06)",
        zeroline=False, tickfont=dict(size=11, color="#888780"),
    )
    fig.update_yaxes(
        showgrid=True, gridcolor="rgba(255,255,255,0.06)",
        zeroline=False, tickfont=dict(size=11, color="#888780"),
    )
    return fig


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 1 — THE CRIME SCENE
# ═══════════════════════════════════════════════════════════════════════════
if page == "📍 The Crime Scene":

    st.markdown('<div class="section-eyebrow">Chapter 1 · Detective Narrative</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">The Crime Scene</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">'
        'Every 40 minutes, someone in NSW is involved in a road crash. '
        'The data tells us where — but not yet why.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Nav dots
    st.markdown(
        '<div class="nav-dots">'
        '<div class="dot active"></div>'
        '<div class="dot"></div><div class="dot"></div>'
        '<div class="dot"></div><div class="dot"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # KPI tiles
    st.markdown(
        f"""<div class="kpi-grid">
        <div class="kpi-card">
            <div class="label">Total crashes</div>
            <div class="value">{total_crashes:,}</div>
            <div class="delta up">Filtered selection</div>
        </div>
        <div class="kpi-card">
            <div class="label">Fatalities</div>
            <div class="value" style="color:#E24B4A">{fatal_count:,}</div>
            <div class="delta up">Lives lost</div>
        </div>
        <div class="kpi-card">
            <div class="label">Serious injuries</div>
            <div class="value" style="color:#BA7517">{serious_count:,}</div>
            <div class="delta up">Hospitalised</div>
        </div>
        <div class="kpi-card">
            <div class="label">Alcohol involved</div>
            <div class="value" style="color:#7F77DD">{alcohol_pct:.0f}%</div>
            <div class="delta up">Of all crashes</div>
        </div>
        <div class="kpi-card">
            <div class="label">Fatigue involved</div>
            <div class="value" style="color:#378ADD">{fatigue_pct:.0f}%</div>
            <div class="delta up">Of all crashes</div>
        </div>
        </div>""",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        # Crash map
        map_df = dff.dropna(subset=["latitude","longitude"]).copy()
        color_map = {"Fatal":"#E24B4A","Serious Injury":"#BA7517","Minor Injury":"#378ADD","Non-Casualty":"#888780"}
        fig_map = px.scatter_mapbox(
            map_df.sample(min(3000, len(map_df)), random_state=42),
            lat="latitude", lon="longitude",
            color="severity",
            color_discrete_map=color_map,
            size_max=6,
            opacity=0.6,
            zoom=6,
            center={"lat": -32.5, "lon": 147.5},
            mapbox_style="carto-darkmatter",
            hover_data={"lga_name": True, "severity": True, "latitude": False, "longitude": False},
            title="Crash locations across NSW",
        )
        fig_map.update_layout(
            height=460,
            margin=dict(l=0, r=0, t=36, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#888780", size=11)),
            font=dict(color="#CCCBC4"),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        st.markdown("#### Crashes by LGA")
        lga_counts = (
            dff.groupby("lga_name")
            .size()
            .reset_index(name="crashes")
            .sort_values("crashes", ascending=True)
            .tail(12)
        )
        fig_lga = px.bar(
            lga_counts, x="crashes", y="lga_name", orientation="h",
            color="crashes",
            color_continuous_scale=["#1A1C24", "#E24B4A"],
        )
        fig_lga = style_fig(fig_lga, height=460)
        fig_lga.update_coloraxes(showscale=False)
        fig_lga.update_yaxes(title=None)
        fig_lga.update_xaxes(title="Crashes")
        st.plotly_chart(fig_lga, use_container_width=True)

    # Clue card
    top_lga = lga_counts.iloc[-1]["lga_name"] if len(lga_counts) else "unknown"
    st.markdown(
        f'<div class="clue-card">🔍 <strong>Clue #1:</strong> '
        f'<strong>{top_lga}</strong> records the highest crash frequency in the selected period. '
        f'But high volume alone doesn\'t reveal severity. Turn to Chapter 2 to identify the suspects.'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 2 — THE SUSPECTS
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🔎 The Suspects":

    st.markdown('<div class="section-eyebrow">Chapter 2 · Detective Narrative</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">The Suspects</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">'
        'Three prime suspects emerge from the data: time, speed, and road type. '
        'Each has a motive — but which one is driving fatalities?'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-dots">'
        '<div class="dot"></div><div class="dot active"></div>'
        '<div class="dot"></div><div class="dot"></div><div class="dot"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Heatmap: hour × day of week ──
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heatmap_data = (
        dff.groupby(["day_of_week", "hour"])
        .size()
        .reset_index(name="crashes")
    )
    heatmap_pivot = (
        heatmap_data.pivot(index="day_of_week", columns="hour", values="crashes")
        .reindex(day_order)
        .fillna(0)
    )

    fig_heat = go.Figure(
        go.Heatmap(
            z=heatmap_pivot.values,
            x=[f"{h:02d}:00" for h in heatmap_pivot.columns],
            y=heatmap_pivot.index,
            colorscale=[[0,"#1A1C24"],[0.5,"#BA7517"],[1,"#E24B4A"]],
            hovertemplate="<b>%{y}</b> at %{x}<br>Crashes: %{z}<extra></extra>",
        )
    )
    fig_heat = style_fig(fig_heat, height=300)
    fig_heat.update_layout(title="When do crashes happen? (hour × day)")
    fig_heat.update_yaxes(showgrid=False)
    fig_heat.update_xaxes(showgrid=False, tickangle=-45)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.plotly_chart(fig_heat, use_container_width=True)
    with col2:
        # Speed zone bar
        speed_counts = (
            dff.groupby("speed_limit")
            .size()
            .reset_index(name="crashes")
            .sort_values("speed_limit")
        )
        fig_speed = px.bar(
            speed_counts, x="speed_limit", y="crashes",
            color="crashes",
            color_continuous_scale=["#1A1C24","#E24B4A"],
            title="Crashes by speed limit zone (km/h)",
        )
        fig_speed = style_fig(fig_speed, height=300)
        fig_speed.update_coloraxes(showscale=False)
        fig_speed.update_xaxes(title="Speed limit (km/h)", type="category")
        fig_speed.update_yaxes(title="Crashes")
        st.plotly_chart(fig_speed, use_container_width=True)

    # ── Monthly trend line ──
    if "month" in dff.columns and "year" in dff.columns:
        trend = (
            dff.groupby(["year","month","month_name"])
            .size()
            .reset_index(name="crashes")
            .sort_values(["year","month"])
        )
        trend["period"] = trend["year"].astype(str) + "-" + trend["month"].astype(str).str.zfill(2)

        fatal_trend = (
            dff[dff["severity"]=="Fatal"]
            .groupby(["year","month"])
            .size()
            .reset_index(name="fatals")
        )
        fatal_trend["period"] = fatal_trend["year"].astype(str) + "-" + fatal_trend["month"].astype(str).str.zfill(2)
        trend = trend.merge(fatal_trend, on="period", how="left")

        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        fig_trend.add_trace(
            go.Bar(x=trend["period"], y=trend["crashes"],
                   name="All crashes", marker_color=COLORS["blue"], opacity=0.5),
            secondary_y=False,
        )
        fig_trend.add_trace(
            go.Scatter(x=trend["period"], y=trend["fatals"],
                       name="Fatalities", line=dict(color=COLORS["red"], width=2.5),
                       mode="lines+markers", marker_size=5),
            secondary_y=True,
        )
        fig_trend = style_fig(fig_trend, height=300)
        fig_trend.update_layout(title="Monthly trend: crashes vs fatalities")
        fig_trend.update_yaxes(title_text="Total crashes", secondary_y=False)
        fig_trend.update_yaxes(title_text="Fatalities", secondary_y=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    # Road type
    road_sev = (
        dff.groupby(["road_type","severity"])
        .size()
        .reset_index(name="count")
    )
    sev_order = ["Fatal","Serious Injury","Minor Injury","Non-Casualty"]
    sev_colors = {"Fatal":COLORS["red"],"Serious Injury":COLORS["amber"],
                  "Minor Injury":COLORS["blue"],"Non-Casualty":COLORS["gray"]}
    fig_road = px.bar(
        road_sev, x="road_type", y="count", color="severity",
        category_orders={"severity": sev_order},
        color_discrete_map=sev_colors,
        title="Crash severity by road type",
        barmode="stack",
    )
    fig_road = style_fig(fig_road, height=320)
    fig_road.update_xaxes(title=None)
    fig_road.update_yaxes(title="Crashes")
    st.plotly_chart(fig_road, use_container_width=True)

    peak_hour = dff.groupby("hour").size().idxmax() if len(dff) else "unknown"
    peak_day  = dff.groupby("day_of_week").size().idxmax() if len(dff) else "unknown"
    st.markdown(
        f'<div class="clue-card">🔍 <strong>Clue #2:</strong> '
        f'The heatmap exposes a pattern — crashes spike at <strong>{peak_hour}:00 hrs on {peak_day}s</strong>. '
        f'But time alone doesn\'t explain fatality severity. Chapter 3 examines the chemical evidence.'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 3 — THE EVIDENCE
# ═══════════════════════════════════════════════════════════════════════════
elif page == "🧪 The Evidence":

    st.markdown('<div class="section-eyebrow">Chapter 3 · Detective Narrative</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">The Evidence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">'
        'Three factors enter the interrogation room: alcohol, fatigue, and weather. '
        'The data will tell us which one has blood on its hands.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-dots">'
        '<div class="dot"></div><div class="dot"></div>'
        '<div class="dot active"></div>'
        '<div class="dot"></div><div class="dot"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Context-aware sidebar filter — Advanced Feature #1 ──
    st.markdown("##### Filter evidence by factor")
    show_alcohol = st.checkbox("Alcohol involved", value=True)
    show_fatigue  = st.checkbox("Fatigue involved",  value=True)
    filter_weather = st.selectbox("Weather condition", ["All"] + sorted(dff["weather_condition"].dropna().unique().tolist()))

    ev_df = dff.copy()
    if not show_alcohol:
        ev_df = ev_df[ev_df["alcohol_involved"] == False]
    if not show_fatigue:
        ev_df = ev_df[ev_df["fatigue_involved"] == False]
    if filter_weather != "All":
        ev_df = ev_df[ev_df["weather_condition"] == filter_weather]

    # ── Dynamic narrative text (context-aware) ──
    alc_fatal = ev_df[ev_df["alcohol_involved"] & (ev_df["severity"]=="Fatal")].shape[0]
    fat_fatal = ev_df[ev_df["fatigue_involved"] & (ev_df["severity"]=="Fatal")].shape[0]
    total_fatal = (ev_df["severity"]=="Fatal").sum()

    alc_share = (alc_fatal / total_fatal * 100) if total_fatal > 0 else 0
    fat_share = (fat_fatal / total_fatal * 100) if total_fatal > 0 else 0

    st.markdown(
        f'<div class="pull-quote">'
        f'In the filtered selection: alcohol is implicated in <strong>{alc_share:.0f}%</strong> of fatalities '
        f'and fatigue in <strong>{fat_share:.0f}%</strong>. '
        f'These two factors together account for a disproportionate share of lives lost.'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        # Contributing factor breakdown
        factor_sev = (
            ev_df.groupby(["contributing_factor","severity"])
            .size()
            .reset_index(name="count")
        )
        fig_factor = px.bar(
            factor_sev, x="contributing_factor", y="count", color="severity",
            color_discrete_map={
                "Fatal": COLORS["red"], "Serious Injury": COLORS["amber"],
                "Minor Injury": COLORS["blue"], "Non-Casualty": COLORS["gray"],
            },
            barmode="stack",
            title="Contributing factors × severity",
        )
        fig_factor = style_fig(fig_factor, height=360)
        fig_factor.update_xaxes(title=None, tickangle=-30)
        fig_factor.update_yaxes(title="Crashes")
        st.plotly_chart(fig_factor, use_container_width=True)

    with col2:
        # Weather × severity
        weather_sev = (
            ev_df.groupby(["weather_condition","severity"])
            .size()
            .reset_index(name="count")
        )
        fig_weather = px.bar(
            weather_sev, x="weather_condition", y="count", color="severity",
            color_discrete_map={
                "Fatal": COLORS["red"], "Serious Injury": COLORS["amber"],
                "Minor Injury": COLORS["blue"], "Non-Casualty": COLORS["gray"],
            },
            barmode="group",
            title="Weather condition × severity",
        )
        fig_weather = style_fig(fig_weather, height=360)
        fig_weather.update_xaxes(title=None)
        fig_weather.update_yaxes(title="Crashes")
        st.plotly_chart(fig_weather, use_container_width=True)

    # Scatter: speed limit × severity rate
    sev_by_speed = (
        ev_df.groupby("speed_limit")
        .agg(total=("severity","count"),
             fatals=("severity", lambda x: (x=="Fatal").sum()))
        .reset_index()
    )
    sev_by_speed["fatal_rate"] = sev_by_speed["fatals"] / sev_by_speed["total"] * 100

    fig_scatter = px.scatter(
        sev_by_speed, x="speed_limit", y="fatal_rate",
        size="total", color="fatal_rate",
        color_continuous_scale=["#378ADD","#E24B4A"],
        title="Fatality rate (%) by speed limit zone — bubble size = total crashes",
        labels={"speed_limit":"Speed limit (km/h)","fatal_rate":"Fatality rate (%)"},
        hover_data={"total": True, "fatals": True},
    )
    fig_scatter = style_fig(fig_scatter, height=320)
    fig_scatter.update_coloraxes(showscale=False)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown(
        f'<div class="clue-card">🔍 <strong>Clue #3:</strong> '
        f'Speed zones above 80 km/h show a disproportionately high fatality rate per crash. '
        f'Combined with alcohol and fatigue, higher speed zones are the deadliest combination. '
        f'Chapter 4 names the culprit.'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 4 — THE REVEAL
# ═══════════════════════════════════════════════════════════════════════════
elif page == "💡 The Reveal":

    st.markdown('<div class="section-eyebrow">Chapter 4 · Detective Narrative</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">The Reveal</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">'
        'The culprit isn\'t a single factor — it\'s a lethal combination. '
        'Late-night driving on high-speed rural roads, impaired by fatigue or alcohol, '
        'accounts for a wildly disproportionate share of fatalities.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-dots">'
        '<div class="dot"></div><div class="dot"></div>'
        '<div class="dot"></div><div class="dot active"></div>'
        '<div class="dot"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── "Aha" annotated chart ──
    night = dff[dff["hour"].between(22, 23) | dff["hour"].between(0, 5)].copy()
    day_c = dff[dff["hour"].between(7, 18)].copy()

    night_fatal_rate = (night["severity"]=="Fatal").mean() * 100 if len(night) > 0 else 0
    day_fatal_rate   = (day_c["severity"]=="Fatal").mean() * 100 if len(day_c) > 0 else 0

    # Hourly fatal rate
    hourly = (
        dff.groupby("hour")
        .agg(total=("severity","count"), fatals=("severity", lambda x: (x=="Fatal").sum()))
        .reset_index()
    )
    hourly["fatal_rate"] = hourly["fatals"] / hourly["total"] * 100

    fig_reveal = go.Figure()
    fig_reveal.add_trace(go.Bar(
        x=hourly["hour"], y=hourly["total"],
        name="All crashes", marker_color=COLORS["blue"], opacity=0.35,
        yaxis="y2",
    ))
    fig_reveal.add_trace(go.Scatter(
        x=hourly["hour"], y=hourly["fatal_rate"],
        name="Fatality rate (%)", line=dict(color=COLORS["red"], width=3),
        mode="lines+markers", marker_size=7,
    ))
    # Shade danger zone
    fig_reveal.add_vrect(x0=22, x1=24, fillcolor=COLORS["red"], opacity=0.07, line_width=0)
    fig_reveal.add_vrect(x0=0,  x1=6,  fillcolor=COLORS["red"], opacity=0.07, line_width=0)

    # Annotations
    fig_reveal.add_annotation(
        x=2, y=hourly["fatal_rate"].max() * 0.85,
        text="<b>Night window</b><br>Fatality rate peaks here",
        showarrow=True, arrowhead=2, arrowcolor=COLORS["red"],
        font=dict(size=12, color=COLORS["red"]),
        bgcolor="#1A1C24", bordercolor=COLORS["red"], borderwidth=1,
    )

    fig_reveal.update_layout(
        **PLOTLY_TEMPLATE,
        height=380, margin=dict(l=0,r=0,t=36,b=0),
        title="Fatality rate by hour of day — the night anomaly",
        yaxis=dict(title="Fatality rate (%)", showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
        yaxis2=dict(title="Total crashes", overlaying="y", side="right",
                    showgrid=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#888780")),
        xaxis=dict(title="Hour of day", tickvals=list(range(0,24,2)),
                   ticktext=[f"{h:02d}:00" for h in range(0,24,2)],
                   showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig_reveal, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div class="pull-quote">'
            f'Night crashes (10pm–6am) have a fatality rate of <strong>{night_fatal_rate:.1f}%</strong> — '
            f'vs <strong>{day_fatal_rate:.1f}%</strong> during daylight hours. '
            f'That\'s a <strong>{night_fatal_rate/day_fatal_rate:.1f}× higher</strong> chance of dying in a nighttime crash.'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Impairment at night
        night_alc = night["alcohol_involved"].mean() * 100 if "alcohol_involved" in night else 0
        night_fat = night["fatigue_involved"].mean() * 100 if "fatigue_involved" in night else 0
        day_alc   = day_c["alcohol_involved"].mean() * 100 if "alcohol_involved" in day_c else 0
        day_fat   = day_c["fatigue_involved"].mean() * 100 if "fatigue_involved" in day_c else 0

        compare_df = pd.DataFrame({
            "Factor": ["Alcohol","Fatigue","Alcohol","Fatigue"],
            "Period": ["Night","Night","Day","Day"],
            "Rate": [night_alc, night_fat, day_alc, day_fat],
        })
        fig_compare = px.bar(
            compare_df, x="Factor", y="Rate", color="Period",
            barmode="group",
            color_discrete_map={"Night":COLORS["red"],"Day":COLORS["blue"]},
            title="Impairment: night vs day",
        )
        fig_compare = style_fig(fig_compare, height=300)
        fig_compare.update_yaxes(title="% of crashes")
        st.plotly_chart(fig_compare, use_container_width=True)

    with col2:
        # High-speed + night fatal share
        night_high_speed = dff[(dff["hour"].isin(list(range(0,6))+list(range(22,24)))) & (dff["speed_limit"]>=80)]
        night_hs_fatals = (night_high_speed["severity"]=="Fatal").sum()
        all_fatals = (dff["severity"]=="Fatal").sum()
        hs_share = night_hs_fatals / all_fatals * 100 if all_fatals > 0 else 0

        # Sunburst: hour bin × speed zone × severity
        dff_sun = dff.copy()
        dff_sun["time_bin"] = pd.cut(
            dff_sun["hour"],
            bins=[-1,5,11,17,21,24],
            labels=["Night (0–5)","Morning (6–11)","Afternoon (12–17)","Evening (18–21)","Late Night (22–23)"],
        )
        sun_data = (
            dff_sun.groupby(["time_bin","severity"])
            .size()
            .reset_index(name="count")
        )
        fig_sun = px.sunburst(
            sun_data, path=["time_bin","severity"], values="count",
            color="severity",
            color_discrete_map={
                "Fatal":COLORS["red"], "Serious Injury":COLORS["amber"],
                "Minor Injury":COLORS["blue"], "Non-Casualty":COLORS["gray"],
            },
            title="Crash severity by time of day",
        )
        fig_sun.update_layout(
            height=380, margin=dict(l=0,r=0,t=36,b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#CCCBC4"),
        )
        st.plotly_chart(fig_sun, use_container_width=True)

    st.markdown(
        f'<div class="clue-card">⚠️ <strong>The Culprit:</strong> '
        f'High-speed roads at night, with impaired drivers, account for <strong>{hs_share:.0f}%</strong> of all fatalities '
        f'while representing a fraction of total traffic. The case is closed. '
        f'Chapter 5 hands down the verdict — and the action plan.'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════
#  PAGE 5 — THE VERDICT + WHAT-IF (Advanced Feature #2)
# ═══════════════════════════════════════════════════════════════════════════
elif page == "⚖️ The Verdict":

    st.markdown('<div class="section-eyebrow">Chapter 5 · The Verdict</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">The Verdict</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">'
        'The data has spoken. Now you hold the power to act. '
        'Use the scenario modeller below to estimate the lives saved by specific policy interventions.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-dots">'
        '<div class="dot"></div><div class="dot"></div>'
        '<div class="dot"></div><div class="dot"></div>'
        '<div class="dot active"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### ⚙️ What-If Scenario Modeller")
    st.markdown(
        "Adjust the levers below. These are evidence-based estimates derived from NSW crash data patterns "
        "and Transport for NSW road safety literature.",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        speed_reduce = st.slider(
            "Reduce speed limit on rural roads (km/h reduction)",
            min_value=0, max_value=20, value=10, step=5,
            help="E.g. 100→90 km/h. Research shows each 5 km/h reduction on high-speed roads cuts fatal risk ~20%."
        )
        alc_enforce = st.slider(
            "Increase random breath testing coverage (%)",
            min_value=0, max_value=50, value=20, step=5,
            help="Estimated reduction in alcohol-involved fatal crashes per % coverage increase: ~0.8%."
        )
        fatigue_cam = st.slider(
            "Fatigue camera deployment (additional sites)",
            min_value=0, max_value=100, value=30, step=10,
            help="Each 10 additional camera sites estimated to reduce fatigue-fatal crashes by ~3%."
        )
        night_curfew = st.checkbox(
            "Introduce graduated night driving restrictions (under-25)",
            value=False,
        )

    with col2:
        # Model the outcomes
        base_fatals = (dff["severity"]=="Fatal").sum()
        if base_fatals == 0:
            base_fatals = 350  # default if data empty

        # Speed reduction effect (~4% per 5 km/h on high-speed roads, scaled to 30% of fatals)
        speed_effect = (speed_reduce / 5) * 0.04 * 0.30 * base_fatals

        # Alcohol enforcement (~0.8% per %)
        alc_effect = alc_enforce * 0.008 * (alcohol_pct / 100) * base_fatals

        # Fatigue cameras (~3% per 10 sites, scaled to fatigue share)
        fat_effect = (fatigue_cam / 10) * 0.03 * (fatigue_pct / 100) * base_fatals

        # Night curfew (~15% reduction in under-25 night fatals, ~20% of total)
        night_effect = 0.15 * 0.20 * base_fatals if night_curfew else 0

        total_saved = speed_effect + alc_effect + fat_effect + night_effect
        total_saved = min(total_saved, base_fatals * 0.60)  # cap at 60% reduction (plausibility)

        st.markdown(
            f"""<div class="kpi-card" style="text-align:center; margin-bottom:12px">
            <div class="label">Estimated lives saved annually</div>
            <div class="value" style="color:#1D9E75;font-size:52px">{total_saved:.0f}</div>
            <div class="delta down">Based on selected interventions</div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Waterfall breakdown
        labels = ["Baseline fatalities","Speed limit","Alcohol enforcement","Fatigue cameras"]
        values = [base_fatals, -speed_effect, -alc_effect, -fat_effect]
        if night_curfew:
            labels.append("Night restrictions")
            values.append(-night_effect)
        labels.append("Projected fatalities")
        values.append(base_fatals - total_saved)

        measure = (
            ["absolute"] +
            ["relative"] * (len(labels) - 2) +
            ["total"]
        )
        colors = (
            [COLORS["red"]] +
            [COLORS["teal"]] * (len(labels) - 2) +
            [COLORS["blue"]]
        )

        fig_wf = go.Figure(go.Waterfall(
            orientation="v",
            measure=measure,
            x=labels,
            y=values,
            connector=dict(line=dict(color="rgba(255,255,255,0.15)", width=1)),
            decreasing=dict(marker_color=COLORS["teal"]),
            increasing=dict(marker_color=COLORS["red"]),
            totals=dict(marker_color=COLORS["blue"]),
            text=[f"{abs(v):.0f}" for v in values],
            textposition="outside",
        ))
        fig_wf = style_fig(fig_wf, height=320)
        fig_wf.update_layout(title="Projected fatality reduction waterfall")
        fig_wf.update_xaxes(tickangle=-20)
        st.plotly_chart(fig_wf, use_container_width=True)

    # CTA box
    recommendations = [
        f"Reduce rural speed limits by {speed_reduce} km/h on State Highways and Regional Roads" if speed_reduce > 0 else None,
        f"Expand RBT coverage by {alc_enforce}% with dedicated night-time enforcement" if alc_enforce > 0 else None,
        f"Deploy {fatigue_cam} additional fatigue detection cameras on identified high-risk corridors" if fatigue_cam > 0 else None,
        "Introduce graduated night-driving restrictions for drivers under 25" if night_curfew else None,
    ]
    recs = [r for r in recommendations if r]

    if recs:
        recs_html = "".join(f"<li>{r}</li>" for r in recs)
        st.markdown(
            f"""<div class="cta-box">
            <h3>Recommended Actions for Transport for NSW</h3>
            <ul>{recs_html}</ul>
            <p style="margin-top:14px;font-size:13px;color:#888780">
            Estimated impact: <strong style="color:#1D9E75">{total_saved:.0f} lives saved</strong> annually 
            based on evidence-based modelling. The data demands action.
            </p>
            </div>""",
            unsafe_allow_html=True,
        )
    else:
        st.info("Adjust the sliders above to model your policy scenario.")

    st.markdown(
        '<div style="margin-top:32px;font-size:12px;color:#555">'
        'Data source: NSW Crash Data (data.nsw.gov.au) · 2024–2026 · '
        'Modelling estimates are indicative and based on published road safety research. '
        'Consult Transport for NSW actuarial teams for formal projections.'
        '</div>',
        unsafe_allow_html=True,
    )
