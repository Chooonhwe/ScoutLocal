from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scoutlocal.data import minutes
from scoutlocal.data.statsbomb import StatsBombOpenData
from scoutlocal.data.minutes import calculate_minutes
from scoutlocal.metrics.player_metrics import (
    aggregate_events,
    add_per90_metrics,
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--competition-id", type=int, required=True)
    parser.add_argument("--season-id", type=int, required=True)
    parser.add_argument(
        "--max-matches",
        type=int,
        default=None,
        help="Optional limit while testing.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    client = StatsBombOpenData()

    matches = client.matches(args.competition_id, args.season_id)

    if args.max_matches:
        matches = matches[: args.max_matches]

    all_totals = []
    all_minutes = []

    print(f"Processing {len(matches)} matches...")

    for index, match in enumerate(matches, start=1):
        match_id = match["match_id"]
        print(f"[{index}/{len(matches)}] match_id={match_id}")

        events = client.events(match_id)

        event_metrics = aggregate_events(events)
        minute_metrics = calculate_minutes(events)

        if not event_metrics.empty:
            all_totals.append(event_metrics)

        if not minute_metrics.empty:
            all_minutes.append(minute_metrics)

    if not all_totals:
        raise RuntimeError("No player event data was produced.")

    totals = pd.concat(all_totals, ignore_index=True)
    totals = (
        totals
        .groupby(["player_id", "player_name", "team_name"], as_index=False)
        .sum(numeric_only=True)
    )

    minutes = pd.concat(all_minutes, ignore_index=True)

    minutes = (
    minutes
    .groupby(
        ["player_id", "player_name", "team_name"],
        as_index=False,
    )
    ["seconds_played"]
    .sum()
    )

    # calculate decimal minutes from the total seconds
    minutes["minutes"] = minutes["seconds_played"] / 60

# make the total time easy to read
    total_seconds = minutes["seconds_played"].round().astype(int)

    minutes["minutes_display"] = (
      (total_seconds // 60).astype(str)
     + ":"
     + (total_seconds % 60).astype(str).str.zfill(2)
    )


    players = totals.merge(
        minutes,
        on=["player_id", "player_name", "team_name"],
        how="left",
    )

    players["minutes"] = players["minutes"].fillna(0)
    players = add_per90_metrics(players)

    players = players.sort_values(
        ["minutes", "player_name"],
        ascending=[False, True],
    )

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    output_path = output_dir / "player_metrics.csv"
    players.to_csv(output_path, index=False)

    print()
    print(f"Saved: {output_path}")
    print(f"Players: {len(players)}")
    print()
    print(players.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
