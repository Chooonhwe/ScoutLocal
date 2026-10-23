
# generate a side by side comparison of two scouting reports
def generate_comparison_report(report_a, report_b):
    # ensure both players have the same scouting role
    if report_a["position"] != report_b["position"]:
        raise ValueError(
            "Players must belong to the same positional group."
        )

    # organize metrics by name for easy matching
    metrics_a = {
        item["metric"]: item
        for item in report_a["all_metrics"]
    }

    metrics_b = {
        item["metric"]: item
        for item in report_b["all_metrics"]
    }

    # compare only metrics shared by both reports
    shared_metrics = [
        metric
        for metric in metrics_a
        if metric in metrics_b
    ]

    comparisons = []

    for metric in shared_metrics:
        a = metrics_a[metric]
        b = metrics_b[metric]

        comparisons.append({
            "metric": metric,
            "player_a_value": a["value"],
            "player_b_value": b["value"],
            "player_a_percentile": a["percentile"],
            "player_b_percentile": b["percentile"],
        })

    return {
        "player_a": report_a["player_name"],
        "player_b": report_b["player_name"],
        "position": report_a["position"],
        "metrics": comparisons,
    }



# identify statistical leaders in a player comparison
def generate_comparison_summary(comparison):
    player_a = comparison["player_a"]
    player_b = comparison["player_b"]

    advantages = {
        player_a: [],
        player_b: [],
    }

    tied_metrics = []

    for item in comparison["metrics"]:
        metric = item["metric"]
        value_a = item["player_a_value"]
        value_b = item["player_b_value"]

        # make the metric name readable
        metric_name = metric.replace("_per90", "")
        metric_name = metric_name.replace("_", " ")

        if value_a > value_b:
            advantages[player_a].append(metric_name)

        elif value_b > value_a:
            advantages[player_b].append(metric_name)

        else:
            tied_metrics.append(metric_name)

    return {
        "advantages": advantages,
        "tied_metrics": tied_metrics,
        "metrics_compared": len(comparison["metrics"]),
    }
