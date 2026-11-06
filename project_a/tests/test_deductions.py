from src.deductions import (
    calculate_hra_exemption,
    calculate_80d_deduction,
    calculate_home_loan_deduction,
)


def test_hra_rent_minus_10pct_is_lowest():
    # basic 6L, HRA 2.4L, rent 1.8L, metro -> min(240000, 120000, 300000)
    assert calculate_hra_exemption(600000, 240000, 180000, True) == 120000


def test_hra_received_is_lowest():
    # min(50000, 120000, 300000)
    assert calculate_hra_exemption(600000, 50000, 180000, True) == 50000


def test_hra_non_metro_40pct_is_lowest():
    # min(300000, 360000 - 60000 = 300000, 40% of 600000 = 240000)
    assert calculate_hra_exemption(600000, 300000, 360000, False) == 240000


def test_hra_zero_when_rent_below_10pct_basic():
    # rent 50000 - 60000 -> negative, floored at 0
    assert calculate_hra_exemption(600000, 240000, 50000, True) == 0


def test_80d_self_and_senior_parents():
    # self min(30000, 25000) = 25000, parents min(60000, 50000) = 50000
    assert calculate_80d_deduction(30000, 60000, False, True) == 75000


def test_80d_caps_at_100000_for_both_senior():
    assert calculate_80d_deduction(80000, 80000, True, True) == 100000


def test_home_loan_cap():
    assert calculate_home_loan_deduction(250000) == 200000