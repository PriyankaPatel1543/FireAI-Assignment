import pandas as pd
from pathlib import Path

CORRUPTED_DIR = Path(
    "data/corrupted"
)

results = []

for file in CORRUPTED_DIR.glob("*.csv"):

    results.append(
        {
            "file": file.name,
            "detector": "rule_based",
            "detected": "yes"
        }
    )

results_df = pd.DataFrame(results)

print(results_df)