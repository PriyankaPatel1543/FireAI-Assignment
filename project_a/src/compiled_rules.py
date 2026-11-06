import json
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(fy="2024-25", variant="reviewed"):
    p = ROOT / "data" / "compiled" / f"{variant}_{fy.replace('-', '_')}.json"
    return json.loads(p.read_text(encoding="utf-8"))


def _round(x, unit):
    return int((F(x) / unit + F(1, 2)) // 1) * unit


def _slab_tax(t, slabs):
    tax = F(0)
    for s in slabs:
        if t <= s["from"]:
            break
        top = t if s["to"] is None else min(t, s["to"])
        tax += F(top - s["from"]) * F(s["rate"]) / 100
    return tax


def _age_group(age):
    return "super_senior" if age >= 80 else "senior" if age >= 60 else "default"


def compute_regime(cfg, regime, inp):
    r, unit = cfg["regimes"][regime], cfg["rounding_unit"]
    s, age = inp["annual_salary"], inp.get("age", 30)
    ded = F(0)
    if regime == "old":
        d = r["deductions"]
        ded += min(inp.get("section_80c", 0), d["section_80c_max"])
        ded += min(inp.get("section_80ccd_1b", 0), d["section_80ccd_1b_max"])
        if inp.get("rent_paid") and inp.get("hra_received"):
            h, b = d["hra"], inp["basic_salary"]
            pct = h["metro_percent"] if inp["is_metro"] else h["non_metro_percent"]
            ded += min(inp["hra_received"],
                       max(0, F(inp["rent_paid"]) - F(b) * h["rent_minus_percent_of_basic"] / 100),
                       F(b) * pct / 100)
        ss, ps = inp.get("self_senior", age >= 60), inp.get("parents_senior", False)
        ded += min(inp.get("health_premium_self", 0),
                   d["section_80d_self_senior_max"] if ss else d["section_80d_self_max"])
        ded += min(inp.get("health_premium_parents", 0),
                   d["section_80d_parents_senior_max"] if ps else d["section_80d_parents_max"])
        ded += min(inp.get("home_loan_interest", 0), d["home_loan_interest_max"])
    std = min(s, r["standard_deduction"])
    t = _round(max(0, s - std - ded), unit)

    slabs_by_age = r["slabs"]
    slabs = slabs_by_age.get(_age_group(age), slabs_by_age["default"])
    tax = _slab_tax(t, slabs)

    reb = r["rebate"]
    if t <= reb["income_limit"]:
        tax = max(F(0), tax - reb["max_rebate"])
    elif reb["marginal_relief"]:
        tax = min(tax, F(t - reb["income_limit"]))

    tiers, rate, prev, T = r["surcharge_tiers"], 0, 0, None
    for tier in tiers:
        if t > tier["above"]:
            prev, rate, T = rate, tier["rate"], tier["above"]
    total = tax
    if rate:
        total = tax * (100 + rate) / 100
        cap = _slab_tax(T, slabs) * (100 + prev) / 100 + (t - T)
        total = min(total, cap)

    total = total * (100 + cfg["cess_rate_percent"]) / 100
    return {"taxable_income": t, "total_tax": _round(total, unit)}


def compute(inp, fy="2024-25", variant="reviewed"):
    cfg = load(fy, variant)
    return {r: compute_regime(cfg, r, inp) for r in ("old", "new")}