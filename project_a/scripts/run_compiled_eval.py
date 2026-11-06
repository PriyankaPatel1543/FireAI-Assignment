import json, sys, time, os
from pathlib import Path
from src.compiled_rules import compute

ROOT = Path(__file__).resolve().parent.parent
CASES_FILE = os.environ.get("CASES_FILE", "cases.json")
CASES = json.loads((ROOT / "tests" / CASES_FILE).read_text(encoding="utf-8"))
CACHE = ROOT / "results" / ("llm_cache.json" if CASES_FILE == "cases.json" else "llm_cache_2025_26.json")
variant = "raw" if "--raw" in sys.argv else "reviewed"

bad, t0 = [], time.time()
for c in CASES:
    r = compute(c["input"], c["fy"], variant)
    for regime in ("old", "new"):
        if r[regime]["total_tax"] != c[f"expected_{regime}"]:
            bad.append((c["id"], regime, c[f"expected_{regime}"], r[regime]["total_tax"]))
n = len(CASES) * 2
print(f"[{variant}] exact {n - len(bad)}/{n}  ({(time.time()-t0)/len(CASES)*1000:.2f} ms per case)")
for b in bad[:20]:
    print("  FAIL", b)