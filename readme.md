````md
# NSW Road Crash Risk Intelligence Dashboard  
### 36104 – Data Visualisation and Narratives (DVN) Assignment 3  
### Group 22

---

# Project Overview

This project was developed as part of the **Data Visualisation and Narratives Studio Assignment** at the University of Technology Sydney (UTS). The objective of the assignment is to transform complex, real-world data into an interactive and persuasive narrative system that goes beyond a traditional dashboard.

Our project focuses on analysing **NSW Road Crash Data (2020–2024)** to investigate crash hotspots, identify temporal and spatial risk patterns, and support evidence-based road safety interventions.

The dashboard is designed for the stakeholder persona:

> **Transport Safety Policy Advisor – NSW Government**

The system follows a **Detective Narrative Arc**, where users progressively uncover:
- where crashes concentrate,
- when risks increase,
- what crash outcomes dominate,
- and which areas should be prioritised for intervention.

---

# Narrative Objective

This dashboard is not designed as a passive reporting tool. Instead, it functions as a decision-support narrative system intended to:

- reveal hidden crash patterns,
- communicate urgency through visual storytelling,
- support policy prioritisation,
- and encourage targeted road safety action.

The narrative flow includes:
1. Crime Scene Overview  
2. Crash Trend Investigation  
3. Hotspot Detection  
4. Temporal Risk Analysis  
5. Severity Profiling  
6. Spatial Evidence Mapping  
7. What-if Intervention Simulation  
8. Final Policy Recommendations  

---

# Dataset

## Dataset Source
NSW Government Open Data Portal

## Dataset Used
**NSW Road Crash Data – 2020–2024 – CRASH**

## Dataset Link
https://data.nsw.gov.au/data/dataset/2-nsw-crash-data

## Key Dataset Characteristics
- Real-world government dataset
- Recent and policy-relevant
- Temporal variables
- Spatial variables
- Multi-dimensional crash indicators
- Suitable for interactive narrative analysis

---

# Dashboard Features

## Core Features
- Interactive filtering by:
  - year,
  - region/LGA,
  - crash severity

- Dynamic crash trend analysis
- Hotspot identification
- Temporal risk investigation
- Crash severity distribution
- Interactive spatial mapping
- Policy recommendation framework

---

# Advanced Features Implemented

The assignment required implementation of advanced narrative/dashboard techniques. The dashboard includes:

## 1. Context-Aware Filtering
Interactive filters dynamically update all visuals and narrative context.

## 2. Narrative Scrollytelling
The dashboard follows a structured investigative storyline using sequential sections and evidence-driven progression.

## 3. What-if Parameterisation
A simulation slider estimates potential crash reductions under hypothetical intervention scenarios.

---

# Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core development |
| Streamlit | Interactive dashboard framework |
| Pandas | Data processing |
| Plotly | Interactive visualisation |
| OpenPyXL | Excel dataset handling |
| GitHub | Collaboration and version control |

---

# Repository Structure

```text
36104_DVN_AT3_G22/
│
├── dashboards/
│   └── vignesh_dashboard/
│       ├── app.py
│       ├── requirements.txt
│       ├── screenshots/
│       └── README.md
│
├── datasets/
│
├── documentation/
│
└── final_dashboard/
````

---

# Running the Dashboard Locally

## Step 1 — Clone Repository

```bash
git clone <repository-url>
```

## Step 2 — Open Project Folder

```bash
cd 36104_DVN_AT3_G22
```

## Step 3 — Install Requirements

```bash
pip install -r requirements.txt
```

## Step 4 — Run Streamlit Dashboard

```bash
streamlit run app.py
```

---

# Design Principles Applied

The dashboard incorporates principles from:

* Gestalt visual organisation,
* visual hierarchy,
* pre-attentive attributes,
* cognitive load reduction,
* and stakeholder-centred storytelling.

The dark executive-style interface was intentionally selected to resemble modern intelligence and risk-monitoring systems used in professional environments.

---

# Intended Stakeholder Impact

The dashboard aims to help NSW transport policymakers:

* identify high-risk corridors,
* prioritise infrastructure reviews,
* understand crash timing patterns,
* support targeted enforcement planning,
* and improve evidence-based road safety intervention strategies.

---

# Contribution

## Contributor

**Vignesh Selvam**

## Contribution Areas

* Narrative architecture
* Streamlit dashboard development
* Data preprocessing
* Interactive filtering system
* Visual storytelling implementation
* Policy recommendation framework
* GitHub contribution workflow

---

# Academic Context

This project was developed for:

**36104 – Data Visualisation and Narratives**
University of Technology Sydney (UTS)

---

# Disclaimer

This dashboard is developed for academic and educational purposes only. The analyses and recommendations presented are exploratory and should not be interpreted as official NSW Government policy advice.

```
```
