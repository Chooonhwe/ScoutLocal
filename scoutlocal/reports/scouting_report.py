
# create a scouting report from player percentiles
def generate_scouting_report(player, metrics):
    # collect metric names and percentile values
    results = []

    for metric in metrics:
        percentile_column = f"{metric}_position_percentile"

       
        results.append({
            "metric": metric,
            "value": float(player[metric]),
            "percentile": float(player[percentile_column]),
        })


    # rank metrics from highest to lowest
    results.sort(
        key=lambda item: item["percentile"],
        reverse=True,
    )

    # select two highest and two lowest metrics
    strongest = results[:2]
    lowest = results[-2:][::-1]


    report = {
        "player_name": player["player_name"],
        "team_name": player["team_name"],
        "position": player["primary_position_group"],
        "minutes": float(player["minutes"]),
        "peer_count": int(player["position_peer_count"]),
        "all_metrics": results,
        "strongest_metrics": strongest,
        "lowest_metrics": lowest,
    }

    return report


# convert percentile rankings into neutral descriptions
def describe_percentile(percentile):
    if percentile >= 80:
        return "High recorded activity"
    elif percentile >= 40:
        return "Moderate recorded activity"
    else:
        return "Low recorded activity"

# generate readable scouting observations
def generate_scouting_observations(report):
    observations = []

    # combine highest and lowest ranked metrics
    selected_metrics = (
        report["strongest_metrics"]
        + report["lowest_metrics"]
    )

    # avoid duplicates when profiles have few metrics
    seen_metrics = set()

    for item in selected_metrics:
        metric = item["metric"]

        if metric in seen_metrics:
            continue

        seen_metrics.add(metric)

        # make metric names easier to read
        metric_name = metric.replace("_per90", "")
        metric_name = metric_name.replace("_", " ").capitalize()

        value = item["value"]
        percentile = item["percentile"]

        # format the measurement unit
        unit = " per 90 minutes" if metric.endswith("_per90") else ""

        # build a readable scouting observation
        observation = (
         f"{metric_name}: {value:.2f}{unit} "
         f"(percentile rank {percentile:.2f} among "
         f"{report['peer_count']} eligible "
         f"{report['position'].lower()} players). "
         f"{describe_percentile(percentile)}."
)


        observations.append(observation)

    return observations
