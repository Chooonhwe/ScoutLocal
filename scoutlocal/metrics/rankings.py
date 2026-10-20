
import pandas as pd


# calculate player percentile rankings
def calculate_percentiles(df, metrics, min_minutes=900):
    # check required columns
    required_columns = ["minutes"] + metrics

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # only include players with enough minutes
    eligible = df[
        df["minutes"] >= min_minutes
    ].copy()

    if eligible.empty:
        raise ValueError("No eligible players found.")

    # calculate percentile ranking for each metric
    for metric in metrics:
        eligible[f"{metric}_percentile"] = (
            eligible[metric]
            .rank(pct=True, method="average")
            .mul(100)
        )

    return eligible



# calculate percentiles within each positional group
def calculate_position_percentiles(
    df,
    metrics,
    min_minutes=900,
):
    # check required columns
    required_columns = [
        "minutes",
        "primary_position_group",
    ] + metrics

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    # exclude players with insufficient minutes or unknown positions
    eligible = df[
        (df["minutes"] >= min_minutes)
        & (df["primary_position_group"].notna())
        & (df["primary_position_group"] != "Unknown")
    ].copy()

    if eligible.empty:
        raise ValueError("No eligible players found.")

    # count eligible players in each positional group
    eligible["position_peer_count"] = (
        eligible.groupby("primary_position_group")["minutes"]
        .transform("size")
    )

    # rank each metric only against players in the same role
    for metric in metrics:
        eligible[f"{metric}_position_percentile"] = (
            eligible.groupby("primary_position_group")[metric]
            .rank(pct=True, method="average")
            .mul(100)
        )

    return eligible
