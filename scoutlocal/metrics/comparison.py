
import pandas as pd


# compare players using their player and team ids
def compare_players(df, player_selections, metrics):
    # check required columns
    required_columns = [
        "player_id",
        "team_id",
        "player_name",
        "team_name",
        "minutes",
    ]

    missing_columns = [
        column
        for column in required_columns + metrics
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # create a unique key for each player and team
    selected_keys = set(player_selections)

    # select matching player team records
    selected = df[
        [
            (player_id, team_id) in selected_keys
            for player_id, team_id in zip(
                df["player_id"],
                df["team_id"],
            )
        ]
    ].copy()

    if selected.empty:
        raise ValueError("No matching players found.")

    # keep player information and selected metrics
    columns = required_columns + metrics

    selected = selected[columns]

    # sort players by name and team
    selected = selected.sort_values(
        ["player_name", "team_name"]
    )

    return selected
