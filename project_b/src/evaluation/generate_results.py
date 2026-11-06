import pandas as pd

comparison = pd.DataFrame(

    [
        ["Renamed Column", "Yes", "No", "No"],
        ["Dropped Column", "Yes", "No", "No"],
        ["Type Change", "Yes", "Yes", "Yes"],
        ["Date Format Switch", "Yes", "Partial", "Yes"],
        ["Exact Duplicate", "Yes", "Yes", "No"],
        ["Near Duplicate", "Partial", "Yes", "Yes"],
        ["Null Spike", "Yes", "Yes", "Yes"],
        ["ZIP/Borough", "Partial", "Partial", "Yes"],
        ["Complaint/Descriptor", "Partial", "Partial", "Yes"],
        ["Resolution Contradiction", "Partial", "No", "Yes"],
        ["PII", "Yes", "Partial", "Yes"]
    ],

    columns=[
        "Corruption",
        "Rules",
        "Statistical",
        "LLM"
    ]
)

print(comparison)