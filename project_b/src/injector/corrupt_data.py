import pandas as pd
from pathlib import Path

# Input and output paths
INPUT_FILE = "data/raw/nyc_311_2023_sample.csv"
OUTPUT_DIR = Path("data/corrupted")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load the original clean dataset
df = pd.read_csv(INPUT_FILE)
print(df.columns.tolist())

print("Original dataset shape:", df.shape)


# 1. Renamed column
def rename_column(data):
    corrupted = data.copy()
    corrupted = corrupted.rename(
        columns={"created_date": "request_date"}
    )
    return corrupted


# 2. Dropped column
def drop_column(data):
    corrupted = data.copy()
    corrupted = corrupted.drop(columns=["agency_name"])
    return corrupted


# 3. Column type change
def change_column_type(data):
    corrupted = data.copy()

    # Convert latitude to text and insert invalid text values
    corrupted["latitude"] = corrupted["latitude"].astype("object")

    count = max(1, int(len(corrupted) * 0.05))

    corrupted.loc[
        corrupted.sample(count, random_state=42).index,
        "latitude"
    ] = "INVALID_LATITUDE"

    return corrupted


# 4. Date format switch halfway through the dataset
def switch_date_format(data):
    corrupted = data.copy()

    dates = pd.to_datetime(
        corrupted["created_date"],
        errors="coerce",
        utc=True
    )

    midpoint = len(corrupted) // 2

    # First half: ISO-style date
    corrupted.loc[:midpoint - 1, "created_date"] = (
        dates.iloc[:midpoint].dt.strftime("%Y-%m-%d %H:%M:%S")
    )

    # Second half: US-style date
    corrupted.loc[midpoint:, "created_date"] = (
        dates.iloc[midpoint:].dt.strftime("%m/%d/%Y %I:%M:%S %p")
    )

    return corrupted


# 5. Exact duplicate rows
def add_exact_duplicates(data):
    corrupted = data.copy()

    count = max(1, int(len(corrupted) * 0.05))

    duplicates = corrupted.sample(
        n=count,
        random_state=42
    )

    corrupted = pd.concat(
        [corrupted, duplicates],
        ignore_index=True
    )

    return corrupted


# 6. Near-duplicate rows
def add_near_duplicates(data):
    corrupted = data.copy()

    count = max(1, int(len(corrupted) * 0.05))

    near_duplicates = corrupted.sample(
        n=count,
        random_state=42
    ).copy()

    # Change one field slightly, keeping the rest of the row identical
    near_duplicates["descriptor"] = (
        near_duplicates["descriptor"].fillna("").astype(str)
        + " "
    )

    corrupted = pd.concat(
        [corrupted, near_duplicates],
        ignore_index=True
    )

    return corrupted

# 7. Null spike in one agency's records
def add_null_spike(data):
    corrupted = data.copy()

    # Find the agency with the most records
    agency = corrupted["agency"].dropna().mode().iloc[0]

    agency_indices = corrupted[
        corrupted["agency"] == agency
    ].index

    count = max(1, int(len(agency_indices) * 0.30))

    selected_indices = corrupted.loc[
        agency_indices
    ].sample(n=count, random_state=42).index

    # Introduce missing values in selected fields
    for column in ["descriptor", "incident_zip", "location_type"]:
        if column in corrupted.columns:
            corrupted.loc[selected_indices, column] = pd.NA

    return corrupted


# 8. Closed date before created date
def reverse_dates(data):
    corrupted = data.copy()

    created = pd.to_datetime(
        corrupted["created_date"],
        errors="coerce"
    )

    valid_indices = created.dropna().index

    count = max(1, int(len(valid_indices) * 0.05))

    selected_indices = pd.Series(valid_indices).sample(
        n=count,
        random_state=42
    )

    # Force column to object type
    corrupted["closed_date"] = corrupted["closed_date"].astype(object)

    for idx in selected_indices:
        corrupted.loc[idx, "closed_date"] = (
            created.loc[idx] - pd.Timedelta(days=1)
        ).strftime("%Y-%m-%d %H:%M:%S")

    test_created = pd.to_datetime(
        corrupted["created_date"],
        errors="coerce"
    )

    test_closed = pd.to_datetime(
        corrupted["closed_date"],
        errors="coerce"
    )

    print("Sample rows:")
    print(
        corrupted.loc[
            selected_indices[:5],
            ["created_date", "closed_date"]
        ]
    )

    print(
        "Rows with closed < created:",
        (test_closed < test_created).sum()
    )

    return corrupted

