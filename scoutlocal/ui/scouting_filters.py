
import pandas as pd
import streamlit as st


def metric_label(metric):
    return (
        metric.removesuffix("_per90")
        .replace("_", " ")
        .title()
    )


def render_advanced_filters(candidates, eligible, focus_metrics):
    """
    Filter player candidates using positional percentiles.

    candidates:
        Players who passed the existing search filters.

    eligible:
        Players with at least 900 minutes in the selected
        position, including percentile columns.

    focus_metrics:
        Metrics available for the selected scouting role.
    """

    with st.expander("Advanced Scouting Filters", expanded=False):

        st.caption(
            "Find players who meet specific statistical "
            "requirements. Percentiles compare players "
            "within the same positional group."
        )

        available_metrics = [
            metric
            for metric in focus_metrics
            if f"pct_{metric}" in eligible.columns
        ]

        if not available_metrics:
            st.info(
                "No percentile metrics are available "
                "for this scouting selection."
            )
            return candidates

        enabled = st.checkbox(
            "Enable advanced filters",
            value=False,
            key="advanced_filters_enabled",
        )

        if not enabled:
            return candidates

        metric_1 = st.selectbox(
            "First Statistical Metric",
            available_metrics,
            format_func=metric_label,
            key="advanced_metric_1",
        )

        percentile_1 = st.slider(
            "Minimum Percentile — First Metric",
            0,
            100,
            70,
            5,
            key="advanced_percentile_1",
        )

        use_second = st.checkbox(
            "Add a second statistical condition",
            value=False,
            key="advanced_use_second",
        )

        metric_2 = None
        percentile_2 = None

        if use_second:
            second_options = [
                metric
                for metric in available_metrics
                if metric != metric_1
            ]

            if second_options:
                metric_2 = st.selectbox(
                    "Second Statistical Metric",
                    second_options,
                    format_func=metric_label,
                    key="advanced_metric_2",
                )

                percentile_2 = st.slider(
                    "Minimum Percentile — Second Metric",
                    0,
                    100,
                    60,
                    5,
                    key="advanced_percentile_2",
                )
            else:
                st.info(
                    "Only one metric is available for this role."
                )

        conditions = [
            (metric_1, percentile_1)
        ]

        if metric_2 is not None:
            conditions.append(
                (metric_2, percentile_2)
            )

        result = candidates.copy()

        # Match eligible player records using their existing indices.
        for metric, threshold in conditions:
            percentile_column = f"pct_{metric}"

            matches = eligible[
                eligible[percentile_column] >= threshold
            ].index

            result = result[
                result.index.isin(matches)
            ]

        st.caption(
            f"{len(result)} candidates satisfy "
            "the advanced statistical requirements."
        )

        st.info(
            "Players below 900 minutes remain searchable "
            "when advanced filters are disabled. "
            "Percentile filters require at least 900 minutes."
        )

        return result
