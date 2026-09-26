#final_third_pass   is  pass ends at x >= 80
#final_third_entry  is starts below 80 AND ends at/above 80
#progressive_pass   is separate definition later
#Some of the coordinates in our data sit outside the bounds of the pitch (you can see the layout of our pitch coordinates in our event spec, but it's 0-120 along the x axis and 0-80 along the y axis)
from __future__ import annotations
from collections import defaultdict
import pandas as pd


def is_forward_pass(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    start = event.get("location")
    end = event.get("pass", {}).get("end_location")

    # need both locations
    if not start or not end:
        return False

    start_x = start[0]
    end_x = end[0]

    return end_x > start_x

def is_final_third_pass(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    end = event.get("pass", {}).get("end_location")

    if not end:
        return False

    end_x = end[0]

    return end_x >= 80

def is_final_third_entry(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    start = event.get("location")
    end = event.get("pass", {}).get("end_location")

    if not start or not end:
        return False

    start_x = start[0]
    end_x = end[0]

    return start_x < 80 and end_x >= 80

def aggregate_passing(events: list[dict]) -> pd.DataFrame:
    rows = defaultdict(lambda: defaultdict(float))

    for event in events:
        if event.get("type", {}).get("name") != "Pass":
            continue

        player = event.get("player")
        team = event.get("team")

        if not player or not team:
            continue

        key = (
            player["id"],
            player["name"],
            team["name"],
        )

        row = rows[key]

        row["player_id"] = player["id"]
        row["player_name"] = player["name"]
        row["team_name"] = team["name"]

        # count every pass
        row["passes"] += 1

        if is_forward_pass(event):
            row["forward_passes"] += 1

        if is_final_third_pass(event):
            row["final_third_passes"] += 1

        if is_final_third_entry(event):
            row["final_third_entries"] += 1

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows.values()).fillna(0)

    return df