import pandas as pd

# check if an event is a tackle
def is_tackle(event):
    if event.get("type", {}).get("name") != "Duel":
        return False

    duel_type = event.get("duel", {}).get("type", {}).get("name")

    return duel_type == "Tackle"


# check if a tackle is won
def is_tackle_won(event):
    if not is_tackle(event):
        return False

    outcome = event.get("duel", {}).get("outcome", {}).get("name")

    return outcome in {
        "Won",
        "Success In Play",
        "Success Out",
    }


# aggregate defending metrics for each player
def aggregate_defending(events):
    rows = {}
        # get all shot event ids
    shot_ids = {
        event.get("id")
        for event in events
        if event.get("type", {}).get("name") == "Shot"
    }

    for event in events:
        # only process tackles interceptions and blocks
        if not (
            is_tackle(event)
            or is_interception(event)
            or is_block(event)
        ):
            continue

        player = event.get("player") or {}
        team = event.get("team") or {}

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
                "tackles_attempted": 0,
                "tackles_won": 0,
                "interceptions_attempted": 0,
                "interceptions_won": 0,
                "total_blocks": 0,
                 "shot_blocks": 0,
            }

        # count tackles attempted for each player
        if is_tackle(event):
            rows[key]["tackles_attempted"] += 1

        # count tackles won for each player
        if is_tackle_won(event):
            rows[key]["tackles_won"] += 1

        # count interceptions attempted for each player
        if is_interception(event):
            rows[key]["interceptions_attempted"] += 1

        # count interceptions won for each player
        if is_interception_won(event):
            rows[key]["interceptions_won"] += 1

        # count total blocks for each player
        if is_block(event):
            rows[key]["total_blocks"] += 1
                # count shot blocks for each player
        if is_shot_block(event, shot_ids):
            rows[key]["shot_blocks"] += 1

    df = pd.DataFrame(
        list(rows.values()),
        columns=[
            "player_id",
            "player_name",
            "team_id",
            "team_name",
            "tackles_attempted",
            "tackles_won",
            "interceptions_attempted",
            "interceptions_won",
            "total_blocks",
            "shot_blocks",
        ],
    )

    # calculate tackle success rate for each player
    df["tackle_success_rate"] = (
        df["tackles_won"]
        .div(df["tackles_attempted"].replace(0, float("nan")))
        .mul(100)
        .fillna(0)
    )

    # calculate interception success rate for each player
    df["interception_success_rate"] = (
        df["interceptions_won"]
        .div(df["interceptions_attempted"].replace(0, float("nan")))
        .mul(100)
        .fillna(0)
    )

    return df

# check if an event is an interception
def is_interception(event):
    return event.get("type", {}).get("name") == "Interception"


# check if an interception is successful
def is_interception_won(event):
    if not is_interception(event):
        return False

    outcome = (
        event.get("interception", {})
        .get("outcome", {})
        .get("name")
    )

    return outcome in {
        "Won",
        "Success In Play",
        "Success Out",
    }

# check if an event is a block
def is_block(event):
    return event.get("type", {}).get("name") == "Block"


# check if a block is related to a shot
def is_shot_block(event, shot_ids):
    if not is_block(event):
        return False

    related_ids = event.get("related_events") or []

    return any(
        related_id in shot_ids
        for related_id in related_ids
    )
