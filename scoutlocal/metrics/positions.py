
import pandas as pd


# classify statsbomb positions into scouting roles
def classify_position(position_name):
    if not position_name:
        return "Unknown"

    position = position_name.lower()

    # goalkeeper
    if position == "goalkeeper":
        return "Goalkeeper"

    # center backs
    if "center back" in position:
        return "Center Back"

    # wing backs and full backs
    if "wing back" in position or position in {
        "left back",
        "right back",
    }:
        return "Full Back"

    # defensive midfielders
    if "defensive midfield" in position:
        return "Defensive Midfielder"

    # central midfielders
    if "center midfield" in position:
        return "Central Midfielder"

    # attacking midfielders
    if "attacking midfield" in position:
        return "Attacking Midfielder"

    # wide midfielders and wingers
    if "wing" in position or "midfield" in position:
        return "Winger"

    # forwards
    if "forward" in position:
        return "Forward"

    return "Unknown"


# extract starting positions from one match
def extract_match_positions(events):
    rows = []

    for event in events:
        # only inspect starting lineups
        if event.get("type", {}).get("name") != "Starting XI":
            continue

        team = event.get("team") or {}
        lineup = event.get("tactics", {}).get("lineup") or []

        for lineup_player in lineup:
            player = lineup_player.get("player") or {}
            position = lineup_player.get("position") or {}

            player_id = player.get("id")
            team_id = team.get("id")

            if player_id is None or team_id is None:
                continue

            position_name = position.get("name")

            rows.append({
                "player_id": player_id,
                "team_id": team_id,
                "player_name": player.get("name"),
                "team_name": team.get("name"),
                "position_name": position_name,
                "position_group": classify_position(position_name),
            })

    return pd.DataFrame(
        rows,
        columns=[
            "player_id",
            "team_id",
            "player_name",
            "team_name",
            "position_name",
            "position_group",
        ],
    )
