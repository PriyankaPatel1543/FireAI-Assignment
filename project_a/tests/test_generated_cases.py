import json
import pytest
from pathlib import Path
from src.regime_comparison import compare

CASES = []
for f in ("cases.json", "cases_2025_26.json"):
    p = Path(__file__).parent / f
    if p.exists():
        CASES += json.loads(p.read_text())


@pytest.mark.parametrize("c", CASES, ids=[c["id"] for c in CASES])
def test_generated(c):
    r = compare(c["input"], fy=c["fy"])
    assert r["old"]["total_tax"] == c["expected_old"]
    assert r["new"]["total_tax"] == c["expected_new"]