
import argparse
import pandas as pd


# accept a player name from the terminal
parser = argparse.ArgumentParser(
    description="Search ScoutLocal players by name"
)

parser.add_argument(
    "name",
    type=str,
    help="Player name or part of a name",
)

args = parser.parse_args()


# load the season player dataset
df = pd.read_csv(
    "data/player_metrics_with_positions.csv"
)

# search player names without case sensitivity
matches = df[
    df["player_name"].str.contains(
        args.name,
        case=False,
        na=False,
        regex=False,
    )
].copy()


# display matching players
print("\nSCOUTLOCAL PLAYER SEARCH\n")

if matches.empty:
    print(f"No players found matching '{args.name}'.")

else:
    # make missing positions easier to understand
    matches["primary_position_group"] = (
        matches["primary_position_group"].fillna("Unknown")
    )

    matches = matches.sort_values(
        "minutes",
        ascending=False,
    )

    columns = [
        "player_id",
        "player_name",
        "team_name",
        "primary_position_group",
        "minutes",
    ]

    print(
        matches[columns].to_string(
            index=False,
            float_format=lambda value: f"{value:.2f}",
        )
    )

    print("\nTotal matches:", len(matches))
