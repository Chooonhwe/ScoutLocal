
import pandas as pd


# load player metrics and season positions
metrics = pd.read_csv("data/player_metrics.csv")
positions = pd.read_csv("data/player_positions.csv")

# select position columns
positions = positions[
    [
        "player_id",
        "team_id",
        "primary_position",
        "primary_position_group",
        "starts",
    ]
]

# verify player team keys are unique
assert not metrics.duplicated(
    ["player_id", "team_id"]
).any()

assert not positions.duplicated(
    ["player_id", "team_id"]
).any()

# join positions without dropping player records
merged = metrics.merge(
    positions,
    on=["player_id", "team_id"],
    how="left",
    validate="one_to_one",
)

# keep unclassified players clearly labelled
merged["primary_position_group"] = (
    merged["primary_position_group"].fillna("Unknown")
)
merged["primary_position"] = (
    merged["primary_position"].fillna("Unknown")
)

# validate that we have not lost players
assert len(merged) == len(metrics)

# save the enriched dataset separately
merged.to_csv(
    "data/player_metrics_with_positions.csv",
    index=False,
    encoding="utf-8-sig",
)

print("\nPOSITION MERGE VALIDATION\n")
print("Original players:", len(metrics))
print("Merged players:", len(merged))
print(
    "Players with positions:",
    (merged["primary_position_group"] != "Unknown").sum(),
)
print(
    "Unknown positions:",
    (merged["primary_position_group"] == "Unknown").sum(),
)
print(
    "Duplicate player/team IDs:",
    merged.duplicated(["player_id", "team_id"]).sum(),
)

# inspect three previously compared players
selected = merged[
    merged["player_id"].isin([124903, 20837, 161099])
]

print("\nPLAYER POSITION CHECK\n")
print(
    selected[
        [
            "player_name",
            "team_name",
            "minutes",
            "primary_position",
            "primary_position_group",
            "starts",
        ]
    ].to_string(
        index=False,
        float_format=lambda value: f"{value:.2f}",
    )
)
