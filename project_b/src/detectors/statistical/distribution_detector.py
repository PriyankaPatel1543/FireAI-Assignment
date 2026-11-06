import pandas as pd


def detect_distribution_anomalies(df):

    issues = []

    if "latitude" not in df.columns:
        return issues

    numeric = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    invalid = numeric.isna().sum()

    if invalid > 0:

        issues.append(
            f"Non-numeric latitude values: "
            f"{invalid}"
        )

    return issues