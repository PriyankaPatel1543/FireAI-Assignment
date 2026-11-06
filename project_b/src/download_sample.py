
import requests
import pandas as pd
from pathlib import Path

# Official NYC Open Data API
API_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

# Columns required for our project
columns = [
    "unique_key",
    "created_date",
    "closed_date",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "location_type",
    "incident_zip",
    "borough",
    "latitude",
    "longitude",
    "status",
    "resolution_description"
]

# Filter records created during 2023
params = {
    "$select": ",".join(columns),
    "$where": (
        "created_date >= '2023-01-01T00:00:00' "
        "AND created_date < '2024-01-01T00:00:00'"
    ),
    "$limit": 1000,
    "$order": "unique_key"
}

print("Downloading NYC 311 sample data...")

response = requests.get(API_URL, params=params, timeout=120)

# Check whether API request was successful
response.raise_for_status()

data = response.json()

# Convert JSON into DataFrame
df = pd.DataFrame(data)

# Create output directory
output_path = Path("data/raw")
output_path.mkdir(parents=True, exist_ok=True)

# Save dataset
file_path = output_path / "nyc_311_2023_sample.csv"
df.to_csv(file_path, index=False)

print("\nDownload completed!")
print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("Saved at:", file_path)

print("\nDataset preview:")
print(df.head())

print("\nDataset information:")
print(df.info())
