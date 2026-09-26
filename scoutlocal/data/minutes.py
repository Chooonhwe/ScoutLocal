from __future__ import annotations

from collections import defaultdict
import pandas as pd


MATCH_MINUTES_FALLBACK = 90.0


# change the event time into seconds
def _event_time_seconds(event: dict) -> float:
    minute = event.get("minute", 0)
    second = event.get("second", 0)

    return float(minute * 60 + second)


# make the time easier to read like 96:49
def _format_minutes(seconds: float) -> str:
    total_seconds = round(seconds)

    minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60

    return f"{minutes}:{remaining_seconds:02d}"


# find when the match ended
def _match_end_seconds(events: list[dict]) -> float:
    half_end_times = []

    for event in events:
        if event.get("type", {}).get("name") == "Half End":
            half_end_times.append(_event_time_seconds(event))

    if half_end_times:
        return max(half_end_times)

    return MATCH_MINUTES_FALLBACK * 60


# get all the starting players
def _get_starters(events: list[dict]) -> dict:
    starters = {}

    for event in events:
        if event.get("type", {}).get("name") != "Starting XI":
            continue

        team = event.get("team")
        lineup = event.get("tactics", {}).get("lineup", [])

        if not team:
            continue

        for lineup_player in lineup:
            player = lineup_player.get("player")

            if not player:
                continue

            key = (
                player["id"],
                player["name"],
                team["name"],
            )

            starters[key] = 0.0

    return starters


# get who went out, who came in and when
def _get_substitutions(events: list[dict]) -> list[dict]:
    substitutions = []

    for event in events:
        if event.get("type", {}).get("name") != "Substitution":
            continue

        player = event.get("player")
        team = event.get("team")
        replacement = event.get("substitution", {}).get("replacement")

        if not player or not team or not replacement:
            continue

        substitutions.append({
            "team_name": team["name"],
            "player_id": player["id"],
            "player_name": player["name"],
            "replacement_id": replacement["id"],
            "replacement_name": replacement["name"],
            "time_seconds": _event_time_seconds(event),
        })

    return substitutions


# calculate how long every player played
def calculate_minutes(events: list[dict]) -> pd.DataFrame:
    match_end = _match_end_seconds(events)
    starters = _get_starters(events)
    substitutions = _get_substitutions(events)

    player_times = {}

    # starters begin from the start of the match
    for key, start_time in starters.items():
        player_times[key] = {
            "start": start_time,
            "end": match_end,
        }

    # change the times when substitutions happen
    for substitution in substitutions:
        team_name = substitution["team_name"]
        substitution_time = substitution["time_seconds"]

        outgoing_key = (
            substitution["player_id"],
            substitution["player_name"],
            team_name,
        )

        replacement_key = (
            substitution["replacement_id"],
            substitution["replacement_name"],
            team_name,
        )

        # outgoing player stops here
        if outgoing_key in player_times:
            player_times[outgoing_key]["end"] = substitution_time

        # replacement starts here
        player_times[replacement_key] = {
            "start": substitution_time,
            "end": match_end,
        }

    records = []

    for (player_id, player_name, team_name), times in player_times.items():
        seconds_played = times["end"] - times["start"]
        minutes = seconds_played / 60

        records.append({
            "player_id": player_id,
            "player_name": player_name,
            "team_name": team_name,
            "seconds_played": seconds_played,
            "minutes": minutes,
            "minutes_display": _format_minutes(seconds_played),
        })

    return pd.DataFrame(records)


# old method kept here for now
def estimate_minutes_from_events(events: list[dict]) -> pd.DataFrame:
    player_times = defaultdict(lambda: {"first": None, "last": None})

    for event in events:
        player = event.get("player")
        team = event.get("team")
        minute = event.get("minute")

        if not player or not team or minute is None:
            continue

        key = (
            player["id"],
            player["name"],
            team["name"],
        )

        info = player_times[key]

        info["first"] = (
            minute
            if info["first"] is None
            else min(info["first"], minute)
        )

        info["last"] = (
            minute
            if info["last"] is None
            else max(info["last"], minute)
        )

    records = []

    for (player_id, player_name, team_name), info in player_times.items():
        if info["first"] is None or info["last"] is None:
            minutes = 0.0
        else:
            minutes = max(
                float(info["last"] - info["first"]),
                1.0,
            )

        records.append({
            "player_id": player_id,
            "player_name": player_name,
            "team_name": team_name,
            "minutes": minutes,
        })

    return pd.DataFrame(records)