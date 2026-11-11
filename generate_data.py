"""Generate a synthetic IT incident dataset and load it into SQLite.

All data is randomly generated (seeded, so it is reproducible). It does not
come from any real company or system.
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DB_PATH = Path(__file__).parent / "data" / "itops.db"
SEED = 42

APPLICATIONS = [
    # name, platform, owning team
    ("ERP Core", "SAP", "Business Applications"),
    ("HR Portal", "Web", "Business Applications"),
    ("Data Warehouse", "Cloud", "Data Platform"),
    ("BI Reporting", "Cloud", "Data Platform"),
    ("Email & Collaboration", "SaaS", "Workplace IT"),
    ("VPN Gateway", "Network", "Network Services"),
    ("Office WiFi", "Network", "Network Services"),
    ("Identity & Access", "Cloud", "Security"),
    ("Supply Chain Tracker", "Web", "Business Applications"),
    ("Service Desk Tool", "SaaS", "Workplace IT"),
]
CATEGORIES = ["Outage", "Performance", "Access / Login", "Data Issue", "Configuration", "Request"]
PRIORITIES = ["P1", "P2", "P3", "P4"]
# Target resolution time (hours) per priority - used as the SLA in the dashboard
SLA_HOURS = {"P1": 4, "P2": 8, "P3": 24, "P4": 72}


def build_frames(n_incidents: int = 3000, seed: int = SEED):
    rng = np.random.default_rng(seed)

    apps = pd.DataFrame(APPLICATIONS, columns=["name", "platform", "team"])
    apps.insert(0, "app_id", range(1, len(apps) + 1))

    start = pd.Timestamp("2025-11-01")
    span_hours = 365 * 24
    opened = start + pd.to_timedelta(rng.integers(0, span_hours, n_incidents), unit="h")
    opened = opened + pd.to_timedelta(rng.integers(0, 60, n_incidents), unit="m")

    priority = rng.choice(PRIORITIES, n_incidents, p=[0.05, 0.20, 0.45, 0.30])
    category = rng.choice(CATEGORIES, n_incidents, p=[0.10, 0.20, 0.30, 0.15, 0.15, 0.10])
    app_id = rng.choice(apps["app_id"], n_incidents)

    # Resolution time: log-normal around a fraction of the SLA, so some breach it
    sla = np.array([SLA_HOURS[p] for p in priority], dtype=float)
    hours = rng.lognormal(mean=np.log(sla * 0.7), sigma=0.6)
    resolved = opened + pd.to_timedelta(hours, unit="h")

    # Incidents opened in the last 3 days may still be open
    cutoff = opened.max() - pd.Timedelta(days=3)
    still_open = (opened > cutoff) & (rng.random(n_incidents) < 0.5)

    incidents = pd.DataFrame(
        {
            "incident_id": range(1, n_incidents + 1),
            "app_id": app_id,
            "opened_at": opened,
            "resolved_at": resolved.where(~still_open, pd.NaT),
            "priority": priority,
            "category": category,
            "status": np.where(still_open, "Open", "Resolved"),
        }
    )
    sla_df = pd.DataFrame({"priority": list(SLA_HOURS), "sla_hours": list(SLA_HOURS.values())})
    return apps, incidents, sla_df


def main(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    apps, incidents, sla = build_frames()
    with sqlite3.connect(db_path) as con:
        apps.to_sql("applications", con, if_exists="replace", index=False)
        sla.to_sql("sla", con, if_exists="replace", index=False)
        inc = incidents.copy()
        for col in ("opened_at", "resolved_at"):
            inc[col] = inc[col].dt.strftime("%Y-%m-%d %H:%M:%S")
        inc.to_sql("incidents", con, if_exists="replace", index=False)
    print(f"Wrote {len(incidents)} incidents and {len(apps)} applications to {db_path}")


if __name__ == "__main__":
    main()
