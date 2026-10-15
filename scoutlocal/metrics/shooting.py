
import pandas as pd


# check if a shot is on target
def is_shot_on_target(event):
    if event.get("type", {}).get("name") != "Shot":
        return False

    outcome = event.get("shot", {}).get("outcome", {}).get("name")

    return outcome in {"Saved", "Goal", "Saved to Post"}


# check if a shot is a goal
def is_goal(event):
    if event.get("type", {}).get("name") != "Shot":
        return False

    outcome = event.get("shot", {}).get("outcome", {}).get("name")

    return outcome == "Goal"


# check if a shot is taken inside the penalty box
def is_shot_inside_box(event):
    if event.get("type", {}).get("name") != "Shot":
        return False

    location = event.get("location")

    if not location or len(location) < 2:
        return False

    x, y = location[:2]

    return x >= 102 and 18 <= y <= 62


# get non penalty xg from a shot
def get_non_penalty_xg(event):
    if event.get("type", {}).get("name") != "Shot":
        return 0.0

    shot = event.get("shot", {})
    shot_type = shot.get("type", {}).get("name")

    if shot_type == "Penalty":
        return 0.0

    return float(shot.get("statsbomb_xg", 0.0))


# check if a shot uses a specific body part
def is_shot_body_part(event, body_part):
    if event.get("type", {}).get("name") != "Shot":
        return False

    shot_body_part = (
        event.get("shot", {})
        .get("body_part", {})
        .get("name")
    )

    return shot_body_part == body_part


# aggregate shooting metrics for each player
def aggregate_shooting(events):
    rows = {}

    for event in events:
        if event.get("type", {}).get("name") != "Shot":
            continue

        player = event.get("player", {})
        team = event.get("team", {})

        player_id = player.get("id")
        team_id = team.get("id")

        if player_id is None or team_id is None:
            continue

        key = (player_id, team_id)

        if key not in rows:
            rows[key] = {
                "player_id": player_id,
                "player_name": player.get("name"),
                "team_id": team_id,
                "team_name": team.get("name"),
                "shots_on_target": 0,
                "goals": 0,
                "shots_inside_box": 0,
                "non_penalty_xg": 0.0,
            }

        # count shots on target for each player
        if is_shot_on_target(event):
            rows[key]["shots_on_target"] += 1

        # count goals for each player
        if is_goal(event):
            rows[key]["goals"] += 1

        # count shots inside the penalty box for each player
        if is_shot_inside_box(event):
            rows[key]["shots_inside_box"] += 1

        # add non penalty xg for each player
        rows[key]["non_penalty_xg"] += get_non_penalty_xg(event)

    return pd.DataFrame(
        list(rows.values()),
        columns=[
            "player_id",
            "player_name",
            "team_id",
            "team_name",
            "shots_on_target",
            "goals",
            "shots_inside_box",
            "non_penalty_xg",
        ],
    )