# 9. ZIP code inconsistent with borough
def mismatch_zip_borough(data):
    corrupted = data.copy()

    valid = corrupted[
        corrupted["borough"].notna()
        & corrupted["incident_zip"].notna()
    ]

    boroughs = valid["borough"].unique()

    if len(boroughs) < 2:
        print("Warning: Not enough boroughs for ZIP mismatch.")
        return corrupted

    # Pick records from two different boroughs
    target_indices = []

    for borough in boroughs[:2]:
        candidates = valid[valid["borough"] == borough]

        if not candidates.empty:
            target_indices.append(candidates.index[0])

    if len(target_indices) == 2:
        first_zip = corrupted.loc[target_indices[0], "incident_zip"]
        second_zip = corrupted.loc[target_indices[1], "incident_zip"]

        # Swap ZIP codes between two different boroughs
        corrupted.loc[target_indices[0], "incident_zip"] = second_zip
        corrupted.loc[target_indices[1], "incident_zip"] = first_zip

    return corrupted


# 10. Complaint type inconsistent with descriptor
def mismatch_complaint_descriptor(data):
    corrupted = data.copy()

    valid = corrupted[
        corrupted["complaint_type"].notna()
        & corrupted["descriptor"].notna()
    ]

    if len(valid) < 2:
        print("Warning: Not enough records for descriptor mismatch.")
        return corrupted

    # Find two records with different complaint types
    pairs = None

    for first_index in valid.index:
        first_type = valid.loc[first_index, "complaint_type"]

        different_type_rows = valid[
            valid["complaint_type"] != first_type
        ]

        if not different_type_rows.empty:
            second_index = different_type_rows.index[0]
            pairs = (first_index, second_index)
            break

    if pairs:
        first_index, second_index = pairs

        first_descriptor = corrupted.loc[first_index, "descriptor"]
        second_descriptor = corrupted.loc[second_index, "descriptor"]

        # Swap descriptors between different complaint types
        corrupted.loc[first_index, "descriptor"] = second_descriptor
        corrupted.loc[second_index, "descriptor"] = first_descriptor

    return corrupted


# 11. Resolution description contradicting status
def contradict_resolution_status(data):
    corrupted = data.copy()

    if "status" not in corrupted.columns:
        return corrupted

    # Closed requests receive a description claiming they are unresolved
    closed_mask = corrupted["status"].astype(str).str.lower().str.contains(
        "closed", na=False
    )

    corrupted.loc[
        closed_mask, "resolution_description"
    ] = "This request is still pending and has not been resolved."

    # Open requests receive a description claiming they are resolved
    open_mask = corrupted["status"].astype(str).str.lower().str.contains(
        "open", na=False
    )

    corrupted.loc[
        open_mask, "resolution_description"
    ] = "The issue has been resolved and corrective action completed."

    return corrupted


# 12. Personal information in free-text fields
def inject_personal_information(data):
    corrupted = data.copy()

    # Use synthetic information only
    synthetic_text = (
        "Contact John Smith at john.smith@example.com "
        "or call 212-555-0198."
    )

    count = max(1, int(len(corrupted) * 0.05))

    selected_indices = corrupted.sample(
        n=count,
        random_state=42
    ).index

    corrupted.loc[
        selected_indices, "resolution_description"
    ] = synthetic_text

    return corrupted


# Store each corruption separately
corruption_functions = {
    "01_renamed_column": rename_column,
    "02_dropped_column": drop_column,
    "03_column_type_change": change_column_type,
    "04_date_format_switch": switch_date_format,
    "05_exact_duplicates": add_exact_duplicates,
    "06_near_duplicates": add_near_duplicates,
    "07_null_spike": add_null_spike,
    "08_closed_before_created": reverse_dates,
    "09_zip_borough_mismatch": mismatch_zip_borough,
    "10_complaint_descriptor_mismatch": mismatch_complaint_descriptor,
    "11_resolution_status_contradiction": contradict_resolution_status,
    "12_personal_information": inject_personal_information
}


# Run all twelve corruption functions
for issue_name, function in corruption_functions.items():

    corrupted_df = function(df)

    output_file = OUTPUT_DIR / f"{issue_name}.csv"

    corrupted_df.to_csv(output_file, index=False)

    print(
        f"{issue_name}: "
        f"{corrupted_df.shape[0]} rows, "
        f"{corrupted_df.shape[1]} columns"
    )

    print("Saved:", output_file)


print("\nAll twelve corruption datasets created successfully!")

