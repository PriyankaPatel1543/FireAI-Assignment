Project B Results
Dataset
NYC 311 Service Requests (2023)

Corruptions Injected
Renamed Column
Dropped Column
Type Change
Date Format Switch
Exact Duplicates
Near Duplicates
Null Spike
Closed Before Created
ZIP/Borough Mismatch
Complaint/Descriptor Mismatch
Resolution Description Contradiction
Personal Information
Detector Comparison
Corruption	Rules	Statistical	LLM
Renamed Column	Yes	No	No
Dropped Column	Yes	No	No
Type Change	Yes	Yes	Yes
Date Format Switch	Yes	Partial	Yes
Exact Duplicate	Yes	Yes	No
Near Duplicate	Partial	Yes	Yes
Null Spike	Yes	Yes	Yes
ZIP/Borough Mismatch	Partial	Partial	Yes
Complaint/Descriptor Mismatch	Partial	Partial	Yes
Resolution Contradiction	Partial	No	Yes
Personal Information	Yes	Partial	Yes
Recommended Architecture
Rules → Schema Validation, Duplicates

Statistical Models → Anomaly Detection

LLM → Semantic Consistency Checks

Hybrid Pipeline → Rules + Statistics + LLM Review