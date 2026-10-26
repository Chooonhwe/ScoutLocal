
import math

import streamlit as st


# format metric names
def metric_label(metric):
    return metric.removesuffix("_per90").replace("_", " ").title()


# generate evidence-based scouting observations
def generate_observations(metrics, peer_count):
    observations = []

    for item in metrics:
        percentile = item.get("percentile")
        value = item.get("value")

        if percentile is None or value is None:
            continue

        try:
            percentile = float(percentile)
            value = float(value)
        except (TypeError, ValueError):
            continue

        if not (math.isfinite(percentile) and math.isfinite(value)):
            continue

        name = metric_label(item["metric"])

        if percentile >= 80:
            description = "Higher recorded activity than most positional peers"
        elif percentile <= 20:
            description = "Lower recorded activity than most positional peers"
        else:
            description = "Within the middle range of positional peers"

        observations.append(
            f"**{name}:** {value:.2f} per 90 minutes "
            f"({percentile:.2f} percentile among "
            f"{peer_count} eligible positional peers). "
            f"{description}."
        )

    return observations


# render the scouting insights section
def render_scouting_insights(metrics, peer_count):
    st.subheader("Scouting Intelligence")

    valid_metrics = []

    for item in metrics:
        percentile = item.get("percentile")
        value = item.get("value")

        try:
            if (
                percentile is not None
                and value is not None
                and math.isfinite(float(percentile))
                and math.isfinite(float(value))
            ):
                valid_metrics.append(item)
        except (TypeError, ValueError):
            continue

    if not valid_metrics:
        st.info(
            "No eligible positional percentile rankings "
            "are available for this player."
        )
        return

    ranked = sorted(
        valid_metrics,
        key=lambda item: float(item["percentile"]),
        reverse=True,
    )

    strongest = ranked[0]
    lowest = ranked[-1]

    left_col, right_col = st.columns(2)

    with left_col:
        with st.container(border=True):
            st.caption("HIGHEST-RANKED METRIC")
            st.subheader(metric_label(strongest["metric"]))
            st.metric(
                "Percentile Rank",
                f"{float(strongest['percentile']):.2f}",
            )
            st.caption(
                f"{float(strongest['value']):.2f} per 90 minutes"
            )

    with right_col:
        with st.container(border=True):
            st.caption("LOWEST-RANKED METRIC")
            st.subheader(metric_label(lowest["metric"]))
            st.metric(
                "Percentile Rank",
                f"{float(lowest['percentile']):.2f}",
            )
            st.caption(
                f"{float(lowest['value']):.2f} per 90 minutes"
            )

    st.divider()
    st.subheader("Statistical Observations")

    for observation in generate_observations(
        valid_metrics, peer_count
    ):
        st.markdown(f"- {observation}")

    st.info(
        "ScoutLocal describes recorded statistical activity, "
        "not overall player ability. Higher percentiles are "
        "not automatically better for every metric."
    )
