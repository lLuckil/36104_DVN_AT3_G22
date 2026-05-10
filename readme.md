# NSW Road Safety Analytics Hub

##  Project Overview

The NSW Road Safety Analytics Hub is an interactive data storytelling dashboard developed using Streamlit, Python, Pandas, and Plotly.

This project analyses New South Wales road crash data to identify crash hotspots, severity trends, temporal risk patterns, spatial crash concentration, and possible intervention outcomes. The dashboard transforms raw crash records into a human-centred analytical narrative that supports evidence-based road safety planning.

The project was designed as part of a Data Visualisation and Narrative assignment focused on transforming complex datasets into persuasive and actionable insights.

---

# 🎯 Project Objective

The primary goal of this dashboard is to:

- Analyse crash trends across NSW
- Identify high-risk LGAs (Local Government Areas)
- Investigate when crash risks are highest
- Understand crash severity composition
- Visualise spatial crash concentration
- Support safer and smarter transport policy decisions

The dashboard focuses not only on crash volume but also on the human and policy impact behind the data.

---

# 🗂️ Dataset Information

The dashboard uses NSW road crash data stored in the `/data` directory.

Expected dataset file:

```text
data/nsw_crash_data_clean.csv
```

---

# 📊 Key Variables Used

| Variable | Description |
|---|---|
| year_of_crash | Crash year |
| month_of_crash | Crash month |
| day_of_week_of_crash | Day of week |
| two-hour_intervals | Crash time interval |
| lga | Local Government Area |
| degree_of_crash | Crash severity |
| latitude | Crash latitude |
| longitude | Crash longitude |
| no._killed | Number of fatalities |
| no._seriously_injured | Serious injuries |
| no._moderately_injured | Moderate injuries |
| no._minor-other_injured | Minor injuries |

---

# ⚙️ Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- NumPy
- OpenPyXL

---

# 🧠 Dashboard Features

## 1. Interactive Filtering System

Users can dynamically filter crash data by:

- Crash year
- Region / LGA
- Crash severity

---

## 2. Road Safety Snapshot

The dashboard displays:

- Total crashes
- Fatal crashes
- Injury crashes
- Number of LGAs analysed

---

## 3. Crash Trend Analysis

The dashboard visualises yearly crash trends to identify whether crash frequency is increasing or decreasing over time.

---

## 4. High-Risk LGA Detection

Crash hotspot LGAs are identified using crash frequency comparisons.

---

## 5. Temporal Risk Analysis

The dashboard analyses:

- Crash distribution by day of week
- Crash distribution by time interval
- Monthly crash patterns

---

## 6. Crash Severity Composition

Severity outcomes are analysed across:

- Fatal crashes
- Injury crashes
- Non-casualty crashes

---

## 7. Human Impact Indicator

The dashboard highlights:

- Number killed
- Serious injuries
- Moderate injuries
- Minor injuries

---

## 8. Spatial Crash Mapping

Crash locations are visualised geographically using latitude and longitude coordinates.

---

## 9. What-if Intervention Simulator

The dashboard estimates possible crash reductions based on hypothetical intervention percentages.

---

# 📖 Narrative Structure

### What?
What crash patterns exist across NSW?

### So What?
Which crash risks require urgent policy attention?

### What Next?
What interventions should be prioritised?

---

# 🚨 Key Insights

- Some LGAs consistently experience higher crash volumes
- Crash risk changes significantly across time periods
- Severe crash outcomes require targeted policy action
- Spatial clustering supports hotspot-based intervention

---

# ✅ Recommended Actions

- Targeted enforcement
- Road safety audits
- Infrastructure redesign
- Public awareness campaigns
- Time-based traffic management

---

# ▶️ How to Run the Dashboard

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Run Streamlit Dashboard

```bash
streamlit run app.py
```

---

# 📁 Project Structure

```text
NSW Dashboard
│
├── app.py
├── requirements.txt
├── readme.md
│
└── data
    └── nsw_crash_data_clean.csv
```

---

# 👨‍💻 Developed By

Saumya Goswami

Master of Data Science and Innovation  
University of Technology Sydney (UTS)

---

