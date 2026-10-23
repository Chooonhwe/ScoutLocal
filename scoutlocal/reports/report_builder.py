
import pandas as pd

from scoutlocal.metrics.profiles import get_profile_metrics
from scoutlocal.metrics.rankings import calculate_position_percentiles
from scoutlocal.reports.scouting_report import (
    generate_scouting_report,
    generate_scouting_observations,
)


# build a scouting report directly from the player dataset
def build_player_report(player_id, min_minutes=900):
    # load season metrics and player positions
    df = pd.read_csv(
        "data/player_metrics_with_positions.csv"
    )

    # find the selected player
    matches = df[df["player_id"] == player_id]

    if matches.empty:
        raise ValueError(
            f"Player ID {player_id} not found."
        )

    # player ids may occur for multiple teams
    if len(matches) > 1:
        raise ValueError(
            f"Player ID {player_id} has multiple team records. "
            "Team selection is required."
        )

    player = matches.iloc[0]
    position = player["primary_position_group"]

    # check whether a scouting profile exists
    metrics = get_profile_metrics(position)

    # rank against eligible positional peers
    ranked = calculate_position_percentiles(
        df,
        metrics,
        min_minutes=min_minutes,
    )

    selected = ranked[
        ranked["player_id"] == player_id
    ]

    if selected.empty:
        raise ValueError(
            f"Player ID {player_id} is not eligible. "
            f"Minimum minutes: {min_minutes}."
        )

    # generate the player's full scouting report
    report = generate_scouting_report(
        selected.iloc[0],
        metrics,
    )

    report["observations"] = (
        generate_scouting_observations(report)
    )

    return report


# find a unique player id using a name
def find_player_id(player_name):
    # load player records
    df = pd.read_csv(
        "data/player_metrics_with_positions.csv"
    )

    # find an exact match without case sensitivity
    matches = df[
        df["player_name"].str.casefold()
        == player_name.strip().casefold()
    ]

    if matches.empty:
        raise ValueError(
            f"No player found named '{player_name}'. "
            "Use scripts/search_players.py to search."
        )

    # reject ambiguous names
    if len(matches) > 1:
        raise ValueError(
            f"Multiple records found for '{player_name}'. "
            "Use a player ID instead."
        )

    return int(matches.iloc[0]["player_id"])
