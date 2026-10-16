
import pandas as pd


# load the player data we just made
df = pd.read_csv("data/player_metrics.csv")


print("PLAYERS")
print(len(df))


# check if anyone has weird minutes
print("\nMINUTES CHECK")

print("Lowest minutes:", df["minutes"].min())
print("Highest minutes:", df["minutes"].max())

print("\nPLAYERS WITH 0 OR NEGATIVE MINUTES")

bad_minutes = df[df["minutes"] <= 0]

if bad_minutes.empty:
    print("None")
else:
    print(
        bad_minutes[
            ["player_name", "team_name", "minutes"]
        ].to_string(index=False)
    )


# check if any stats somehow became negative
print("\nNEGATIVE STATS CHECK")

stat_columns = [
    "passes",
    "completed_passes",
    "pressures",
    "carries",
    "ball_recoveries",
    "shots",
    "xg",
    "interceptions",
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
]

for column in stat_columns:
    negative_count = (df[column] < 0).sum()
    print(f"{column}: {negative_count}")


# completed passes should never be more than passes
print("\nPASS CHECK")

bad_passes = df[
    df["completed_passes"] > df["passes"]
]

if bad_passes.empty:
    print("No impossible pass totals")
else:
    print(
        bad_passes[
            [
                "player_name",
                "passes",
                "completed_passes",
            ]
        ].to_string(index=False)
    )


# completed passing stats should never be more than attempts
print("\nDETAILED PASS CHECK")

passing_checks = [
    (
        "forward_passes",
        "completed_forward_passes",
    ),
    (
        "final_third_passes",
        "completed_final_third_passes",
    ),
    (
        "final_third_entries",
        "completed_final_third_entries",
    ),
    (
        "progressive_passes",
        "completed_progressive_passes",
    ),
    (
        "penalty_box_entries",
        "completed_penalty_box_entries",
    ),
    (
        "long_passes",
        "completed_long_passes",
    ),
    (
        "crosses",
        "completed_crosses",
    ),
]

for attempts, completed in passing_checks:
    bad = df[
        df[completed] > df[attempts]
    ]

    if bad.empty:
        print(f"{completed}: valid")
    else:
        print(f"{completed}: INVALID")

        print(
            bad[
                [
                    "player_name",
                    attempts,
                    completed,
                ]
            ].to_string(index=False)
        )


# pass completion should stay between 0 and 100
print("\nPASS COMPLETION CHECK")

completion_columns = [
    "pass_completion_pct",
    "forward_pass_completion_pct",
    "final_third_pass_completion_pct",
    "final_third_entry_completion_pct",
    "progressive_pass_completion_pct",
    "penalty_box_entry_completion_pct",
    "long_pass_completion_pct",
    "cross_completion_pct",
]

for column in completion_columns:
    bad_completion = df[
        (df[column] < 0)
        | (df[column] > 100)
    ]

    if bad_completion.empty:
        print(f"{column}: valid")
    else:
        print(f"{column}: INVALID")

        print(
            bad_completion[
                [
                    "player_name",
                    column,
                ]
            ].to_string(index=False)
        )


# key passes should equal shot assists and goal assists
print("\nKEY PASS CHECK")

bad_key_passes = df[
    df["key_passes"]
    != (
        df["shot_assists"]
        + df["goal_assists"]
    )
]

if bad_key_passes.empty:
    print("All key pass totals are valid")
else:
    print(
        bad_key_passes[
            [
                "player_name",
                "shot_assists",
                "goal_assists",
                "key_passes",
            ]
        ].to_string(index=False)
    )


# check the players with the most minutes
print("\nTOP 20 PLAYERS BY MINUTES")

top_minutes = df.sort_values(
    "seconds_played",
    ascending=False,
).head(20)

print(
    top_minutes[
        [
            "player_name",
            "team_name",
            "minutes_display",
        ]
    ].to_string(index=False)
)


# check the players with the least minutes
print("\nBOTTOM 20 PLAYERS BY MINUTES")

bottom_minutes = df.sort_values(
    "seconds_played",
    ascending=True,
).head(20)

print(
    bottom_minutes[
        [
            "player_name",
            "team_name",
            "minutes_display",
        ]
    ].to_string(index=False)
)


# check carrying stats
print("\nCARRYING CHECK")

carrying_checks = [
    "forward_carries",
    "progressive_carries",
    "final_third_carry_entries",
    "penalty_box_carry_entries",
]

for column in carrying_checks:
    bad = df[df[column] > df["carries"]]

    if bad.empty:
        print(f"{column}: valid")
    else:
        print(f"{column}: INVALID")


# check carrying distance
print("\nCARRY DISTANCE CHECK")

bad_distance = df[
    (df["carry_distance"] < 0)
    | (df["forward_carry_distance"] < 0)
    | (
        df["forward_carry_distance"]
        > df["carry_distance"] + 0.000001
    )
]

if bad_distance.empty:
    print("Carry distances: valid")
