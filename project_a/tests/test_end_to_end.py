import pytest
from src.regime_comparison import compare

CASES = [
    # id, input, expected_old, expected_new
    ("12L_no_deductions", {"annual_salary": 1200000}, 163800, 71500),
    ("12L_80c_150k", {"annual_salary": 1200000, "section_80c": 150000}, 117000, 71500),
    ("7_75L_rebate_zero_new", {"annual_salary": 775000}, None, 0),
    ("7_80L_marginal_relief_new", {"annual_salary": 780000}, None, 5200),
    ("15L_full", {
    "annual_salary": 1500000, "basic_salary": 600000,
    "hra_received": 240000, "rent_paid": 180000, "is_metro": True,
    "section_80c": 150000, "health_premium_self": 25000,
}, 165360, 130000),
]

@pytest.mark.parametrize("cid,inp,exp_old,exp_new", CASES, ids=[c[0] for c in CASES])
def test_end_to_end(cid, inp, exp_old, exp_new):
    r = compare(inp)
    if exp_new is not None:
        assert r["new"]["total_tax"] == exp_new
    if exp_old is not None:
        assert r["old"]["total_tax"] == exp_old