import pandas as pd


def detect_date_issues(df):
    issues = []

    if "created_date" not in df.columns:
        issues.append(
            "Missing column: created_date"
        )
        return issues

    if "closed_date" not in df.columns:
        issues.append(
            "Missing column: closed_date"
        )
        return issues

    created = pd.to_datetime(
        df["created_date"],
        errors="coerce"
    )

    closed = pd.to_datetime(
        df["closed_date"],
        errors="coerce"
    )

    violations = (
        closed < created
    ).sum()

    if violations > 0:
        issues.append(
            f"Closed before created: {violations}"
        )

    return issues