else:
    print("Carry distances: INVALID")
    print(
        bad_distance[
            [
                "player_name",
                "carry_distance",
                "forward_carry_distance",
            ]
        ].to_string(index=False)
    )


# check if all shots have a body part
print("\nSHOOTING BODY PART CHECK")

body_part_shots = (
    df["headed_shots"]
    + df["left_footed_shots"]
    + df["right_footed_shots"]
    + df["other_shots"]
)

print("Total shots:", int(df["shots"].sum()))
print("Body part shots:", int(body_part_shots.sum()))
print("Other shots:", int(df["other_shots"].sum()))

bad_body_parts = df[
    body_part_shots != df["shots"]
]

if bad_body_parts.empty:
    print("All shooting body part totals are valid")
else:
    print("Shooting body part totals: INVALID")

    print(
        bad_body_parts[
            [
                "player_name",
                "team_name",
                "shots",
                "headed_shots",
                "left_footed_shots",
                "right_footed_shots",
                "other_shots",
            ]
        ].to_string(index=False)
    )


# check shooting counts
print("\nSHOOTING COUNT CHECK")

shooting_checks = [
    ("shots_on_target", "shots"),
    ("goals", "shots_on_target"),
    ("non_penalty_goals", "goals"),
    ("shots_inside_box", "shots"),
    ("headed_shots", "shots"),
    ("left_footed_shots", "shots"),
    ("right_footed_shots", "shots"),
    ("other_shots", "shots"),
]

for count_column, total_column in shooting_checks:
    bad = df[
        df[count_column] > df[total_column]
    ]

    if bad.empty:
        print(f"{count_column}: valid")
    else:
        print(f"{count_column}: INVALID")

        print(
            bad[
                [
                    "player_name",
                    count_column,
                    total_column,
                ]
            ].to_string(index=False)
        )


# check non penalty xg
print("\nNON PENALTY XG CHECK")

bad_non_penalty_xg = df[
    df["non_penalty_xg"] > df["xg"] + 0.000001
]

if bad_non_penalty_xg.empty:
    print("Non penalty xg: valid")
else:
    print("Non penalty xg: INVALID")

    print(
        bad_non_penalty_xg[
            [
                "player_name",
                "xg",
                "non_penalty_xg",
            ]
        ].to_string(index=False)
    )


# check shooting accuracy
print("\nSHOOTING ACCURACY CHECK")

expected_accuracy = (
    df["shots_on_target"]
    .div(df["shots"].replace(0, float("nan")))
    .mul(100)
    .fillna(0)
)

bad_accuracy = df[
    (df["shooting_accuracy"] - expected_accuracy).abs() > 0.011
]

if bad_accuracy.empty:
    print("Shooting accuracy: valid")
else:
    print("Shooting accuracy: INVALID")


# check goal conversion rate
print("\nGOAL CONVERSION CHECK")

expected_conversion = (
    df["goals"]
    .div(df["shots"].replace(0, float("nan")))
    .mul(100)
    .fillna(0)
)

bad_conversion = df[
    (df["goal_conversion_rate"] - expected_conversion).abs() > 0.011
]

if bad_conversion.empty:
    print("Goal conversion rate: valid")
else:
    print("Goal conversion rate: INVALID")


# check xg per shot
print("\nXG PER SHOT CHECK")

expected_xg_per_shot = (
    df["xg"]
    .div(df["shots"].replace(0, float("nan")))
    .fillna(0)
)

bad_xg_per_shot = df[
    (df["xg_per_shot"] - expected_xg_per_shot).abs() > 0.011
]

if bad_xg_per_shot.empty:
    print("Xg per shot: valid")
else:
    print("Xg per shot: INVALID")


# check goals minus xg
print("\nGOALS MINUS XG CHECK")

expected_goals_minus_xg = (
    df["goals"] - df["xg"]
)

bad_goals_minus_xg = df[
    (df["goals_minus_xg"] - expected_goals_minus_xg).abs() > 0.011
]

if bad_goals_minus_xg.empty:
    print("Goals minus xg: valid")
else:
    print("Goals minus xg: INVALID")


# check non penalty goals minus xg
print("\nNON PENALTY GOALS MINUS XG CHECK")

expected_non_penalty_difference = (
    df["non_penalty_goals"] - df["non_penalty_xg"]
)

bad_non_penalty_difference = df[
    (
        df["non_penalty_goals_minus_xg"]
        - expected_non_penalty_difference
    ).abs() > 0.011
]

if bad_non_penalty_difference.empty:
    print("Non penalty goals minus xg: valid")
else:
    print("Non penalty goals minus xg: INVALID")


# check missing team ids
print("\nTEAM ID CHECK")

missing_team_ids = df["team_id"].isna().sum()

print("Missing team ids:", missing_team_ids)

if missing_team_ids == 0:
    print("All team ids: valid")
else:
    print("Team ids: INVALID")

    print(
        df.loc[
            df["team_id"].isna(),
            ["player_id", "player_name", "team_name"],
        ].to_string(index=False)
    )
