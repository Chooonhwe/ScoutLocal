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


# pass completion should stay between 0 and 100
print("\nPASS COMPLETION CHECK")

bad_completion = df[
    (df["pass_completion_pct"] < 0)
    | (df["pass_completion_pct"] > 100)
]

if bad_completion.empty:
    print("All pass completion values are valid")
else:
    print(
        bad_completion[
            ["player_name", "pass_completion_pct"]
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