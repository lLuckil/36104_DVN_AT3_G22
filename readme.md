# NSW Road Safety Dashboard

This dashboard explores NSW road crashes from 2024 onward and is designed as a crash-first visual story rather than a generic reporting screen. It combines the NSW crash dataset with ABS 2024 LGA population estimates so the dashboard can compare raw crash counts with population-adjusted burden.

## What it shows

- overview KPIs for crashes, deaths, serious injuries, and casualties
- monthly and weekday crash patterns
- severity mix and time-of-day patterns
- crash hotspots by LGA and town
- crash, casualty, and fatality rates per 100,000 residents by LGA
- weather, lighting, speed-limit, and crash-movement factor views
- data-quality reporting for sparse or conditionally populated source fields

## Enrichment

The dashboard joins official ABS local government area population data to the crash dataset. This supports stronger questions such as:

- which LGAs have the highest raw crash counts
- which LGAs have the highest crash rate per 100,000 residents
- where fatal or casualty burden is disproportionately high relative to population

## Project files

- `app.py`: Streamlit app and chart layout
- `dashboard_data.py`: data loading, cleaning, enrichment, and derived metrics
- `data/nsw_crash_data.xlsx`: crash source workbook
- `data/abs_population_lga_2024.csv`: ABS population enrichment file
- `requirements.txt`: Python dependencies

## Run locally

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the dashboard:

```powershell
python -m streamlit run app.py
```

## Notes

- the dashboard keeps sparse crash-factor columns instead of dropping them outright
- blank values in those fields are treated as `Not recorded / Not applicable`
- the current population join matches all filtered crash LGAs except `Lord Howe Island`
