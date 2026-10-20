
import pandas as pd

from scoutlocal.data.statsbomb import StatsBombOpenData
from scoutlocal.metrics.positions import extract_match_positions


# load indian super league match data
client = StatsBombOpenData()
matches = client.matches(1238, 108)

all_positions = []

# use consistent team names
team_name_lookup = {
    7282: "ATK Mohun Bagan",
    7289: "Hyderabad",
}

# collect player starting positions from every match
for index, match in enumerate(matches, start=1):
    match_id = match["match_id"]

    print(f"Processing match {index}/{len(matches)}")

    events = client.events(match_id)

    # fix inconsistent team names
    for event in events:
        team = event.get("team") or {}
        team_id = team.get("id")

        if team_id in team_name_lookup:
            team["name"] = team_name_lookup[team_id]

    match_positions = extract_match_positions(events)

    if not match_positions.empty:
        all_positions.append(match_positions)

if not all_positions:
    raise RuntimeError("No starting positions found.")

# combine starting positions from all matches
positions = pd.concat(
    all_positions,
    ignore_index=True,
)

# count how many matches each player starts in each position
position_counts = (
    positions
    .groupby(
        ["player_id", "team_id", "position_name", "position_group"],
        as_index=False,
    )
    .size()
    .rename(columns={"size": "starts"})
)

# select each player's most frequent starting position
primary_positions = (
    position_counts
    .sort_values(
        ["player_id", "team_id", "starts", "position_name"],
        ascending=[True, True, False, True],
    )
    .drop_duplicates(["player_id", "team_id"])
    .rename(
        columns={
            "position_name": "primary_position",
            "position_group": "primary_position_group",
        }
    )
)

# save season positions
primary_positions.to_csv(
    "data/player_positions.csv",
    index=False,
    encoding="utf-8-sig",
)

print("\nSEASON POSITION VALIDATION\n")
print("Total starting lineup entries:", len(positions))
print("Players with starting positions:", len(primary_positions))
print("Unknown primary positions:",
      (primary_positions["primary_position_group"] == "Unknown").sum())

print("\nPOSITION GROUP DISTRIBUTION\n")
print(primary_positions["primary_position_group"].value_counts())
