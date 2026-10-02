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