"""SQL queries used by the dashboard. Kept in one place so they are easy to test."""
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).parent / "data" / "itops.db"

# Shared base: one row per resolved incident with its resolution time and SLA result
BASE = """
SELECT i.incident_id, i.app_id, a.name AS application, a.platform, a.team,
       i.priority, i.category, i.status, i.opened_at, i.resolved_at,
       s.sla_hours,
       (julianday(i.resolved_at) - julianday(i.opened_at)) * 24.0 AS resolution_hours
FROM incidents i
JOIN applications a ON a.app_id = i.app_id
JOIN sla s ON s.priority = i.priority
WHERE i.opened_at >= :start AND i.opened_at < :end
"""

KPIS = f"""
WITH base AS ({BASE})
SELECT COUNT(*)                                             AS total_incidents,
       SUM(status = 'Open')                                 AS open_incidents,
       ROUND(AVG(resolution_hours), 1)                      AS avg_resolution_hours,
       ROUND(100.0 * SUM(resolution_hours <= sla_hours)
             / NULLIF(SUM(status = 'Resolved'), 0), 1)      AS sla_met_pct
FROM base
"""

MONTHLY = f"""
WITH base AS ({BASE})
SELECT strftime('%Y-%m', opened_at) AS month, COUNT(*) AS incidents
FROM base GROUP BY month ORDER BY month
"""

BY_APPLICATION = f"""
WITH base AS ({BASE})
SELECT application, platform, COUNT(*) AS incidents,
       ROUND(AVG(resolution_hours), 1) AS avg_resolution_hours,
       ROUND(100.0 * SUM(resolution_hours <= sla_hours)
             / NULLIF(SUM(status = 'Resolved'), 0), 1) AS sla_met_pct
FROM base GROUP BY application, platform ORDER BY incidents DESC
"""

BY_CATEGORY = f"""
WITH base AS ({BASE})
SELECT category, COUNT(*) AS incidents FROM base GROUP BY category ORDER BY incidents DESC
"""

BY_PRIORITY = f"""
WITH base AS ({BASE})
SELECT priority, COUNT(*) AS incidents,
       ROUND(AVG(resolution_hours), 1) AS avg_resolution_hours,
       MAX(sla_hours) AS sla_hours,
       ROUND(100.0 * SUM(resolution_hours <= sla_hours)
             / NULLIF(SUM(status = 'Resolved'), 0), 1) AS sla_met_pct
FROM base GROUP BY priority ORDER BY priority
"""


def run(query: str, start: str = "2000-01-01", end: str = "2100-01-01", db_path: Path = DB_PATH) -> pd.DataFrame:
    with sqlite3.connect(db_path) as con:
        return pd.read_sql_query(query, con, params={"start": start, "end": end})
