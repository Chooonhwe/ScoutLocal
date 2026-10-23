
import json

from scoutlocal.reports.comparison_report import (
    generate_comparison_report,
    generate_comparison_summary,
)


# load existing scouting reports
with open(
    "data/reports/player_124903.json",
    encoding="utf-8",
) as file:
    akash = json.load(file)

with open(
    "data/reports/player_161099.json",
    encoding="utf-8",
) as file:
    ricky = json.load(file)

# compare both players
comparison = generate_comparison_report(akash, ricky)

print("\nSCOUTLOCAL PLAYER COMPARISON\n")
print("Player A:", comparison["player_a"])
print("Player B:", comparison["player_b"])
print("Position:", comparison["position"])
print("Shared metrics:", len(comparison["metrics"]))

print("\nMETRIC COMPARISON\n")

for metric in comparison["metrics"]:
    print(
        f"{metric['metric']}: "
        f"{metric['player_a_value']:.2f} vs "
        f"{metric['player_b_value']:.2f} "
        f"| percentiles "
        f"{metric['player_a_percentile']:.2f} vs "
        f"{metric['player_b_percentile']:.2f}"
    )

# summarize each player's higher recorded metrics
summary = generate_comparison_summary(comparison)

print("\nPLAYER COMPARISON SUMMARY\n")

for player_name, metrics in summary["advantages"].items():
    print(f"\n{player_name}")
    print("Higher recorded values:", len(metrics))

    for metric in metrics:
        print("-", metric)

print("\nTied metrics:", len(summary["tied_metrics"]))
print("Total metrics compared:", summary["metrics_compared"])
 