
import pandas as pd

from scoutlocal.metrics.rankings import (
    calculate_position_percentiles,
)


# load enriched player metrics
df = pd.read_csv("data/player_metrics_with_positions.csv")

# choose defensive metrics
metrics = [
    "tackles_won_per90",
    "interceptions_won_per90",
    "total_blocks_per90",
    "total_clearances_per90",
]

# calculate rankings within positions
ranked = calculate_position_percentiles(
    df,
    metrics,
    min_minutes=900,
)

print("\nPOSITIONAL RANKING VALIDATION\n")
print("Total eligible players:", len(ranked))

print("\nELIGIBLE PLAYERS BY POSITION\n")
print(
    ranked.groupby("primary_position_group")
    .size()
    .sort_values(ascending=False)
    .to_string()
)

# inspect our three test players
selected = ranked[
    ranked["player_id"].isin([
        124903,
        161099,
        20837,
    ])
]

columns = [
    "player_name",
    "primary_position_group",
    "position_peer_count",
    "tackles_won_per90_position_percentile",
    "interceptions_won_per90_position_percentile",
    "total_blocks_per90_position_percentile",
    "total_clearances_per90_position_percentile",
]

print("\nPLAYER POSITIONAL COMPARISON\n")
print(
    selected[columns].to_string(
        index=False,
        float_format=lambda value: f"{value:.2f}",
    )
)
