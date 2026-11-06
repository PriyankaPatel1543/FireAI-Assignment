import json, random, csv, sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FY = sys.argv[1] if len(sys.argv) > 1 else "2024-25"

NEW_TABLES = {
    "2024-25": [(0, 0, 0), (300000, 5, 0), (700000, 10, 20000),
                (1000000, 15, 50000), (1200000, 20, 80000), (1500000, 30, 140000)],
    "2025-26": [(0, 0, 0), (400000, 5, 0), (800000, 10, 20000), (1200000, 15, 60000),
                (1600000, 20, 120000), (2000000, 25, 200000), (2400000, 30, 300000)],
}
REBATE_NEW = {"2024-25": (700000, 25000), "2025-26": (1200000, 60000)}
NEW_EDGES = {"2024-25": [300000, 700000, 1000000, 1200000, 1500000],
             "2025-26": [400000, 800000, 1200000, 1600000, 2000000, 2400000]}
NEW = NEW_TABLES[FY]
OLD = {
    "default": [(0, 0, 0), (250000, 5, 0), (500000, 20, 12500), (1000000, 30, 112500)],
    "senior": [(0, 0, 0), (300000, 5, 0), (500000, 20, 10000), (1000000, 30, 110000)],
    "super": [(0, 0, 0), (500000, 20, 0), (1000000, 30, 100000)],
}


def r10(x):  # nearest 10, half-up (current rounding assumption, unchanged between years)
    return int((F(x) / 10 + F(1, 2)) // 1) * 10


def table(regime, age):
    if regime == "new":
        return NEW
    return OLD["super" if age >= 80 else "senior" if age >= 60 else "default"]


def slab(t, tb):
    lower, rate, base = [row for row in tb if row[0] <= t][-1]
    return base + F(t - lower) * rate / 100


def ref_regime(inp, regime):
    s = inp["annual_salary"]
    age = inp.get("age", 30)
    ded = 0
    if regime == "old":
        std = min(s, 50000)
        ded += min(inp.get("section_80c", 0), 150000)
        ded += min(inp.get("section_80ccd_1b", 0), 50000)
        if inp.get("rent_paid") and inp.get("hra_received"):
            b = inp["basic_salary"]
            pct = F(1, 2) if inp["is_metro"] else F(2, 5)
            ded += min(inp["hra_received"],
                       max(0, inp["rent_paid"] - F(b) / 10), b * pct)
        ss = inp.get("self_senior", age >= 60)
        ps = inp.get("parents_senior", False)
        ded += min(inp.get("health_premium_self", 0), 50000 if ss else 25000)
        ded += min(inp.get("health_premium_parents", 0), 50000 if ps else 25000)
        ded += min(inp.get("home_loan_interest", 0), 200000)
    else:
        std = min(s, 75000)

    t = r10(max(0, s - std - ded))
    tb = table(regime, age)
    tax = slab(t, tb)

    # Sec 87A
    if regime == "new":
        lim, mx = REBATE_NEW[FY]
        if t <= lim:
            tax = max(0, tax - mx)
        else:
            tax = min(tax, t - lim)
    elif t <= 500000:
        tax = max(0, tax - 12500)

    # Surcharge + marginal relief
    tiers = [(5_000_000, 10), (10_000_000, 15), (20_000_000, 25)]
    if regime == "old":
        tiers.append((50_000_000, 37))
    rate, prev, T = 0, 0, None
    for th, r in tiers:
        if t > th:
            prev, rate, T = rate, r, th
    total = tax
    if rate:
        total = tax * (100 + rate) / 100
        cap = slab(T, tb) * (100 + prev) / 100 + (t - T)
        total = min(total, cap)

    return r10(total * F(104, 100))


def ref_both(inp):
    return ref_regime(inp, "old"), ref_regime(inp, "new")


def build():
    cases, n = [], {}

    def add(cat, inp):
        n[cat] = n.get(cat, 0) + 1
        old, new = ref_both(inp)
        cases.append({"id": f"{cat}_{n[cat]:03d}", "fy": FY, "category": cat,
                      "input": inp, "expected_old": old, "expected_new": new,
                      "source": "independent_reference"})

    # 1. Grid: salary x deduction profile
    salaries = [300000, 500000, 600000, 800000, 1000000, 1200000, 1500000,
                2000000, 3000000, 5000000, 7500000, 10000000, 25000000]
    for i, s in enumerate(salaries):
        basic = s // 2
        profiles = [
            {},
            {"section_80c": 150000},
            {"section_80c": 150000, "section_80ccd_1b": 50000, "health_premium_self": 25000},
            {"basic_salary": basic, "hra_received": basic * 2 // 5,
             "rent_paid": s // 4, "is_metro": i % 2 == 0},
            {"home_loan_interest": 200000, "section_80c": 100000},
            {"age": 65, "health_premium_self": 50000, "health_premium_parents": 25000},
            {"age": 82, "section_80c": 150000, "health_premium_parents": 50000,
             "parents_senior": True},
        ]
        for p in profiles:
            add("grid", {"annual_salary": s, **p})

    # 2. Slab / rebate boundaries (taxable income = edge + offset, no deductions)
    offs = [-10, -1, 0, 1, 10]
    for edge in NEW_EDGES[FY]:
        for o in offs:
            add("boundary_new", {"annual_salary": edge + 75000 + o})
    for edge in [250000, 300000, 500000, 1000000]:
        for o in offs:
            add("boundary_old", {"annual_salary": edge + 50000 + o})

    # 3. Surcharge thresholds, both regimes
    for T in [5_000_000, 10_000_000, 20_000_000, 50_000_000]:
        for std in (50000, 75000):
            for o in [-10, 0, 10, 1000, 100000]:
                add("surcharge", {"annual_salary": T + std + o})

    # 4. Random realistic profiles
    random.seed(42)
    for _ in range(40):
        s = random.randrange(300000, 6000000, 1000)
        basic = random.randrange(s // 3, s // 2, 1000)
        inp = {"annual_salary": s, "age": random.choice([30, 35, 45, 62, 70, 82]),
               "section_80c": random.randrange(0, 200001, 10000),
               "section_80ccd_1b": random.choice([0, 25000, 50000, 70000]),
               "health_premium_self": random.randrange(0, 60001, 5000),
               "home_loan_interest": random.choice([0, 100000, 250000])}
        if random.random() < 0.6:
            inp.update({"basic_salary": basic, "hra_received": basic * 2 // 5,
                        "rent_paid": random.randrange(60000, 400000, 10000),
                        "is_metro": random.random() < 0.5})
        add("random", inp)
    return cases


if __name__ == "__main__":
    cases = build()
    out = "cases.json" if FY == "2024-25" else "cases_2025_26.json"
    (ROOT / "tests" / out).write_text(json.dumps(cases, indent=2))
    print(f"Wrote {len(cases)} cases to tests/{out}")

    # Verification list only for FY 2024-25, and never overwrite your filled-in copy
    csv_path = ROOT / "verification" / "to_verify.csv"
    if FY == "2024-25" and not csv_path.exists():
        pick = cases[:: max(1, len(cases) // 30)][:30]
        (ROOT / "verification").mkdir(exist_ok=True)
        with open(csv_path, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "input", "expected_old", "expected_new",
                        "official_old", "official_new"])
            for c in pick:
                w.writerow([c["id"], json.dumps(c["input"]),
                            c["expected_old"], c["expected_new"], "", ""])
        print(f"Wrote {len(pick)} cases to verification/to_verify.csv")