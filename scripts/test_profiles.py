
import pandas as pd

from scoutlocal.metrics.profiles import get_profile_metrics
from scoutlocal.metrics.rankings import (
    calculate_position_percentiles,
)


# load players with positions
df = pd.read_csv("data/player_metrics_with_positions.csv")

# choose one scouting role
position_group = "Full Back"

# get metrics for the selected role
metrics = get_profile_metrics(position_group)

# rank eligible players
ranked = calculate_position_percentiles(
    df,
    metrics,
    min_minutes=900,
)

# select full backs only
full_backs = ranked[
    ranked["primary_position_group"] == position_group
]

# display chosen player comparisons
selected = full_backs[
    full_backs["player_id"].isin([
        124903,
        161099,
    ])
]

columns = [
    "player_name",
    "team_name",
] + [
    f"{metric}_position_percentile"
    for metric in metrics
]

print("\nFULL BACK SCOUTING PROFILE TEST\n")
print("Eligible full backs:", len(full_backs))

print(
    selected[columns].to_string(
        index=False,
        float_format=lambda value: f"{value:.2f}",
    )
)
