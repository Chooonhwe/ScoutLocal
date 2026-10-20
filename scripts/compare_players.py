
import pandas as pd

from scoutlocal.metrics.comparison import compare_players


# load season player data
df = pd.read_csv("data/player_metrics.csv")

# choose specific player and team records
player_selections = [
    (124903, 7289),  # akash mishra - hyderabad
    (20837, 7283),   # marko leskovic - kerala blasters
    (161099, 2021),  # ricky lallawmawma - jamshedpur
]

# choose comparison metrics
metrics = [
    "tackles_won_per90",
    "interceptions_won_per90",
    "total_blocks_per90",
    "total_clearances_per90",
]

# compare the selected players
comparison = compare_players(
    df,
    player_selections,
    metrics,
)

# display results to 2 decimal places
print("\nPLAYER COMPARISON TEST\n")

print(
    comparison.to_string(
        index=False,
        float_format=lambda value: f"{value:.2f}",
    )
)
