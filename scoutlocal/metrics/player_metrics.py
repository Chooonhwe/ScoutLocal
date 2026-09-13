from __future__ import annotations

from collections import defaultdict
import pandas as pd


COUNTABLE_EVENTS = {
    "Pass": "passes",
    "Shot": "shots",
    "Carry": "carries",
    "Pressure": "pressures",
    "Interception": "interceptions",
    "Ball Recovery": "ball_recoveries",
}


def _player_key(event: dict):
    player = event.get("player")
    team = event.get("team")

    if not player or not team:
        return None

    return (
        player["id"],
        player["name"],
        team["name"],
    )


def aggregate_events(events: list[dict]) -> pd.DataFrame:
    """
    Aggregate a list of StatsBomb match events into player-level totals.

    V0.1 intentionally uses simple event counts.
    More advanced possession-adjusted / role-aware metrics come later.
    """
    rows = defaultdict(lambda: defaultdict(float))

    for event in events:
        key = _player_key(event)
        if key is None:
            continue

        player_id, player_name, team_name = key
        row = rows[key]

        row["player_id"] = player_id
        row["player_name"] = player_name
        row["team_name"] = team_name

        event_type = event.get("type", {}).get("name")

        if event_type in COUNTABLE_EVENTS:
            row[COUNTABLE_EVENTS[event_type]] += 1

        if event_type == "Pass":
            outcome = event.get("pass", {}).get("outcome")
            if outcome is None:
                row["completed_passes"] += 1

        if event_type == "Shot":
            xg = event.get("shot", {}).get("statsbomb_xg")
            if xg is not None:
                row["xg"] += float(xg)

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows.values()).fillna(0)

    numeric_defaults = [
        "passes",
        "completed_passes",
        "shots",
        "carries",
        "pressures",
        "interceptions",
        "ball_recoveries",
        "xg",
    ]

    for column in numeric_defaults:
        if column not in df.columns:
            df[column] = 0

    return df


def add_per90_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add basic per-90 metrics.

    Requires a 'minutes' column. Players with zero minutes are protected
    from division-by-zero and receive 0 for per-90 values.
    """
    df = df.copy()

    if "minutes" not in df.columns:
        raise ValueError("Dataframe must contain a 'minutes' column.")

    denominator = df["minutes"].replace(0, pd.NA)

    source_columns = [
        "passes",
        "completed_passes",
        "shots",
        "carries",
        "pressures",
        "interceptions",
        "ball_recoveries",
        "xg",
    ]

    for column in source_columns:
        df[f"{column}_per90"] = (
            df[column] / denominator * 90
        ).fillna(0)

    df["pass_completion_pct"] = (
        df["completed_passes"]
        / df["passes"].replace(0, pd.NA)
        * 100
    ).fillna(0)

    return df
