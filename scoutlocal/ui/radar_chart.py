
import math

import plotly.graph_objects as go
import streamlit as st


# convert metric names into readable labels
def metric_label(metric):
    return (
        metric.removesuffix("_per90")
        .replace("_", " ")
        .title()
    )


# render a player's positional scouting radar
def render_radar_chart(metrics, player_name):
    if not metrics:
        st.info("No positional metrics available for this player.")
        return

    # ignore metrics without a valid percentile
    valid_metrics = [
        item for item in metrics
        if item.get("percentile") is not None
        and math.isfinite(float(item["percentile"]))
    ]

    if len(valid_metrics) < 3:
        st.info(
            "At least three valid positional percentiles "
            "are needed to display a radar chart."
        )
        return

    labels = [
        metric_label(item["metric"])
        for item in valid_metrics
    ]

    values = [
        float(item["percentile"])
        for item in valid_metrics
    ]

    # close the radar shape
    labels.append(labels[0])
    values.append(values[0])

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=labels,
            fill="toself",
            name=player_name,
            line=dict(color="#60A5FA", width=3),
            fillcolor="rgba(96, 165, 250, 0.22)",
            hovertemplate=(
                "%{theta}<br>"
                "Percentile: %{r:.2f}"
                "<extra></extra>"
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
                tickfont=dict(color="#D5E3F3", size=12),
            ),
        ),
        showlegend=False,
        margin=dict(l=70, r=70, t=30, b=30),
        height=440,
        font=dict(color="#D5E3F3"),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
    )

    st.caption(
        "Radar values represent positional percentile ranks "
        "from 0 to 100, not overall player ability."
    )
