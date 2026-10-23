
from scoutlocal.reports.report_builder import (
    build_player_report,
)


# test automatic report generation
for player_id in [124903, 161099]:
    report = build_player_report(player_id)

    print("\nAUTOMATIC REPORT BUILDER TEST")
    print("Player:", report["player_name"])
    print("Team:", report["team_name"])
    print("Position:", report["position"])
    print("Minutes:", f'{report["minutes"]:.2f}')
    print("Eligible peers:", report["peer_count"])
    print("Total metrics:", len(report["all_metrics"]))

    print("\nMETRICS")
    for item in report["all_metrics"]:
        print(
            item["metric"],
            f'Value: {item["value"]:.2f}',
            f'Percentile: {item["percentile"]:.2f}',
        )
