from pathlib import Path
import pandas as pd

from semantic_consistency_detector import (
    check_complaint_descriptor
)

from resolution_detector import (
    check_resolution_status
)

CORRUPTED_DIR = Path(
    "data/corrupted"
)

FILES = [
    "10_complaint_descriptor_mismatch.csv",
    "11_resolution_status_contradiction.csv"
]

for filename in FILES:

    print("\n" + "=" * 60)
    print(filename)
    print("=" * 60)

    df = pd.read_csv(
        CORRUPTED_DIR / filename
    )

    sample = df.sample(
        10,
        random_state=42
    )

    for _, row in sample.iterrows():

        if filename.startswith("10"):

            result = check_complaint_descriptor(
                row["complaint_type"],
                row["descriptor"]
            )

            print(result)

        if filename.startswith("11"):

            result = check_resolution_status(
                row["status"],
                row["resolution_description"]
            )

            print(result)