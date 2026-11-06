def detect_null_anomalies(df):

    issues = []

    for column in df.columns:

        null_rate = df[column].isna().mean()

        if null_rate > 0.15:

            issues.append(
                f"{column}: unusually high null rate "
                f"({null_rate:.2%})"
            )

    return issues