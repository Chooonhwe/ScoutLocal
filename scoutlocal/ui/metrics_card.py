
import pandas as pd
import streamlit as st


# convert metric names into readable labels
def metric_label(metric):
    return metric.removesuffix("_per90").replace("_", " ").title()


# display the player's main statistical summary
def render_player_metrics(player, peer_count, metrics):
    minutes = float(player["minutes"])

    st.subheader("Performance Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.metric("Minutes Played", f"{minutes:,.2f}")

    with col2:
        with st.container(border=True):
            st.metric("Eligible Positional Peers", peer_count)

    with col3:
        with st.container(border=True):
            st.metric("Metrics Analysed", len(metrics))

    # show ranking eligibility
    if minutes < 900:
        st.warning(
            "Limited playing time: this player has fewer than "
            "900 minutes. Per-90 statistics can be displayed, "
            "but positional percentile rankings are unavailable."
        )
    else:
        st.caption(
            "Percentile eligibility: at least 900 recorded minutes."
        )


# display position-specific statistical performance
def render_metric_breakdown(metrics):
    st.subheader("Statistical Breakdown")

    if not metrics:
        st.info("No position-specific metrics available.")
        return

    for metric in metrics:
        name = metric_label(metric["metric"])
        value = metric.get("value")
        percentile = metric.get("percentile")

        with st.container(border=True):
            left, right = st.columns([3, 1])

            with left:
                st.markdown(f"**{name}**")

                if value is not None and pd.notna(value):
                    st.caption(
                        f"{float(value):.2f} recorded actions per 90 minutes"
                    )
                else:
                    st.caption("No recorded value available")

            with right:
                if percentile is not None and pd.notna(percentile):
                    st.metric(
                        "Percentile",
                        f"{float(percentile):.2f}",
                    )
                else:
                    st.caption("Not ranked")

            if percentile is not None and pd.notna(percentile):
                st.progress(
                    min(max(float(percentile) / 100, 0.0), 1.0)
                )

    st.caption(
        "Percentiles show relative statistical activity among "
        "eligible positional peers, not overall player quality."
    )
