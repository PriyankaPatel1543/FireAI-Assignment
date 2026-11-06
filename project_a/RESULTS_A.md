# Project A: Results

Model used for all LLM work: gemini-3.1-flash-lite (free tier). Price used for cost: $0.25 / 1M input tokens, $1.50 / 1M output tokens (ai.google.dev pricing, read 6 Nov 2026).

## 1. Comparison table

| Metric | Hand-coded rules | LLM at query time | LLM-compiled rules |
|---|---|---|---|
| Accuracy vs independent reference, FY 2024-25 | 216/216 cases, both regimes | 46/120 exact (38%), 60-case subset | raw 431/432, reviewed 432/432 |
| Accuracy vs independent reference, FY 2025-26 | 221/221 cases, both regimes | [fill in from llm_cache_2025_26 run] | raw 442/442, reviewed 442/442 |
| Deterministic | 1 distinct result set in 10 runs over all 216 cases | 1 distinct answer in 10 runs on each of 5 cases (consistently wrong on at least 3 of them) | By construction: no LLM at run time. Not separately run 10 times |
| Latency per request | 2.33 ms (re-reads the rules JSON on every call) | 2.55 s average | 0.27 to 1.84 ms across runs (machine noise) |
| Cost per 1,000 requests | $0 | about $0.98 (1,429 in + 412 out tokens per call) | $0. One-off compile cost about $0.0024 (1,779 in + 1,271 out) |
| Clause traceability | One clause string per regime; not per rupee line | 60/60 responses listed clauses (self-reported, not verified against the text) | Config has a clauses block, but the executor does not print it |
| Rule update time (FY 2025-26) | [stopwatch time]; one new JSON file, no Python change | Rule text rewritten; [time] | Recompiled in 4.7 s; no review changes; executor untouched |

Parser (Task 3): 50/50 on the first run (27 complete, 10 incomplete, 13 contradictory). About 438 tokens and 6.9 s per call. One transient 503, retried.

## 2. What the LLM at query time got wrong

74 of 120 case-regime pairs were wrong. Taking the first step where the LLM's breakdown diverged from the engine: 69 (93%) were wrong at slab tax, 5 were wrong at taxable income. No case was off by 10 or less, so these are arithmetic errors, not rounding. Wrong answers carried no error or warning. Re-running the same input gave the same wrong answer every time.

## 3. Compiled rules: what review caught and missed

The FY 2024-25 compile copied "3,00,001 to 7,00,000" from the prose literally and made all 12 slab lower bounds off by one. My line-by-line review missed it. Test case random_030 exposed it because its total landed on a rounding boundary (raw 474,890 vs expected 474,900). The error changed tax by about Rs 0.5, so 431 of 432 outputs were still correct: a silent failure that a smaller test suite would not have caught. Fixed in the reviewed file only. For FY 2025-26 the rule text used "from X up to Y" wording and the compile had no such error. This was not a controlled test, because the wording and the law changed together.

## 4. FY 2025-26 change log

| Implementation | Time | What changed | What broke | Silent? |
|---|---|---|---|---|
| Hand-coded | [stopwatch] | New tax_rules_2025_26.json (slabs, 87A limit and amount). No engine code change | First test run failed loudly (FileNotFoundError) until the JSON existed | No |
| Test generator | [stopwatch] | Parametrised by year (new slab table, rebate, boundary edges) | Missing function bodies after a bad paste | No |
| LLM query-time | [stopwatch] | New rule_text_2025_26.md | [fill in] | Yes: wrong answers carry no error |
| LLM-compiled | 4.7 s compile + review | New config from new rule text | Nothing. Reviewed equals raw | No |

Silent failures found:
1. Calling compare() with the wrong or missing fy returns a plausible wrong answer with no error (a Rs 12.75 lakh salary gives Rs 0 tax under 2025-26 and a non-zero tax under 2024-25).
2. calculate_standard_deduction() still hardcodes Rs 50,000 and Rs 75,000 and takes no fy. It did not break only because those values did not change.
3. The LLM version gives confident wrong answers on most multi-slab cases.
4. FY 2025-26 figures were taken from secondary sources via search, not the Act itself. Metro cities and 80D limits were assumed unchanged and not verified.

## 5. Official calculator checks (incometax.gov.in, AY 2025-26)

I checked 3 cases fully (both regimes) on the salary-based calculator, plus salary-only probes at Rs 8,00,000 and Rs 8,00,003. I did not reach 30 checks, because of the time limit.

| id | my old | official old | my new | official new |
|---|---|---|---|---|
| surcharge_001 | 13,65,000 | 13,64,997 | 12,29,800 | 12,29,797 |
| surcharge_003 | 13,65,010 | 13,65,011 | 12,29,800 | 12,29,803 |
| boundary_new_011 | 1,24,800 | 1,24,797 | 52,000 | 51,999 |

Finding: the slabs, cess, surcharge and marginal relief agree with the official tool. The final rounding does not. My engine rounds taxable income and final tax to Rs 10 (Sec 288A/288B as I understood them). The salary-based calculator returns odd rupees and does not round taxable income. The second (net-income) calculator rounds tax to the nearest rupee, and the two official tools disagree with each other on at least one input (Rs 8,00,003: Rs 23,401 vs Rs 23,400). I could not pin down one rule, so my results are within Rs 3 of the official figure on the cases checked, but not rupee-exact. Two earlier rounding hypotheses of mine were disproved by these checks.

## 6. Limits

- The reference calculator and the engine share one author and one reading of the law. Only the few official checks are independent.
- Official checks cover 3 cases plus probes, not 30. The HRA path (grid_025) and random_030 were not confirmed on the official tool.
- The LLM was measured on a 60-case subset per year because of free-tier limits.
- Determinism of the LLM was tested on 5 cases at temperature 0.