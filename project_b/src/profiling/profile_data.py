
import pandas as pd
import json
from pathlib import Path

# ------------------------------------------------
# 1. Load dataset
# ------------------------------------------------

DATA_PATH = Path("data/raw/nyc_311_2023_sample.csv")

df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("          NYC 311 DATA QUALITY PROFILING")
print("=" * 60)

total_rows = len(df)
total_columns = len(df.columns)

print(f"\nTotal records: {total_rows}")
print(f"Total columns: {total_columns}")

Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

# ------------------------------------------------
# 2. Basic dataset information
# ------------------------------------------------

print("\n--- DATA TYPES ---")
print(df.dtypes)

print("\n--- DATASET INFORMATION ---")
df.info()

# Treat whitespace-only strings as missing
df = df.replace(r"^\s*$", pd.NA, regex=True)


# ------------------------------------------------
# 3. Missing value analysis
# ------------------------------------------------

print("\n--- MISSING VALUE ANALYSIS ---")

missing_count = df.isnull().sum()

missing_percentage = (
    missing_count / total_rows * 100
).round(2)

missing_report = pd.DataFrame({
    "Missing_Count": missing_count,
    "Missing_Percentage": missing_percentage
})

print(missing_report)

# Save missing value report
missing_report.to_csv(
    "data/processed/missing_values.csv"
)


# ------------------------------------------------
# 4. Duplicate analysis
# ------------------------------------------------

print("\n--- DUPLICATE ANALYSIS ---")

exact_duplicates = df.duplicated().sum()

duplicate_keys = df["unique_key"].duplicated().sum()

print("Exact duplicate rows:", exact_duplicates)
print("Duplicate Unique Keys:", duplicate_keys)


# ------------------------------------------------
# 5. Date validation
# ------------------------------------------------

print("\n--- DATE VALIDATION ---")

created = pd.to_datetime(
    df["created_date"],
    errors="coerce",
    utc=True
)

closed = pd.to_datetime(
    df["closed_date"],
    errors="coerce",
    utc=True
)

invalid_created_dates = (
    df["created_date"].notna() & created.isna()
).sum()

invalid_closed_dates = (
    df["closed_date"].notna() & closed.isna()
).sum()

closed_before_created = (
    created.notna() &
    closed.notna() &
    (closed < created)
).sum()

print("Invalid Created Dates:", invalid_created_dates)
print("Invalid Closed Dates:", invalid_closed_dates)
print("Closed Before Created:", closed_before_created)


# ------------------------------------------------
# 6. Geographic validation
# ------------------------------------------------

print("\n--- GEO DATA VALIDATION ---")

latitude = pd.to_numeric(
    df["latitude"], errors="coerce"
)

longitude = pd.to_numeric(
    df["longitude"], errors="coerce"
)

invalid_latitude = (
    latitude.notna() &
    ~latitude.between(-90, 90)
).sum()

invalid_longitude = (
    longitude.notna() &
    ~longitude.between(-180, 180)
).sum()

print("Invalid Latitude:", invalid_latitude)
print("Invalid Longitude:", invalid_longitude)


# ------------------------------------------------
# 7. ZIP code validation
# ------------------------------------------------

print("\n--- ZIP CODE VALIDATION ---")

zip_code = df["incident_zip"].astype("string").str.strip()

invalid_zip = (
    zip_code.notna() &
    ~zip_code.str.fullmatch(r"\d{5}", na=False)
).sum()

print("Invalid ZIP Codes:", invalid_zip)


# ------------------------------------------------
# 8. Category analysis
# ------------------------------------------------

print("\n--- COMPLAINT TYPE DISTRIBUTION ---")

print(df["complaint_type"].value_counts().head(10))

print("\n--- STATUS DISTRIBUTION ---")

print(df["status"].value_counts(dropna=False))


# ------------------------------------------------
# 9. Collect profiling results
# ------------------------------------------------

results = {
    "total_rows": int(total_rows),
    "total_columns": int(total_columns),
    "exact_duplicates": int(exact_duplicates),
    "duplicate_unique_keys": int(duplicate_keys),
    "invalid_created_dates": int(invalid_created_dates),
    "invalid_closed_dates": int(invalid_closed_dates),
    "closed_before_created": int(closed_before_created),
    "invalid_latitude": int(invalid_latitude),
    "invalid_longitude": int(invalid_longitude),
    "invalid_zip_codes": int(invalid_zip)
}

# Create output directory
Path("data/processed").mkdir(
    parents=True,
    exist_ok=True
)

# Save profiling results
with open(
    "data/processed/profiling_results.json",
    "w"
) as file:
    json.dump(results, file, indent=4)


# ------------------------------------------------
# 10. Generate issue examples
# ------------------------------------------------

issues = []

def add_issue(issue_name, mask, columns):
    examples = df.loc[mask, columns].head(5)

    for _, row in examples.iterrows():
        issues.append({
            "Issue": issue_name,
            "Example": row.to_dict()
        })


add_issue(
    "Closed Before Created",
    created.notna() & closed.notna() & (closed < created),
    ["unique_key", "created_date", "closed_date"]
)

add_issue(
    "Invalid Created Date",
    df["created_date"].notna() & created.isna(),
    ["unique_key", "created_date"]
)

add_issue(
    "Invalid ZIP Code",
    zip_code.notna() &
    ~zip_code.str.fullmatch(r"\d{5}", na=False),
    ["unique_key", "incident_zip", "borough"]
)

add_issue(
    "Invalid Latitude",
    latitude.notna() & ~latitude.between(-90, 90),
    ["unique_key", "latitude", "longitude"]
)

examples_df = pd.DataFrame(issues)

examples_df.to_json(
    "data/processed/issue_examples.json",
    orient="records",
    indent=4,
    default_handler=str
)

print("\n" + "=" * 60)
print("PROFILING COMPLETED SUCCESSFULLY")
print("=" * 60)

print("\nResults saved in data/processed/")
