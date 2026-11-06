from pathlib import Path
import pandas as pd

from schema_detector import detect_schema_issues
from date_detector import detect_date_issues
from duplicate_detector import detect_duplicates
from null_detector import detect_null_spike
from pii_detector import detect_pii

CORRUPTED_DIR = Path("data/corrupted")

for file in CORRUPTED_DIR.glob("*.csv"):

    print("\n" + "=" * 60)
    print(file.name)
    print("=" * 60)

    try:
        df = pd.read_csv(file)

        issues = []

        issues.extend(detect_schema_issues(df))
        issues.extend(detect_date_issues(df))
        issues.extend(detect_duplicates(df))
        issues.extend(detect_null_spike(df))
        issues.extend(detect_pii(df))

        if issues:
            for issue in issues:
                print("ALERT:", issue)
        else:
            print("No issues detected")

    except Exception as e:
        print("ERROR:", e)