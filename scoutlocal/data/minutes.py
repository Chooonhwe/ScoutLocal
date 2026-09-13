from __future__ import annotations

from collections import defaultdict
import pandas as pd


MATCH_MINUTES_FALLBACK = 90.0


def estimate_minutes_from_events(events: list[dict]) -> pd.DataFrame:
    """
    V0.1 minute estimator.

    For each player, estimate minutes using first and last event minute.
    This is deliberately transparent but approximate.

    Later versions should use lineup/substitution information for
    more accurate player minutes.
    """
    player_times = defaultdict(lambda: {"first": None, "last": None})

    for event in events:
        player = event.get("player")
        team = event.get("team")
        minute = event.get("minute")

        if not player or not team or minute is None:
            continue

        key = (player["id"], player["name"], team["name"])
        info = player_times[key]

        info["first"] = minute if info["first"] is None else min(info["first"], minute)
        info["last"] = minute if info["last"] is None else max(info["last"], minute)

    records = []

    for (player_id, player_name, team_name), info in player_times.items():
        if info["first"] is None or info["last"] is None:
            minutes = 0.0
        else:
            minutes = max(float(info["last"] - info["first"]), 1.0)

        records.append({
            "player_id": player_id,
            "player_name": player_name,
            "team_name": team_name,
            "minutes": minutes,
        })

    return pd.DataFrame(records)
