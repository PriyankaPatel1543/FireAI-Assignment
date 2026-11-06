from pathlib import Path
import pandas as pd

from null_anomaly_detector import (
    detect_null_anomalies
)

from duplicate_similarity_detector import (
    detect_near_duplicates
)

from distribution_detector import (
    detect_distribution_anomalies
)

CORRUPTED_DIR = Path("data/corrupted")

for file in CORRUPTED_DIR.glob("*.csv"):

    print("\n" + "=" * 60)
    print(file.name)
    print("=" * 60)

    df = pd.read_csv(file)

    issues = []

    issues.extend(
        detect_null_anomalies(df)
    )

    issues.extend(
        detect_near_duplicates(df)
    )

    issues.extend(
        detect_distribution_anomalies(df)
    )

    if issues:

        for issue in issues:
            print("ALERT:", issue)

    else:
        print("No statistical anomalies")