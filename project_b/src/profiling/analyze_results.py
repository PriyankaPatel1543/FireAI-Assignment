
import pandas as pd
import json

# 1. Read missing value report
missing = pd.read_csv(
    "data/processed/missing_values.csv"
)

print("\n========== MISSING VALUES ==========")

missing = missing.sort_values(
    by="Missing_Count",
    ascending=False
)

print(missing.to_string(index=False))


# 2. Read profiling summary
with open(
    "data/processed/profiling_results.json",
    "r"
) as file:
    results = json.load(file)

print("\n========== PROFILING SUMMARY ==========")

for key, value in results.items():
    print(f"{key}: {value}")


# 3. Read issue examples
with open(
    "data/processed/issue_examples.json",
    "r"
) as file:
    examples = json.load(file)

print("\n========== ISSUE EXAMPLES ==========")

if examples:
    for example in examples:
        print(example)
else:
    print("No examples found for the checked issues.")
