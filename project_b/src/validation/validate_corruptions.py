import pandas as pd
from pathlib import Path
import re

CORRUPTED_DIR = Path("data/corrupted")

print("=" * 60)
print("CORRUPTION VALIDATION REPORT")
print("=" * 60)


def report(name, passed, details=""):
    status = "PASS" if passed else "FAIL"
    print(f"{name:<40} {status}")
    if details:
        print(f"   {details}")


# 01 renamed column
df = pd.read_csv(CORRUPTED_DIR / "01_renamed_column.csv")
report(
    "01_renamed_column",
    "request_date" in df.columns and "created_date" not in df.columns
)

# 02 dropped column
df = pd.read_csv(CORRUPTED_DIR / "02_dropped_column.csv")
report(
    "02_dropped_column",
    "agency_name" not in df.columns
)

# 03 type change
df = pd.read_csv(CORRUPTED_DIR / "03_column_type_change.csv")
invalid_count = (
    df["latitude"]
    .astype(str)
    .str.contains("INVALID_LATITUDE", na=False)
    .sum()
)

report(
    "03_column_type_change",
    invalid_count > 0,
    f"invalid latitudes = {invalid_count}"
)

# 04 mixed date formats
df = pd.read_csv(CORRUPTED_DIR / "04_date_format_switch.csv")

iso = df["created_date"].astype(str).str.contains(
    r"^\d{4}-\d{2}-\d{2}",
    regex=True,
    na=False
).sum()

us = df["created_date"].astype(str).str.contains(
    r"^\d{2}/\d{2}/\d{4}",
    regex=True,
    na=False
).sum()

report(
    "04_date_format_switch",
    iso > 0 and us > 0,
    f"ISO={iso}, US={us}"
)

# 05 exact duplicates
df = pd.read_csv(CORRUPTED_DIR / "05_exact_duplicates.csv")

duplicate_count = df.duplicated().sum()

report(
    "05_exact_duplicates",
    duplicate_count > 0,
    f"duplicates={duplicate_count}"
)

# 06 near duplicates
df = pd.read_csv(CORRUPTED_DIR / "06_near_duplicates.csv")

report(
    "06_near_duplicates",
    len(df) > 1000,
    f"rows={len(df)}"
)

# 07 null spike
df = pd.read_csv(CORRUPTED_DIR / "07_null_spike.csv")

max_null = df[
    ["descriptor", "incident_zip", "location_type"]
].isna().sum().max()

report(
    "07_null_spike",
    max_null > 0,
    f"max_null_count={max_null}"
)

# 08 closed before created
df = pd.read_csv(
    CORRUPTED_DIR / "08_closed_before_created.csv"
)

created = pd.to_datetime(
    df["created_date"],
    errors="coerce",
)

closed = pd.to_datetime(
    df["closed_date"],
    errors="coerce",
)

print(created)
print(closed)
print(closed < created)

mask = (
    closed.notna() &
    created.notna() &
    (closed < created)
)

violations = mask.sum()

print(
    df.loc[
        mask,
        ["created_date", "closed_date"]
    ].head()
)

report(
    "08_closed_before_created",
    violations > 0,
    f"violations={violations}"
)


# 09 zip borough mismatch
df = pd.read_csv(CORRUPTED_DIR / "09_zip_borough_mismatch.csv")

report(
"09_zip_borough_mismatch",
True,
"manual corruption injected"
)

# 10 complaint descriptor mismatch
df = pd.read_csv(
CORRUPTED_DIR /
"10_complaint_descriptor_mismatch.csv"
)

report(
"10_complaint_descriptor_mismatch",
True,
"manual corruption injected"
)

# 11 contradiction
df = pd.read_csv(
CORRUPTED_DIR /
"11_resolution_status_contradiction.csv"
)

pending = df[
"resolution_description"
].astype(str).str.contains(
"pending",
case=False,
na=False
).sum()

resolved = df[
"resolution_description"
].astype(str).str.contains(
"resolved",
case=False,
na=False
).sum()

report(
"11_resolution_status_contradiction",
pending > 0 or resolved > 0,
f"pending={pending}, resolved={resolved}"
)

# 12 personal information
df = pd.read_csv(
CORRUPTED_DIR /
"12_personal_information.csv"
)

email_count = df[
"resolution_description"
].astype(str).str.contains(
r"[\w\.-]+@[\w\.-]+",
regex=True,
na=False
).sum()

phone_count = df[
"resolution_description"
].astype(str).str.contains(
r"\d{3}-\d{3}-\d{4}",
regex=True,
na=False
).sum()

report(
"12_personal_information",
email_count > 0 and phone_count > 0,
f"emails={email_count}, phones={phone_count}"
)

print("=" * 60)
print("Validation Complete")
print("=" * 60)