
import argparse

from scoutlocal.reports.report_builder import (
    build_player_report,
    find_player_id,
)
from scoutlocal.reports.comparison_report import (
    generate_comparison_report,
    generate_comparison_summary,
)


# accept either player names or player ids
parser = argparse.ArgumentParser(
    description="Compare two ScoutLocal players"
)

parser.add_argument("player_a", type=str)
parser.add_argument("player_b", type=str)

args = parser.parse_args()


# convert names or numeric ids into player ids
def resolve_player_id(value):
    if value.isdigit():
        return int(value)

    return find_player_id(value)


player_a_id = resolve_player_id(args.player_a)
player_b_id = resolve_player_id(args.player_b)


# build reports using resolved player ids
report_a = build_player_report(player_a_id)
report_b = build_player_report(player_b_id)

# generate player comparison
comparison = generate_comparison_report(
    report_a,
    report_b,
)

summary = generate_comparison_summary(comparison)


# display player details
print("\nSCOUTLOCAL PLAYER COMPARISON\n")

print("Player A:", comparison["player_a"])
print("Player B:", comparison["player_b"])
print("Position:", comparison["position"])
print("Shared metrics:", len(comparison["metrics"]))


# display statistics and rankings
print("\nMETRIC COMPARISON\n")

for item in comparison["metrics"]:
    print(
        f"{item['metric']}: "
        f"{item['player_a_value']:.2f} vs "
        f"{item['player_b_value']:.2f} "
        f"| percentiles "
        f"{item['player_a_percentile']:.2f} vs "
        f"{item['player_b_percentile']:.2f}"
    )


# summarize higher recorded values
print("\nCOMPARISON SUMMARY\n")

for player_name, metrics in summary["advantages"].items():
    print(
        f"{player_name}: "
        f"{len(metrics)} higher metrics"
    )

    for metric in metrics:
        print(f"  - {metric}")

print("Tied metrics:", len(summary["tied_metrics"]))
