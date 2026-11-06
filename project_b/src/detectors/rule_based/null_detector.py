def detect_null_spike(df):

    if len(df) == 0:
        return []

    issues = []

    for column in df.columns:
        rate = df[column].isna().mean()

        if rate > 0.20:
            issues.append(
                f"{column}: {rate:.2%} nulls"
            )

    return issues