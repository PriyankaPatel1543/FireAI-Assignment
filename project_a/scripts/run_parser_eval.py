import json, sys, time
from pathlib import Path

from src.input_parser import parse

ROOT = Path(__file__).resolve().parent.parent
CASES = json.loads((ROOT / "tests" / "parser_cases.json").read_text(encoding="utf-8"))
CACHE_FILE = ROOT / "results" / "parser_cache.json"
OUT_FILE = ROOT / "results" / "parser_eval.json"
SLEEP = 4          # seconds between live calls (free-tier rate limit)
RETRIES = 3


def kind(case):
    if case.get("expect_conflict"):
        return "contradictory"
    if case["expect_ready"]:
        return "complete"
    return "incomplete"


def check(case, res):
    """Return a list of problems; an empty list means the case passed."""
    problems = []
    if res["ready"] != case["expect_ready"]:
        problems.append(f"ready={res['ready']}, expected {case['expect_ready']}")
    for k, v in case.get("expect_inputs", {}).items():
        if res["inputs"].get(k) != v:
            problems.append(f"{k}={res['inputs'].get(k)}, expected {v}")
    if "expect_missing" in case:
        if set(res["missing_fields"]) != set(case["expect_missing"]):
            problems.append(f"missing={res['missing_fields']}, expected {case['expect_missing']}")
    if case.get("expect_conflict") and not res["conflicts"]:
        problems.append("conflict not detected")
    return problems


def main(refresh=False):
    (ROOT / "results").mkdir(exist_ok=True)
    cache = {}
    if CACHE_FILE.exists() and not refresh:
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    rows = []
    for c in CASES:
        live = c["id"] not in cache
        if live:
            for attempt in range(RETRIES):
                try:
                    t0 = time.time()
                    res = parse(c["text"])
                    res["latency_s"] = round(time.time() - t0, 2)
                    cache[c["id"]] = res
                    break
                except Exception as e:                      # 429, network, bad JSON...
                    print(f"{c['id']} attempt {attempt+1} failed: {str(e)[:80]}")
                    time.sleep(20 * (attempt + 1))
            else:
                cache[c["id"]] = {"error": "failed after retries"}
            CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")  # save after every call
            time.sleep(SLEEP)

        res = cache[c["id"]]
        if "error" in res:
            problems = ["API error"]
        else:
            problems = check(c, res)
        rows.append({"id": c["id"], "kind": kind(c), "text": c["text"],
                     "passed": not problems, "problems": problems})
        print(("PASS " if not problems else "FAIL ") + c["id"])

    # Summary
    print("\n=== Summary ===")
    total_pass = sum(r["passed"] for r in rows)
    print(f"Overall: {total_pass}/{len(rows)}")
    for k in ("complete", "incomplete", "contradictory"):
        sub = [r for r in rows if r["kind"] == k]
        print(f"{k:14s}: {sum(r['passed'] for r in sub)}/{len(sub)}")

    ok = [v for v in cache.values() if "error" not in v]
    if ok:
        print(f"Total tokens: {sum(v.get('tokens', 0) for v in ok)}  "
              f"Avg latency: {sum(v.get('latency_s', 0) for v in ok)/len(ok):.2f}s")

    print("\n=== Failures ===")
    for r in rows:
        if not r["passed"]:
            print(f"{r['id']} [{r['kind']}] {r['text']}")
            for p in r["problems"]:
                print("    -", p)

    OUT_FILE.write_text(json.dumps(rows, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(refresh="--refresh" in sys.argv)