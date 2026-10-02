# final_third_pass  is pass ends at x >= 80
# final_third_entry is starts below 80 AND ends at/above 80
# progressive_pass  is separate definition later
# StatsBomb pitch coordinates: x 0-120, y 0-80

from __future__ import annotations
from collections import defaultdict
import pandas as pd
import math 

def is_completed_pass(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    pass_data = event.get("pass")

    if not pass_data:
        return False

    # no outcome means the pass was completed
    return pass_data.get("outcome") is None


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

def is_penalty_box_entry(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    # only use open play
    play_pattern = (
        event.get("play_pattern", {}).get("name")
    )

    if play_pattern != "Regular Play":
        return False

    start = event.get("location")
    end = event.get("pass", {}).get("end_location")

    # need both locations
    if not start or not end:
        return False

    # check if pass starts inside the box
    start_in_box = (
        start[0] >= 102
        and 18 <= start[1] <= 62
    )

    # check if pass ends inside the box
    end_in_box = (
        end[0] >= 102
        and 18 <= end[1] <= 62
    )

    # starts outside and ends inside
    return not start_in_box and end_in_box

def is_progressive_pass(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    # only use open play
    play_pattern = (
        event.get("play_pattern", {}).get("name")
    )

    if play_pattern != "Regular Play":
        return False

    start = event.get("location")
    end = event.get("pass", {}).get("end_location")

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

    # how much closer the pass gets to goal
    progress_pct = (
        start_distance - end_distance
    ) / start_distance

    return progress_pct >= 0.25

def is_long_pass(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    pass_data = event.get("pass")

    if not pass_data:
        return False

    length = pass_data.get("length")
    height = pass_data.get("height", {}).get("name")

    # need pass length
    if length is None:
        return False

    # statsbomb long pass definition
    return (
        height == "High Pass"
        and length > 30
    )

def is_cross(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    pass_data = event.get("pass")

    if not pass_data:
        return False

    return pass_data.get("cross") is True

def is_shot_assist(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    pass_data = event.get("pass")

    if not pass_data:
        return False

    return pass_data.get("shot_assist") is True


def is_goal_assist(event: dict) -> bool:
    # only check passes
    if event.get("type", {}).get("name") != "Pass":
        return False

    pass_data = event.get("pass")

    if not pass_data:
        return False

    return pass_data.get("goal_assist") is True


def is_key_pass(event: dict) -> bool:
    return (
        is_shot_assist(event)
        or is_goal_assist(event)
    )

def aggregate_passing(events: list[dict]) -> pd.DataFrame:
    rows = defaultdict(lambda: defaultdict(float))

    for event in events:
        # only use pass events
        if event.get("type", {}).get("name") != "Pass":
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

        # check completion once
        completed = is_completed_pass(event)

        # all passes
        row["passes"] += 1

        if completed:
            row["completed_passes"] += 1

        # forward passes
        if is_forward_pass(event):
            row["forward_passes"] += 1

            if completed:
                row["completed_forward_passes"] += 1

        # passes ending in the final third
        if is_final_third_pass(event):
            row["final_third_passes"] += 1

            if completed:
                row["completed_final_third_passes"] += 1

        # passes entering the final third
        if is_final_third_entry(event):
            row["final_third_entries"] += 1

            if completed:
                row["completed_final_third_entries"] += 1

        # passes entering the penalty box
        if is_penalty_box_entry(event):
            row["penalty_box_entries"] += 1

            if completed:
                row["completed_penalty_box_entries"] += 1

        # progressive passes
        if is_progressive_pass(event):
            row["progressive_passes"] += 1

            if completed:
                row["completed_progressive_passes"] += 1

        # long passes
        if is_long_pass(event):
            row["long_passes"] += 1

            if completed:
                row["completed_long_passes"] += 1

        # crosses
        if is_cross(event):
            row["crosses"] += 1

            if completed:
                row["completed_crosses"] += 1
                
        # shot assists
        if is_shot_assist(event):
            row["shot_assists"] += 1

        # goal assists
        if is_goal_assist(event):
            row["goal_assists"] += 1

        # key passes
        if is_key_pass(event):
            row["key_passes"] += 1

    # return empty table if there were no passes
    if not rows:
        return pd.DataFrame()

    # turn player data into a dataframe
    df = pd.DataFrame(rows.values()).fillna(0)

    return df
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

        # check completion once
        completed = is_completed_pass(event)

        # count every pass
        row["passes"] += 1

        # count completed passes
        if completed:
            row["completed_passes"] += 1

        # count forward passes
        if is_forward_pass(event):
            row["forward_passes"] += 1

            if completed:
                row["completed_forward_passes"] += 1

        # passes that end in the final third
        if is_final_third_pass(event):
            row["final_third_passes"] += 1

            if completed:
                row["completed_final_third_passes"] += 1

        # passes that enter the final third
        if is_final_third_entry(event):
            row["final_third_entries"] += 1

            if completed:
                row["completed_final_third_entries"] += 1

        # progressive passes in open play
        if is_progressive_pass(event):
            row["progressive_passes"] += 1

            if completed:
                row["completed_progressive_passes"] += 1

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows.values()).fillna(0)

    return df