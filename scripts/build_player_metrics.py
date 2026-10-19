
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
from scoutlocal.metrics.passing import aggregate_passing
from scoutlocal.metrics.carrying import aggregate_carrying
from scoutlocal.metrics.shooting import aggregate_shooting
from scoutlocal.metrics.defending import aggregate_defending

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
    all_passing = []
    all_carrying = []
    all_shooting = []
    all_defending = []
    all_minutes = []

    # map players to their teams
    team_lookup = {}

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

        # get team ids from player events
        for event in events:
            player = event.get("player") or {}
            team = event.get("team") or {}

            player_id = player.get("id")
            team_id = team.get("id")
            team_name = team.get("name")

            if team_id is None or team_name is None:
                continue

            if player_id is not None:
                team_lookup[(player_id, team_name)] = team_id

            # get team ids from starting lineups
            if event.get("type", {}).get("name") == "Starting XI":
                lineup = event.get("tactics", {}).get("lineup", [])

                for lineup_player in lineup:
                    lineup_id = (
                        lineup_player.get("player", {}).get("id")
                    )

                    if lineup_id is not None:
                        team_lookup[(lineup_id, team_name)] = team_id

            # get team ids from substitutions
            if event.get("type", {}).get("name") == "Substitution":
                replacement = (
                    event.get("substitution", {})
                    .get("replacement", {})
                )

                replacement_id = replacement.get("id")

                if replacement_id is not None:
                    team_lookup[(replacement_id, team_name)] = team_id

        # calculate player stats
        event_metrics = aggregate_events(events)

        # calculate passing stats
        passing_metrics = aggregate_passing(events)

        # calculate carrying stats
        carrying_metrics = aggregate_carrying(events)

        # calculate shooting stats
        shooting_metrics = aggregate_shooting(events)

        # calculate defending stats
        defending_metrics = aggregate_defending(events)

        # calculate how long each player played
        minute_metrics = calculate_minutes(events)

        if not event_metrics.empty:
            all_totals.append(event_metrics)

        if not passing_metrics.empty:
            all_passing.append(passing_metrics)

        if not carrying_metrics.empty:
            all_carrying.append(carrying_metrics)

        if not shooting_metrics.empty:
            all_shooting.append(shooting_metrics)

        if not defending_metrics.empty:
            all_defending.append(defending_metrics)

        if not minute_metrics.empty:
            all_minutes.append(minute_metrics)

    # stop if no player stats were found
    if not all_totals:
        raise RuntimeError(
            "No player event data was produced."
        )

    # stop if no passing stats were found
    if not all_passing:
        raise RuntimeError(
            "No player passing data was produced."
        )

    # stop if no carrying stats were found
    if not all_carrying:
        raise RuntimeError(
            "No player carrying data was produced."
        )

    # stop if no player minutes were found
    if not all_minutes:
        raise RuntimeError(
            "No player minutes data was produced."
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

    # combine passing stats from every match
    passing_totals = pd.concat(
        all_passing,
        ignore_index=True,
    )

    passing_totals = (
        passing_totals
        .groupby(
            ["player_id", "player_name", "team_name"],
            as_index=False,
        )
        .sum(numeric_only=True)
    )

    # combine carrying stats from every match
    carrying_totals = pd.concat(
        all_carrying,
        ignore_index=True,
    )

    carrying_totals = (
        carrying_totals
        .groupby(
            ["player_id", "player_name", "team_name"],
            as_index=False,
        )
        .sum(numeric_only=True)
    )

    # combine shooting stats from every match
    if all_shooting:
        shooting_totals = pd.concat(
            all_shooting,
            ignore_index=True,
        )

        # remove match level percentages before combining
        shooting_totals = shooting_totals.drop(
            columns=[
                "shooting_accuracy",
                "goal_conversion_rate",
                "xg_per_shot",
                "goals_minus_xg",
                "non_penalty_goals_minus_xg",
            ],
            errors="ignore",
        )

        # add together each player's shooting totals
        shooting_totals = (
            shooting_totals
            .groupby(
                ["player_id", "player_name", "team_name"],
                as_index=False,
            )
            .sum(numeric_only=True)
        )
    else:
        shooting_totals = pd.DataFrame(
            columns=[
                "player_id",
                "player_name",
                "team_name",
            ]
        )

    
    # combine defending stats from every match
    if all_defending:
        defending_totals = pd.concat(
            all_defending,
            ignore_index=True,
        )

        # remove match level percentages before combining
        defending_totals = defending_totals.drop(
            columns=[
                "tackle_success_rate",
                "interception_success_rate",
            ],
            errors="ignore",
        )

        # add together each player's defending totals
        defending_totals = (
            defending_totals
            .groupby(
                ["player_id", "player_name", "team_name"],
                as_index=False,
            )
            .sum(numeric_only=True)
        )
    else:
        defending_totals = pd.DataFrame(
            columns=[
                "player_id",
                "player_name",
                "team_name",
            ]
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

    # start with everyone who played
    players = minutes.merge(
        totals,
        on=[
            "player_id",
            "player_name",
            "team_name",
        ],
        how="left",
    )

    # remove passing stats we already have
    passing_totals = passing_totals.drop(
        columns=[
            "passes",
            "completed_passes",
        ],
    )

    # add detailed passing stats
    players = players.merge(
        passing_totals,
        on=[
            "player_id",
            "player_name",
            "team_name",
        ],
        how="left",
    )

    # remove carries we already have
    carrying_totals = carrying_totals.drop(
        columns=["carries"],
    )

    # add detailed carrying stats
    players = players.merge(
        carrying_totals,
        on=[
            "player_id",
            "player_name",
            "team_name",
        ],
        how="left",
    )

    # validate shooting totals against basic metrics
    print("\nSHOOTING DATA VALIDATION")

    print(
        "Basic total shots:",
        int(totals["shots"].sum())
    )

    print(
        "Shooting total shots:",
        int(shooting_totals["total_shots"].sum()) if all_shooting else 0
    )

    print(
        "Basic total xg:",
        round(totals["xg"].sum(), 2)
    )

    print(
        "Shooting total xg:",
        round(shooting_totals["total_xg"].sum(), 2) if all_shooting else 0.0
    )

    # remove shooting stats already in basic metrics
    shooting_totals = shooting_totals.drop(
        columns=[
            "total_shots",
            "total_xg",
            "team_id",
        ],
        errors="ignore",
    )

    # add detailed shooting stats
    players = players.merge(
        shooting_totals,
        on=[
            "player_id",
            "player_name",
            "team_name",
        ],
        how="left",
    )


    # remove defending stats already in basic metrics
    defending_totals = defending_totals.drop(
        columns=[
            "team_id",
        ],
        errors="ignore",
    )

    # add detailed defending stats
    players = players.merge(
        defending_totals,
        on=[
            "player_id",
            "player_name",
            "team_name",
        ],
        how="left",
    )

    # add team id for every player
    players["team_id"] = [
        team_lookup.get((row.player_id, row.team_name))
        for row in players.itertuples(index=False)
    ]

    # check for missing team ids
    missing_team_ids = int(players["team_id"].isna().sum())

    print(
        "Missing team ids:",
        missing_team_ids
    )

    if missing_team_ids:
        print(
            players.loc[
                players["team_id"].isna(),
                ["player_id", "player_name", "team_name"],
            ].to_string(index=False)
        )

    # players with no recorded stats should have 0
    stat_columns = [
        "passes",
        "completed_passes",
        "shots",
        "carries",
        "pressures",
        "interceptions",
        "ball_recoveries",
        "xg",
        "forward_passes",
        "completed_forward_passes",
        "final_third_passes",
        "completed_final_third_passes",
        "final_third_entries",
        "completed_final_third_entries",
        "progressive_passes",
        "completed_progressive_passes",
        "penalty_box_entries",
        "completed_penalty_box_entries",
        "long_passes",
        "completed_long_passes",
        "crosses",
        "completed_crosses",
        "shot_assists",
        "goal_assists",
        "key_passes",
        "forward_carries",
        "progressive_carries",
        "final_third_carry_entries",
        "penalty_box_carry_entries",
        "carry_distance",
        "forward_carry_distance",
        "shots_on_target",
        "goals",
        "non_penalty_goals",
        "shots_inside_box",
        "non_penalty_xg",
        "headed_shots",
        "left_footed_shots",
        "right_footed_shots",
        "other_shots",
        "tackles_attempted",
        "tackles_won",
        "interceptions_attempted",
        "interceptions_won",
        "total_blocks",
        "shot_blocks",
        "total_clearances",
        "headed_clearances",
        "left_footed_clearances",
        "right_footed_clearances",
        "other_clearances",

    ]

    # add missing stat columns as 0
    for column in stat_columns:
        if column not in players.columns:
            players[column] = 0.0

    players[stat_columns] = (
        players[stat_columns].fillna(0)
    )

    # calculate season shooting accuracy
    players["shooting_accuracy"] = (
        players["shots_on_target"]
        .div(players["shots"].replace(0, float("nan")))
        .mul(100)
        .fillna(0)
        .round(2)
    )

    # calculate season goal conversion rate
    players["goal_conversion_rate"] = (
        players["goals"]
        .div(players["shots"].replace(0, float("nan")))
        .mul(100)
        .fillna(0)
        .round(2)
    )

    # calculate season xg per shot
    players["xg_per_shot"] = (
        players["xg"]
        .div(players["shots"].replace(0, float("nan")))
        .fillna(0)
        .round(2)
    )

    # calculate season goals minus xg
    players["goals_minus_xg"] = (
        players["goals"] - players["xg"]
    ).round(2)

    # calculate season non penalty goals minus xg
    players["non_penalty_goals_minus_xg"] = (
        players["non_penalty_goals"]
        - players["non_penalty_xg"]
    ).round(2)

    # validate shooting body part totals
    body_part_shots = (
        players["headed_shots"]
        + players["left_footed_shots"]
        + players["right_footed_shots"]
        + players["other_shots"]
    )

    print(
        "Total shots:",
        int(players["shots"].sum())
    )

    print(
        "Body part shots:",
        int(body_part_shots.sum())
    )

    print(
        "Other shots:",
        int(players["other_shots"].sum())
    )

    print(
        "Total non penalty xg:",
        round(players["non_penalty_xg"].sum(), 2)
    )

    # calculate season tackle success rate
    players["tackle_success_rate"] = (
        players["tackles_won"]
        .div(players["tackles_attempted"].replace(0, float("nan")))
        .mul(100)
        .fillna(0)
    )

    # calculate season interception success rate
    players["interception_success_rate"] = (
        players["interceptions_won"]
        .div(players["interceptions_attempted"].replace(0, float("nan")))
        .mul(100)
        .fillna(0)
    )

    # validate defending totals
    print("\nDEFENDING DATA VALIDATION")

    print("Tackles attempted:", int(players["tackles_attempted"].sum()))
    print("Tackles won:", int(players["tackles_won"].sum()))
    print("Interceptions attempted:", int(players["interceptions_attempted"].sum()))
    print("Interceptions won:", int(players["interceptions_won"].sum()))
    print("Total blocks:", int(players["total_blocks"].sum()))
    print("Shot blocks:", int(players["shot_blocks"].sum()))
    print("Total clearances:", int(players["total_clearances"].sum()))

    # validate all clearance body parts
    clearance_body_parts = (
        players["headed_clearances"]
        + players["left_footed_clearances"]
        + players["right_footed_clearances"]
        + players["other_clearances"]
    )

    print("Clearance body part total:", int(clearance_body_parts.sum()))

    assert (
        players["total_clearances"].sum()
        == clearance_body_parts.sum()
    ), "Clearance body part totals do not match"



    # calculate per 90 stats
    players = add_per90_metrics(players)

    # calculate defending stats per 90 minutes
    defending_per90_columns = [
        "tackles_attempted",
        "tackles_won",
        "interceptions_attempted",
        "interceptions_won",
        "total_blocks",
        "shot_blocks",
        "total_clearances",
        "headed_clearances",
        "left_footed_clearances",
        "right_footed_clearances",
        "other_clearances",
    ]

    for column in defending_per90_columns:
        players[f"{column}_per90"] = (
            players[column]
            .div(players["minutes"].replace(0, float("nan")))
            .mul(90)
            .fillna(0)
        )


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
