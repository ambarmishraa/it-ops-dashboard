# IT Operations Dashboard

A small personal project that analyses IT incident data and shows it in a Streamlit dashboard:
incident volume over time, categories, average resolution time and SLA compliance per application and priority.

**Data:** all data is synthetic. It is randomly generated (seeded, reproducible) by `generate_data.py`
and does not come from any real company or system.

## What it does
- `generate_data.py` creates 3,000 incidents for 10 applications and loads them into a SQLite database (3 tables: `applications`, `incidents`, `sla`).
- `queries.py` holds the SQL (CTEs, joins, aggregations, date filters) and returns Pandas DataFrames.
- `app.py` is the Streamlit dashboard with date and platform filters, KPI tiles and charts.
- `tests/` has pytest tests for the queries and for reproducibility of the data.

## Run it
```bash
pip install -r requirements.txt
python generate_data.py      # creates data/itops.db
streamlit run app.py
pytest
```

## Stack
Python, SQL (SQLite), Pandas, NumPy, Streamlit, Altair, pytest.

## Limitations
Synthetic data only, one fixed SLA per priority, no live data connection.

## Ideas for next steps
Load real ticket exports (CSV), add trend alerts when SLA compliance drops, deploy on Streamlit Community Cloud.
