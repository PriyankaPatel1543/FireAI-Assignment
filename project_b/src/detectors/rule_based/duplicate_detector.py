def detect_duplicates(df):
    duplicates = df.duplicated().sum()

    if duplicates > 0:
        return [
            f"Duplicate rows: {duplicates}"
        ]

    return []