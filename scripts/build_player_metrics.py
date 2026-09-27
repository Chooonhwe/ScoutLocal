from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scoutlocal.data.statsbomb import StatsBombOpenData
from scoutlocal.data.minutes import calculate_minutes
from scoutlocal.metrics.player_metrics import (
    aggregate_events,
    add_per90_metrics,
)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--competition-id",
        type=int,
        required=True,
    )

    parser.add_argument(
        "--season-id",
        type=int,
        required=True,
    )

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

    # get all matches from the competition and season
    matches = client.matches(
        args.competition_id,
        args.season_id,
    )

    # only use a few matches when testing
    if args.max_matches:
        matches = matches[: args.max_matches]

    all_totals = []
    all_minutes = []

    print(f"Processing {len(matches)} matches...")

    # go through every match
    for index, match in enumerate(matches, start=1):
        match_id = match["match_id"]

        print(
            f"[{index}/{len(matches)}] "
            f"match_id={match_id}"
        )

        # get all events from the match
        events = client.events(match_id)

        # calculate player stats
        event_metrics = aggregate_events(events)

        # calculate how long each player played
        minute_metrics = calculate_minutes(events)

        if not event_metrics.empty:
            all_totals.append(event_metrics)

        if not minute_metrics.empty:
            all_minutes.append(minute_metrics)

    # stop if no player stats were found
    if not all_totals:
        raise RuntimeError(
            "No player event data was produced."
        )

    # combine player stats from every match
    totals = pd.concat(
        all_totals,
        ignore_index=True,
    )

    # add together each player's season totals
    totals = (
        totals
        .groupby(
            ["player_id", "player_name", "team_name"],
            as_index=False,
        )
        .sum(numeric_only=True)
    )

    # combine minutes from every match
    minutes = pd.concat(
        all_minutes,
        ignore_index=True,
    )

    # add together each player's total seconds
    minutes = (
        minutes
        .groupby(
            ["player_id", "player_name", "team_name"],
            as_index=False,
        )["seconds_played"]
        .sum()
    )

    # calculate decimal minutes from total seconds
    minutes["minutes"] = (
        minutes["seconds_played"] / 60
    )

    # make total playing time easier to read
    total_seconds = (
        minutes["seconds_played"]
        .round()
        .astype(int)
    )

    minutes["minutes_display"] = (
        (total_seconds // 60).astype(str)
        + ":"
        + (total_seconds % 60)
        .astype(str)
        .str.zfill(2)
    )

    # put player stats and minutes together
    players = totals.merge(
        minutes,
        on=[
            "player_id",
            "player_name",
            "team_name",
        ],
        how="left",
    )

    # protect against missing minutes
    players["minutes"] = (
        players["minutes"].fillna(0)
    )

    # calculate per 90 stats
    players = add_per90_metrics(players)

    # show players with the most minutes first
    players = players.sort_values(
        ["minutes", "player_name"],
        ascending=[False, True],
    )

    # create the data folder if needed
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    # save the final player dataset
    output_path = (
        output_dir / "player_metrics.csv"
    )

    players.to_csv(
        output_path,
        index=False,
    )

    print()
    print(f"Saved: {output_path}")
    print(f"Players: {len(players)}")
    print()

    print(
        players.head(15).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()