from pathlib import Path
import pandas as pd

CORRUPTED_DIR = Path("data/corrupted")

def run_rule_checks(df):
    issues = []

    if "created_date" not in df.columns:
        issues.append("Missing created_date")

    if df.duplicated().sum() > 0:
        issues.append("Duplicate records")

    return issues


def run_statistical_checks(df):
    issues = []

    for column in df.columns:

        null_rate = df[column].isna().mean()

        if null_rate > 0.20:
            issues.append(
                f"High null rate: {column}"
            )

    return issues


def run_llm_checks(df):
    return [
        "Semantic review required"
    ]


for file in CORRUPTED_DIR.glob("*.csv"):

    print("\n" + "=" * 60)
    print(file.name)
    print("=" * 60)

    df = pd.read_csv(file)

    rule_issues = run_rule_checks(df)

    statistical_issues = run_statistical_checks(df)

    if rule_issues or statistical_issues:

        llm_issues = run_llm_checks(df)

    else:

        llm_issues = []

    print("Rules:", rule_issues)
    print("Statistics:", statistical_issues)
    print("LLM:", llm_issues)