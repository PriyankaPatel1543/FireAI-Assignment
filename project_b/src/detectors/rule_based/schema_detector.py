REQUIRED_COLUMNS = [
    "created_date",
    "closed_date",
    "agency",
    "agency_name",
    "complaint_type",
    "descriptor",
    "borough",
    "status",
    "resolution_description",
    "location_type",
    "incident_zip",
    "latitude",
    "longitude"
]


def detect_schema_issues(df):
    issues = []

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            issues.append(
                f"Missing column: {column}"
            )

    return issues