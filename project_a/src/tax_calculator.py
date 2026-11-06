import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def load_rules(fy="2024-25"):
    with open(DATA_DIR / f"tax_rules_{fy.replace('-', '_')}.json") as f:
        return json.load(f)

def _age_group(age):
    if age >= 80: return "super_senior"
    if age >= 60: return "senior"
    return "default"

def calculate_slab_tax(taxable_income, regime, age=30, fy="2024-25"):
    if taxable_income < 0:
        raise ValueError("Taxable income cannot be negative")
    if regime not in ("old", "new"):
        raise ValueError("Regime must be 'old' or 'new'")

    slabs_by_age = load_rules(fy)["regimes"][regime]["slabs"]
    slabs = slabs_by_age.get(_age_group(age), slabs_by_age["default"])

    tax = 0
    for s in slabs:
        if taxable_income <= s["from"]:
            break
        top = taxable_income if s["to"] is None else min(taxable_income, s["to"])
        tax += (top - s["from"]) * s["rate"] / 100
    return tax

from decimal import Decimal, ROUND_HALF_UP

def round_to_10(x):
    return int((Decimal(str(x)) / 10).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 10)

def apply_rebate_87a(taxable_income, tax, regime, fy="2024-25"):
    r = load_rules(fy)["regimes"][regime]["rebate_87a"]
    if taxable_income <= r["income_limit"]:
        return max(0, tax - r["max_rebate"])
    if r["marginal_relief"]:  # tax can't exceed income above the limit
        return min(tax, taxable_income - r["income_limit"])
    return tax

def calculate_surcharge(taxable_income, tax, regime, age=30, fy="2024-25"):
    tiers = load_rules(fy)["regimes"][regime]["surcharge"]

    applicable = None
    prev_rate = 0
    for t in tiers:
        if taxable_income > t["above"]:
            applicable = t
        else:
            break
    if applicable is None:
        return 0

    idx = tiers.index(applicable)
    prev_rate = tiers[idx - 1]["rate"] if idx > 0 else 0

    surcharge = tax * applicable["rate"] / 100

    # Marginal relief: tax + surcharge cannot exceed
    # (tax + surcharge at the threshold) + income above the threshold
    threshold = applicable["above"]
    tax_at_threshold = calculate_slab_tax(threshold, regime, age, fy)
    max_total = tax_at_threshold * (1 + prev_rate / 100) + (taxable_income - threshold)

    if tax + surcharge > max_total:
        surcharge = max(0, max_total - tax)
    return surcharge

def calculate_cess(tax_plus_surcharge, fy="2024-25"):
    rate = load_rules(fy)["cess_rate"]
    return tax_plus_surcharge * rate / 100