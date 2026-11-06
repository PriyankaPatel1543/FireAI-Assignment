import json, os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
ROOT = Path(__file__).resolve().parent.parent
_client = None

SYSTEM = """You are an Indian income tax assistant.
Use ONLY the provided tax provisions. Do not assume missing information.
Calculate tax under BOTH old and new regimes for the given inputs.
Follow the steps in order: gross salary, deductions, taxable income, slab tax,
rebate, surcharge, cess, final tax. Apply the rounding rules in the provisions.
Return ONLY JSON of this shape:
{"old": {"gross_salary": n, "deductions": [{"name": s, "amount": n, "clause": s}],
         "taxable_income": n, "slab_tax": n, "rebate": n, "surcharge": n,
         "cess": n, "total_tax": n, "clauses_used": [s]},
 "new": {... same keys ...}}"""


def llm_compare(inputs, fy="2024-25"):
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    rules = (ROOT / "data" / f"rule_text_{fy.replace('-', '_')}.md").read_text(encoding="utf-8")
    prompt = f"TAX PROVISIONS:\n{rules}\n\nINPUTS (annual rupees):\n{json.dumps(inputs)}"
    resp = _client.models.generate_content(
        model=MODEL, contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            response_mime_type="application/json",
            temperature=0))
    out = json.loads(resp.text)
    out["tokens_in"] = resp.usage_metadata.prompt_token_count
    out["tokens_out"] = resp.usage_metadata.candidates_token_count
    return out