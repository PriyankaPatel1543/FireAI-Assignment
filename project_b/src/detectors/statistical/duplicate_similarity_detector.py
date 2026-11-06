from difflib import SequenceMatcher


def similarity(a, b):
    return SequenceMatcher(
        None,
        str(a),
        str(b)
    ).ratio()

def detect_near_duplicates(df):

    issues = []

    if "descriptor" not in df.columns:
        return issues

    sample = df["descriptor"].dropna().head(100)

    count = 0

    values = sample.tolist()

    for i in range(len(values)):

        for j in range(i + 1, len(values)):

            score = similarity(
                values[i],
                values[j]
            )

            if score > 0.95:
                count += 1

    if count > 0:

        issues.append(
            f"Potential near duplicates: {count}"
        )

    return issues