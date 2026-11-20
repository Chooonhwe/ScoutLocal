
import math

import plotly.graph_objects as go
import streamlit as st


# format metric names for display
def metric_label(metric):
    return (
        metric.removesuffix("_per90")
        .replace("_", " ")
        .title()
    )


# compare two players using positional percentiles
def render_comparison_radar(
    metrics_a,
    metrics_b,
    player_a_name,
    player_b_name,
):
    # match statistics by metric name
    player_a = {
        item["metric"]: item
        for item in metrics_a
    }

    player_b = {
        item["metric"]: item
        for item in metrics_b
    }

    # preserve metric order from the first player
    shared_metrics = []

    for metric in player_a:
        if metric not in player_b:
            continue

        a = player_a[metric].get("percentile")
        b = player_b[metric].get("percentile")

        try:
            if (
                a is not None
                and b is not None
                and math.isfinite(float(a))
                and math.isfinite(float(b))
            ):
                shared_metrics.append(metric)
        except (TypeError, ValueError):
            continue

    if len(shared_metrics) < 3:
        st.info(
            "At least three shared percentile metrics "
            "are required for a radar comparison."
        )
        return

    labels = [
        metric_label(metric)
        for metric in shared_metrics
    ]

    values_a = [
        float(player_a[metric]["percentile"])
        for metric in shared_metrics
    ]

    values_b = [
        float(player_b[metric]["percentile"])
        for metric in shared_metrics
    ]

    # close both radar polygons
    labels.append(labels[0])
    values_a.append(values_a[0])
    values_b.append(values_b[0])

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values_a,
            theta=labels,
            fill="toself",
            name=player_a_name,
            line=dict(
                color="#60A5FA",
                width=3,
            ),
            fillcolor="rgba(96,165,250,0.18)",
            hovertemplate=(
                "%{theta}<br>"
                "Percentile: %{r:.2f}"
                "<extra>%{fullData.name}</extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatterpolar(
            r=values_b,
            theta=labels,
            fill="toself",
            name=player_b_name,
            line=dict(
                color="#F59E0B",
                width=3,
            ),
            fillcolor="rgba(245,158,11,0.15)",
            hovertemplate=(
                "%{theta}<br>"
                "Percentile: %{r:.2f}"
                "<extra>%{fullData.name}</extra>"
            ),
        )
    )

    fig.update_layout(
        paper_bgcolor="#0B1220",
        polar=dict(
            bgcolor="#101D31",
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                gridcolor="#31445E",
                tickfont=dict(color="#94A3B8"),
            ),
            angularaxis=dict(
                gridcolor="#31445E",
                tickfont=dict(
                    color="#D5E3F3",
                    size=12,
                ),
            ),
        ),
        font=dict(color="#D5E3F3"),
        legend=dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=-0.1,
        ),
        showlegend=True,
        height=500,
        margin=dict(l=80, r=80, t=40, b=80),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

    st.caption(
        "Both players should be compared using the same "
        "position, competition, season and percentile "
        "reference group. Radar size does not represent "
        "overall player quality."
    )
