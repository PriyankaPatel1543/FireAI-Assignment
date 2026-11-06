import json, sys, time
from pathlib import Path
from src.llm_calculator import llm_compare

ROOT = Path(__file__).resolve().parent.parent
CASES = json.loads((ROOT / "tests" / "cases.json").read_text(encoding="utf-8"))
CACHE = ROOT / "results" / "llm_cache.json"
OUT = ROOT / "results" / "llm_eval.json"
SLEEP, RETRIES = 4, 3
QUOTA = {"grid": 20, "boundary_new": 10, "boundary_old": 8, "surcharge": 14, "random": 8}


def subset():
    chosen = []
    for cat, n in QUOTA.items():
        items = [c for c in CASES if c["category"] == cat]
        step = max(1, len(items) // n)
        chosen += items[::step][:n]
    return chosen


def call(cache, key, case):
    if key in cache:
        return cache[key]
    for attempt in range(RETRIES):
        try:
            t0 = time.time()
            res = llm_compare(case["input"], case["fy"])
            res["latency_s"] = round(time.time() - t0, 2)
            break
        except Exception as e:
            print(f"{key} attempt {attempt+1} failed: {str(e)[:80]}")
            time.sleep(20 * (attempt + 1))
    else:
        res = {"error": "failed after retries"}
    cache[key] = res
    CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    time.sleep(SLEEP)
    return res


def total(res, regime):
    try:
        return res[regime]["total_tax"]
    except Exception:
        return None


def accuracy(cache):
    rows = []
    for c in subset():
        res = call(cache, c["id"] + "#0", c)
        for regime in ("old", "new"):
            got, exp = total(res, regime), c[f"expected_{regime}"]
            rows.append({"id": c["id"], "cat": c["category"], "regime": regime,
                         "expected": exp, "got": got,
                         "exact": got == exp,
                         "within10": got is not None and abs(got - exp) <= 10})
    n = len(rows)
    print(f"\nExact: {sum(r['exact'] for r in rows)}/{n}   "
          f"Within Rs10: {sum(r['within10'] for r in rows)}/{n}")
    for cat in QUOTA:
        sub = [r for r in rows if r["cat"] == cat]
        print(f"  {cat:13s} {sum(r['exact'] for r in sub)}/{len(sub)}")
    ok = [v for k, v in cache.items() if k.endswith("#0") and "error" not in v]
    if ok:
        print(f"Avg latency {sum(v['latency_s'] for v in ok)/len(ok):.2f}s | "
              f"tokens in/out per call {sum(v['tokens_in'] for v in ok)//len(ok)}/"
              f"{sum(v['tokens_out'] for v in ok)//len(ok)}")
    print("\nFailures:")
    for r in rows:
        if not r["exact"]:
            print(f"  {r['id']} {r['regime']}: expected {r['expected']}, got {r['got']}")
    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def determinism(cache, reps=10):
    picks = [c for c in subset() if c["category"] in ("boundary_new", "surcharge", "grid")][::6][:5]
    for c in picks:
        answers = [(total(call(cache, f"{c['id']}#{i}", c), "old"),
                    total(call(cache, f"{c['id']}#{i}", c), "new")) for i in range(reps)]
        print(f"{c['id']}: {len(set(answers))} distinct answer(s) in {reps} runs {set(answers)}")


if __name__ == "__main__":
    (ROOT / "results").mkdir(exist_ok=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    determinism(cache) if "--determinism" in sys.argv else accuracy(cache)