from src.tax_calculator import calculate_slab_tax
from src.deductions import calculate_standard_deduction
from src.deductions import calculate_taxable_salary
from src.tax_calculator import round_to_10, apply_rebate_87a
import pytest


from src.deductions import (
    calculate_80c_deduction,
    calculate_80ccd_1b_deduction,
    calculate_chapter_via_deductions
)


def test_new_regime_zero_tax():
    assert calculate_slab_tax(300000, "new") == 0


def test_new_regime_5_percent_slab():
    assert calculate_slab_tax(500000, "new") == 10000


def test_new_regime_10_lakh():
    assert calculate_slab_tax(1000000, "new") == 50000


def test_old_regime_below_60():
    assert calculate_slab_tax(500000, "old", age=30) == 12500


def test_old_regime_senior_citizen():
    assert calculate_slab_tax(500000, "old", age=65) == 10000


def test_negative_income():
    with pytest.raises(ValueError):
        calculate_slab_tax(-1000, "new")


def test_old_regime_standard_deduction():
    assert calculate_standard_deduction(1000000, "old") == 50000


def test_new_regime_standard_deduction():
    assert calculate_standard_deduction(1000000, "new") == 75000


def test_old_regime_taxable_salary():
    assert calculate_taxable_salary(1000000, "old") == 950000


def test_new_regime_taxable_salary():
    assert calculate_taxable_salary(1000000, "new") == 925000


def test_salary_less_than_standard_deduction():
    assert calculate_taxable_salary(30000, "new") == 0


def test_80c_limit():
    assert calculate_80c_deduction(180000) == 150000


def test_80c_below_limit():
    assert calculate_80c_deduction(100000) == 100000


def test_80ccd_1b_limit():
    assert calculate_80ccd_1b_deduction(70000) == 50000


def test_80ccd_1b_below_limit():
    assert calculate_80ccd_1b_deduction(30000) == 30000


def test_old_regime_total_deductions():
    result = calculate_chapter_via_deductions(
        "old",
        section_80c=180000,
        section_80ccd_1b=40000
    )

    assert result["80C"] == 150000
    assert result["80CCD_1B"] == 40000
    assert result["total"] == 190000


def test_new_regime_deductions():
    result = calculate_chapter_via_deductions(
        "new",
        section_80c=150000,
        section_80ccd_1b=50000
    )

    assert result["total"] == 0

def test_round_to_10_half_up():
    assert round_to_10(1005) == 1010   # banker's rounding would give 1000
    assert round_to_10(1004) == 1000

def test_new_regime_rebate_zero_tax():
    assert apply_rebate_87a(700000, 20000, "new") == 0

def test_new_regime_marginal_relief():
    assert apply_rebate_87a(705000, 20500, "new") == 5000