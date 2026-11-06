from src.tax_calculator import calculate_surcharge, calculate_slab_tax, calculate_cess


def test_no_surcharge_at_exactly_50_lakh():
    tax = calculate_slab_tax(5000000, "old")
    assert calculate_surcharge(5000000, tax, "old") == 0


def test_surcharge_marginal_relief_old_51_lakh():
    tax = calculate_slab_tax(5100000, "old")
    assert calculate_surcharge(5100000, tax, "old") == 70000


def test_cess_is_4_percent():
    assert calculate_cess(100000) == 4000