import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import generate_data
import queries


def _db(tmp_path):
    db = tmp_path / "t.db"
    generate_data.main(db)
    return db


def test_total_matches_by_category(tmp_path):
    db = _db(tmp_path)
    total = queries.run(queries.KPIS, db_path=db).iloc[0].total_incidents
    cat = queries.run(queries.BY_CATEGORY, db_path=db).incidents.sum()
    assert total == cat == 3000


def test_sla_percentage_is_valid(tmp_path):
    db = _db(tmp_path)
    pct = queries.run(queries.KPIS, db_path=db).iloc[0].sla_met_pct
    assert 0 <= pct <= 100


def test_date_filter_reduces_rows(tmp_path):
    db = _db(tmp_path)
    full = queries.run(queries.KPIS, db_path=db).iloc[0].total_incidents
    half = queries.run(queries.KPIS, start="2026-05-01", end="2026-11-01", db_path=db).iloc[0].total_incidents
    assert 0 < half < full


def test_data_is_reproducible():
    a = generate_data.build_frames()[1]
    b = generate_data.build_frames()[1]
    assert a.equals(b)
