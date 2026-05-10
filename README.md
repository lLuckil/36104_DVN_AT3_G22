# The Detective — NSW Crash Data Narrative

> **A persuasive data narrative for Transport for NSW decision-makers**
> Built for the Data Narratives Studio group assignment (Part 2 & 3)

---

## 🔍 Narrative Arc: The Detective

| Chapter | Page | Focus |
|---------|------|-------|
| 1 | The Crime Scene | Crash density map + KPI overview across NSW |
| 2 | The Suspects | Time patterns, speed zones, road type breakdown |
| 3 | The Evidence | Alcohol, fatigue, weather as contributing factors |
| 4 | The Reveal | The "aha" anomaly — night × speed × impairment |
| 5 | The Verdict | What-if policy modeller + call to action |

---

## 🚀 Running the app

```bash
# 1. Clone / navigate to this folder
cd nsw_crash_detective

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your data
mkdir -p data
# Place your NSW crash CSV here: data/nsw_crashes.csv
# Download from: https://data.nsw.gov.au/data/dataset/2-nsw-crash-data

# 4. Run
streamlit run app.py
```

The app runs on synthetic data by default — replace `data/nsw_crashes.csv` with the real dataset.

---

## 📊 Data Dictionary

| Column | Type | Description | Source |
|--------|------|-------------|--------|
| `crash_date` | date | Date of crash (DD/MM/YYYY) | NSW Crash Data |
| `crash_time` | time | Time of crash (HH:MM) | NSW Crash Data |
| `year` | int | Derived from crash_date | Derived |
| `month` | int | Derived from crash_date (1–12) | Derived |
| `hour` | int | Hour of crash (0–23) | Derived |
| `day_of_week` | str | Day name (Monday–Sunday) | Derived |
| `severity` | str | Fatal / Serious Injury / Minor Injury / Non-Casualty | NSW Crash Data |
| `lga_name` | str | Local Government Area name | NSW Crash Data |
| `road_type` | str | State Highway / Regional Road / Local Road / Motorway / Unnamed Road | NSW Crash Data |
| `speed_limit` | int | Posted speed limit at crash location (km/h) | NSW Crash Data |
| `contributing_factor` | str | Primary contributing factor recorded by police | NSW Crash Data |
| `weather_condition` | str | Weather at time of crash | NSW Crash Data |
| `alcohol_involved` | bool | Whether alcohol was a recorded factor | NSW Crash Data |
| `fatigue_involved` | bool | Whether fatigue was a recorded factor | NSW Crash Data |
| `latitude` | float | Crash location latitude (WGS84) | NSW Crash Data |
| `longitude` | float | Crash location longitude (WGS84) | NSW Crash Data |

---

## ⚙️ Advanced Features (Assignment Requirement)

| Feature | Implementation | Location |
|---------|---------------|----------|
| **Context-aware filtering** | Sidebar LGA / year / severity filters update all charts and the dynamic narrative text on Page 3 | `app.py` — sidebar mask + `ev_df` on Page 3 |
| **What-if parameterisation** | Speed limit / RBT / fatigue camera sliders with evidence-based outcome modelling and waterfall chart | `app.py` — Page 5 |
| **Narrative scrollytelling** | 5-page detective arc with progress dots, clue cards, pull-quotes, and structured narrative flow | `app.py` — all pages |

---

## 🎨 Design System

- **Theme**: Dark (`config.toml`) — `#0F1117` background, `#1A1C24` surface
- **Accent palette**: Red (#E24B4A), Amber (#BA7517), Blue (#378ADD), Teal (#1D9E75), Purple (#7F77DD)
- **Typography**: Playfair Display (headings) + Inter (body)
- **Principles applied**: Pre-attentive colour encoding (red = fatal), Gestalt proximity (KPI tiles), cognitive load (one reveal per page)

---

## 👥 Credits

| Role | Name | Contribution |
|------|------|-------------|
| Architect | TBC | App structure, Streamlit deployment |
| Analyst | TBC | Data cleaning, statistical modelling |
| Artist | TBC | Design system, visual polish |
| Orator | TBC | Narrative script, presentation |

**Data source**: NSW Crash Data — Transport for NSW / Centre for Road Safety  
https://data.nsw.gov.au/data/dataset/2-nsw-crash-data  
Collected from 2024 onwards. Updated periodically by Transport for NSW.

**Tools**: Streamlit · Plotly · Pandas · NumPy  
**Repo**: GitHub (link TBC) · **Hosted**: Streamlit Cloud (link TBC)
