from __future__ import annotations

import math
from collections import defaultdict
import pandas as pd

def is_progressive_carry(event: dict) -> bool:
    # only check carries
    if event.get("type", {}).get("name") != "Carry":
        return False

    start = event.get("location")
    end = event.get("carry", {}).get("end_location")

    # need both locations
    if not start or not end:
        return False

    # centre of opponent goal
    goal_x = 120
    goal_y = 40

    # distance from start to goal
    start_distance = math.sqrt(
        (goal_x - start[0]) ** 2
        + (goal_y - start[1]) ** 2
    )

    # distance from end to goal
    end_distance = math.sqrt(
        (goal_x - end[0]) ** 2
        + (goal_y - end[1]) ** 2
    )

    # avoid dividing by zero
    if start_distance == 0:
        return False

    # how much closer the carry gets to goal
    progress_pct = (
        start_distance - end_distance
    ) / start_distance

    return progress_pct >= 0.25

def is_forward_carry(event: dict) -> bool:
    # only check carries
    if event.get("type", {}).get("name") != "Carry":
        return False

    start = event.get("location")
    end = event.get("carry", {}).get("end_location")

    # need both locations
    if not start or not end:
        return False

    return end[0] > start[0]

def is_final_third_carry_entry(event: dict) -> bool:
    # only check carries
    if event.get("type", {}).get("name") != "Carry":
        return False

    start = event.get("location")
    end = event.get("carry", {}).get("end_location")

    # need both locations
    if not start or not end:
        return False

    return start[0] < 80 and end[0] >= 80

def is_penalty_box_carry_entry(event: dict) -> bool:
    # only check carries
    if event.get("type", {}).get("name") != "Carry":
        return False

    start = event.get("location")
    end = event.get("carry", {}).get("end_location")

    # need both locations
    if not start or not end:
        return False

    # check if carry starts inside the box
    start_in_box = (
        start[0] >= 102
        and 18 <= start[1] <= 62
    )

    # check if carry ends inside the box
    end_in_box = (
        end[0] >= 102
        and 18 <= end[1] <= 62
    )

    # starts outside and ends inside
    return not start_in_box and end_in_box

def get_carry_distance(event: dict) -> float:
    # only check carries
    if event.get("type", {}).get("name") != "Carry":
        return 0.0

    start = event.get("location")
    end = event.get("carry", {}).get("end_location")

    # need both locations
    if not start or not end:
        return 0.0

    return math.sqrt(
        (end[0] - start[0]) ** 2
        + (end[1] - start[1]) ** 2
    )


def get_forward_carry_distance(event: dict) -> float:
    # only check carries
    if event.get("type", {}).get("name") != "Carry":
        return 0.0

    start = event.get("location")
    end = event.get("carry", {}).get("end_location")

    # need both locations
    if not start or not end:
        return 0.0

    return max(0.0, end[0] - start[0])

def aggregate_carrying(events: list[dict]) -> pd.DataFrame:
    rows = defaultdict(lambda: defaultdict(float))

    for event in events:
        # only use carry events
        if event.get("type", {}).get("name") != "Carry":
            continue

        player = event.get("player")
        team = event.get("team")

        # need player and team info
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

        # all carries
        row["carries"] += 1

        # forward carries
        if is_forward_carry(event):
            row["forward_carries"] += 1

        # progressive carries
        if is_progressive_carry(event):
            row["progressive_carries"] += 1

        # final third entries
        if is_final_third_carry_entry(event):
            row["final_third_carry_entries"] += 1

        # penalty box entries
        if is_penalty_box_carry_entry(event):
            row["penalty_box_carry_entries"] += 1

        # carry distance
        row["carry_distance"] += get_carry_distance(event)

        # forward carry distance
        row["forward_carry_distance"] += (
            get_forward_carry_distance(event)
        )

    # return empty table if there were no carries
    if not rows:
        return pd.DataFrame()

    # turn player data into a dataframe
    df = pd.DataFrame(rows.values()).fillna(0)

    stat_columns = [
        "carries",
        "forward_carries",
        "progressive_carries",
        "final_third_carry_entries",
        "penalty_box_carry_entries",
        "carry_distance",
        "forward_carry_distance",
    ]

    for column in stat_columns:
        if column not in df.columns:
            df[column] = 0

    return df