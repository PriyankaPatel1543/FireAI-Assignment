EMAIL = r"[\w\.-]+@[\w\.-]+"
PHONE = r"\d{3}-\d{3}-\d{4}"


def detect_pii(df):

    if "resolution_description" not in df.columns:
        return ["Missing column: resolution_description"]

    issues = []

    text = df[
        "resolution_description"
    ].astype(str)

    email_count = text.str.contains(
        EMAIL,
        regex=True
    ).sum()

    phone_count = text.str.contains(
        PHONE,
        regex=True
    ).sum()

    if email_count > 0:
        issues.append(
            f"Emails found: {email_count}"
        )

    if phone_count > 0:
        issues.append(
            f"Phones found: {phone_count}"
        )

    return issues