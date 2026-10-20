
import pandas as pd

from scoutlocal.metrics.rankings import calculate_percentiles


# load player data
df = pd.read_csv("data/player_metrics.csv")

# choose defensive metrics
metrics = [
    "tackles_won_per90",
    "interceptions_won_per90",
    "total_blocks_per90",
    "total_clearances_per90",
]

# calculate percentiles
ranked = calculate_percentiles(
    df,
    metrics,
    min_minutes=900,
)

# select players for testing
selected = ranked[
    ranked["player_id"].isin([
        124903,
        20837,
        161099,
    ])
]

# show percentile rankings
columns = [
    "player_name",
    "team_name",
    "minutes",
] + [
    f"{metric}_percentile"
    for metric in metrics
]

print("\nPLAYER PERCENTILE TEST\n")
print("Eligible players:", len(ranked))

print(
    selected[columns].to_string(
        index=False,
        float_format=lambda value: f"{value:.2f}",
    )
)
