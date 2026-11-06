from src.tax_calculator import (
    load_rules,
    calculate_slab_tax,
    apply_rebate_87a,
    calculate_surcharge,
    calculate_cess,
    round_to_10,
)
from src.deductions import (
    calculate_standard_deduction,
    calculate_chapter_via_deductions,
    calculate_hra_exemption,
    calculate_80d_deduction,
    calculate_home_loan_deduction,
)


def _calculate_regime(inp, regime, fy):
    rules = load_rules(fy)["regimes"][regime]
    salary = inp["annual_salary"]
    age = inp.get("age", 30)

    std = calculate_standard_deduction(salary, regime)

    if regime == "old":
        ch6a = calculate_chapter_via_deductions(
            "old",
            section_80c=inp.get("section_80c", 0),
            section_80ccd_1b=inp.get("section_80ccd_1b", 0),
        )["total"]

        if inp.get("rent_paid") and inp.get("hra_received"):
            if inp.get("basic_salary") is None or inp.get("is_metro") is None:
                raise ValueError("basic_salary and is_metro are required for HRA")
            hra = calculate_hra_exemption(
                inp["basic_salary"], inp["hra_received"],
                inp["rent_paid"], inp["is_metro"],
            )
        else:
            hra = 0

        d80 = calculate_80d_deduction(
            inp.get("health_premium_self", 0),
            inp.get("health_premium_parents", 0),
            inp.get("self_senior", age >= 60),
            inp.get("parents_senior", False),
        )
        home_loan = calculate_home_loan_deduction(inp.get("home_loan_interest", 0))
    else:
        ch6a = hra = d80 = home_loan = 0

    taxable_raw = max(0, salary - std - hra - ch6a - d80 - home_loan)
    taxable = round_to_10(taxable_raw)

    slab_tax = calculate_slab_tax(taxable, regime, age, fy)
    after_rebate = apply_rebate_87a(taxable, slab_tax, regime, fy)
    surcharge = calculate_surcharge(taxable, after_rebate, regime, age, fy)
    cess = calculate_cess(after_rebate + surcharge, fy)
    total = round_to_10(after_rebate + surcharge + cess)

    return {
        "gross_salary": salary,
        "standard_deduction": std,
        "hra_exemption": hra,
        "chapter_via_deductions": ch6a,
        "deduction_80d": d80,
        "home_loan_interest": home_loan,
        "taxable_income": taxable,
        "slab_tax": slab_tax,
        "rebate_87a": slab_tax - after_rebate,
        "surcharge": surcharge,
        "cess": cess,
        "total_tax": total,
        "clause": rules.get("clause"),
    }


def compare(inp, fy="2024-25"):
    if inp.get("annual_salary") is None:
        raise ValueError("annual_salary is required")

    old = _calculate_regime(inp, "old", fy)
    new = _calculate_regime(inp, "new", fy)

    if old["total_tax"] < new["total_tax"]:
        rec, saving = "old", new["total_tax"] - old["total_tax"]
    elif new["total_tax"] < old["total_tax"]:
        rec, saving = "new", old["total_tax"] - new["total_tax"]
    else:
        rec, saving = "either", 0

    return {"fy": fy, "old": old, "new": new, "recommended": rec, "savings": saving}