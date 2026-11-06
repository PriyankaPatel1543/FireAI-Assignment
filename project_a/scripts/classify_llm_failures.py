import json
from collections import Counter
from pathlib import Path
from src.regime_comparison import compare

ROOT = Path(__file__).resolve().parent.parent
CASES = {c["id"]: c for c in json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))}
CACHE = json.loads((ROOT / "results" / "llm_cache.json").read_text(encoding="utf-8"))

# (LLM key, engine key), in calculation order
STEPS = [("taxable_income", "taxable_income"), ("slab_tax", "slab_tax"),
         ("rebate", "rebate_87a"), ("surcharge", "surcharge"), ("cess", "cess")]

tally, examples = Counter(), {}
for key, llm in CACHE.items():
    if not key.endswith("#0") or "error" in llm:
        continue
    c = CASES[key[:-2]]
    eng = compare(c["input"], c["fy"])
    for regime in ("old", "new"):
        l, e = llm.get(regime, {}), eng[regime]
        if l.get("total_tax") == c[f"expected_{regime}"]:
            continue
        cause = "total only (steps match)"
        for lk, ek in STEPS:
            lv, ev = l.get(lk), e[ek]
            if lv is None or abs(lv - ev) > 1:
                cause = f"first wrong step: {lk}"
                examples.setdefault(cause, f"{c['id']} {regime}: LLM {lv}, engine {ev}")
                break
        tally[(regime, cause)] += 1

for (regime, cause), n in sorted(tally.items()):
    print(f"{regime:4s} {cause:35s} {n}")
print()
for cause, ex in examples.items():
    print(f"{cause}: e.g. {ex}")