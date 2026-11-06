import json, os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
METRO = {"delhi", "mumbai", "kolkata", "chennai"}

PROMPT = """You extract tax-related facts from a user's message (English, Hindi or Hinglish).
Return ONLY JSON with these keys. Use null for anything NOT stated. NEVER guess or infer.
All money values in rupees as plain numbers (12 lakh = 1200000, 15k = 15000).

salary_annual, salary_monthly, basic_salary_annual, hra_received_annual,
rent_monthly, rent_annual, city (string as stated), section_80c, section_80ccd_1b,
health_premium_self, health_premium_parents, home_loan_interest,
age, parents_age,
conflicts: list of strings describing any contradictory values the user gave
(e.g. two different salaries). Leave [] if none.
pays_rent: true if the user says they pay rent or live in rented housing (even with no amount), false if they say they own or pay no rent, null if not mentioned.

If a value is stated as monthly, put it in the *_monthly key, not the annual one.
"""

_client = None


def _llm_extract(text):
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = _client.models.generate_content(
        model=MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction=PROMPT,
            response_mime_type="application/json",
            temperature=0,
        ),
    )
    return json.loads(resp.text), resp.usage_metadata


def normalize(raw):
    """Pure Python: turn raw extraction into compare() inputs + missing list."""
    missing, assumptions, inp = [], [], {}

    sal = raw.get("salary_annual")
    if sal is None and raw.get("salary_monthly") is not None:
        sal = raw["salary_monthly"] * 12
    if sal is None:
        missing.append("annual_salary")
    else:
        inp["annual_salary"] = sal

    rent = raw.get("rent_annual")
    if rent is None and raw.get("rent_monthly") is not None:
        rent = raw["rent_monthly"] * 12

    if rent or raw.get("pays_rent"):
        if rent:
            inp["rent_paid"] = rent
        else:
            missing.append("rent_amount")
        for key, src in [("basic_salary", "basic_salary_annual"),
                         ("hra_received", "hra_received_annual")]:
            if raw.get(src) is None:
                missing.append(key)
            else:
                inp[key] = raw[src]
        city = (raw.get("city") or "").strip().lower()
        if not city:
            missing.append("city")
        else:
            inp["is_metro"] = city in METRO

    if raw.get("health_premium_parents") and raw.get("parents_age") is None:
        missing.append("parents_age")

    for src, dst in [("section_80c", "section_80c"),
                     ("section_80ccd_1b", "section_80ccd_1b"),
                     ("health_premium_self", "health_premium_self"),
                     ("health_premium_parents", "health_premium_parents"),
                     ("home_loan_interest", "home_loan_interest"),
                     ("age", "age")]:
        if raw.get(src) is not None:
            inp[dst] = raw[src]
        elif dst != "age":
            assumptions.append(f"{dst} not mentioned, treated as 0")

    if raw.get("parents_age") is not None:
        inp["parents_senior"] = raw["parents_age"] >= 60

    return inp, missing, assumptions


QUESTIONS = {
    "annual_salary": "What is your annual salary (or monthly salary)?",
    "rent_amount": "How much rent do you pay (monthly or yearly)?",
    "basic_salary": "What is your basic salary (plus DA) per year? HRA depends on it.",
    "hra_received": "How much HRA does your employer pay you per year?",
    "city": "Which city do you live in? (Metro or non-metro changes the HRA limit.)",
    "parents_age": "Are your parents 60 or older? It changes the health-insurance limit.",
}


def parse(text):
    raw, usage = _llm_extract(text)
    conflicts = raw.get("conflicts") or []
    inp, missing, assumptions = normalize(raw)

    if conflicts:
        question = "I found conflicting details: " + "; ".join(conflicts) + ". Which is correct?"
    elif missing:
        question = QUESTIONS[missing[0]]
    else:
        question = None

    return {"inputs": inp, "missing_fields": missing, "conflicts": conflicts,
            "assumptions": assumptions, "clarifying_question": question,
            "ready": question is None, "tokens": usage.total_token_count}