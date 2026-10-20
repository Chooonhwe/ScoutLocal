
import pandas as pd

from scoutlocal.metrics.profiles import get_profile_metrics
from scoutlocal.metrics.rankings import calculate_position_percentiles
from scoutlocal.reports.scouting_report import (
    generate_scouting_report,
    generate_scouting_observations,
)
import json
from pathlib import Path


# load position enriched metrics
df = pd.read_csv("data/player_metrics_with_positions.csv")

# choose full back scouting metrics
metrics = get_profile_metrics("Full Back")

# calculate positional rankings
ranked = calculate_position_percentiles(
    df,
    metrics,
    min_minutes=900,
)

# generate reports for two full backs
for player_id in [124903, 161099]:
    player = ranked.loc[ranked["player_id"] == player_id].iloc[0]

    report = generate_scouting_report(player, metrics)

    print("\n" + "=" * 50)
    print("SCOUTLOCAL PLAYER REPORT")
    print("=" * 50)

    print("Player:", report["player_name"])
    print("Team:", report["team_name"])
    print("Position:", report["position"])
    print("Minutes:", f'{report["minutes"]:.2f}')
    print("Eligible peers:", report["peer_count"])

    print("\nHIGHEST PERCENTILE METRICS")
    for item in report["strongest_metrics"]:
        print(
            item["metric"],
            f'{item["percentile"]:.2f}',
        )

    print("\nLOWEST PERCENTILE METRICS")
    for item in report["lowest_metrics"]:
        print(
            item["metric"],
            f'{item["percentile"]:.2f}',
        )


    # generate and display scouting observations
    observations = generate_scouting_observations(report)

    # save a structured scouting report
    report["observations"] = observations

    output_dir = Path("data/reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"player_{player_id}.json"

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    print(f"\nSaved scouting report: {output_path}")

    print("\nSCOUTING OBSERVATIONS")

    for observation in observations:
        print("-", observation)

