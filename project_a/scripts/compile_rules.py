import json, os, time, sys
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
ROOT = Path(__file__).resolve().parent.parent

SYSTEM = """Convert the tax provisions into a JSON configuration. Output ONLY JSON with exactly this shape.
Use the provisions only; do not add numbers that are not in the text.
{
 "financial_year": "...",
 "rounding_unit": n,
 "cess_rate_percent": n,
 "regimes": {
  "new": {
   "standard_deduction": n,
   "slabs": {"default": [{"from": n, "to": n or null, "rate": percent}]},
   "rebate": {"income_limit": n, "max_rebate": n, "marginal_relief": true/false},
   "surcharge_tiers": [{"above": n, "rate": percent}],
   "clauses": {"<element name>": "<clause text>"}
  },
  "old": {
   "standard_deduction": n,
   "slabs": {"default": [...], "senior": [...], "super_senior": [...]},
   "rebate": {...}, "surcharge_tiers": [...],
   "deductions": {
     "section_80c_max": n, "section_80ccd_1b_max": n,
     "section_80d_self_max": n, "section_80d_self_senior_max": n,
     "section_80d_parents_max": n, "section_80d_parents_senior_max": n,
     "home_loan_interest_max": n,
     "hra": {"metro_percent": n, "non_metro_percent": n, "rent_minus_percent_of_basic": n}
   },
   "clauses": {"<element name>": "<clause text>"}
  }
 }
}"""


def main(fy="2024-25"):
    tag = fy.replace("-", "_")
    text = (ROOT / "data" / f"rule_text_{tag}.md").read_text(encoding="utf-8")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    t0 = time.time()
    resp = client.models.generate_content(
        model=MODEL, contents=text,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM, response_mime_type="application/json", temperature=0))
    out = json.loads(resp.text)
    (ROOT / "data" / "compiled").mkdir(exist_ok=True)
    path = ROOT / "data" / "compiled" / f"raw_{tag}.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {path.name} in {time.time()-t0:.1f}s, "
          f"tokens in/out {resp.usage_metadata.prompt_token_count}/"
          f"{resp.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2024-25")