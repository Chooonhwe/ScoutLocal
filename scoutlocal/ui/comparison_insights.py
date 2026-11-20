
import math

import pandas as pd
import streamlit as st


# format metric names
def metric_label(metric):
    return metric.removesuffix("_per90").replace("_", " ").title()


# safely convert numbers
def valid_number(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


# compare shared metrics between players
def build_comparison_insights(metrics_a, metrics_b):
    lookup_b = {
        item["metric"]: item
        for item in metrics_b
    }

    rows = []

    for item_a in metrics_a:
        metric = item_a["metric"]
        item_b = lookup_b.get(metric)

        if item_b is None:
            continue

        value_a = valid_number(item_a.get("value"))
        value_b = valid_number(item_b.get("value"))
        percentile_a = valid_number(item_a.get("percentile"))
        percentile_b = valid_number(item_b.get("percentile"))

        # only compare complete metric records
        if None in (value_a, value_b, percentile_a, percentile_b):
            continue

        difference = percentile_a - percentile_b

        if math.isclose(difference, 0.0, abs_tol=1e-9):
            leader = "Tie"
        elif difference > 0:
            leader = "Player A"
        else:
            leader = "Player B"

        rows.append({
            "Metric": metric_label(metric),
            "Player A /90": value_a,
            "Player B /90": value_b,
            "Player A Percentile": percentile_a,
            "Player B Percentile": percentile_b,
            "Difference": difference,
            "Absolute Difference": abs(difference),
            "Higher Activity": leader,
        })

    return pd.DataFrame(rows)


# display automatically generated comparison insights
def render_comparison_insights(
    metrics_a,
    metrics_b,
    player_a_name,
    player_b_name,
):
    st.subheader("Automated Comparison Insights")

    results = build_comparison_insights(metrics_a, metrics_b)

    if results.empty:
        st.info(
            "No shared metrics with valid percentile rankings "
            "are available for comparison."
        )
        return

    # calculate descriptive comparison counts
    a_higher = int(
        (results["Higher Activity"] == "Player A").sum()
    )
    b_higher = int(
        (results["Higher Activity"] == "Player B").sum()
    )
    ties = int(
        (results["Higher Activity"] == "Tie").sum()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        f"{player_a_name} Higher",
        a_higher,
    )
    col2.metric(
        f"{player_b_name} Higher",
        b_higher,
    )
    col3.metric("Tied Metrics", ties)

    st.caption(
        f"Based on {len(results)} shared statistical metrics. "
        "These counts do not represent an overall player score."
    )

    st.divider()

    # show the largest percentile differences
    st.subheader("Largest Statistical Differences")

    ranked = results.sort_values(
        "Absolute Difference",
        ascending=False,
    )

    for _, row in ranked.head(5).iterrows():
        gap = float(row["Absolute Difference"])

        if row["Higher Activity"] == "Player A":
            leader_name = player_a_name
        elif row["Higher Activity"] == "Player B":
            leader_name = player_b_name
        else:
            leader_name = "Both players"

        with st.container(border=True):
            left, right = st.columns([3, 1])

            with left:
                st.markdown(f"**{row['Metric']}**")
                st.caption(
                    f"Higher recorded activity: {leader_name}"
                )

            with right:
                st.metric(
                    "Percentile gap",
                    f"{gap:.2f} pp",
                )

            st.progress(min(gap / 100, 1.0))

            st.caption(
                f"{player_a_name}: "
                f"{row['Player A /90']:.2f} /90 "
                f"({row['Player A Percentile']:.2f} percentile) | "
                f"{player_b_name}: "
                f"{row['Player B /90']:.2f} /90 "
                f"({row['Player B Percentile']:.2f} percentile)"
            )

    st.divider()

    # summarise higher activity for each player
    st.subheader("Statistical Playing-Style Summary")

    higher_a = results[
        results["Higher Activity"] == "Player A"
    ]["Metric"].tolist()

    higher_b = results[
        results["Higher Activity"] == "Player B"
    ]["Metric"].tolist()

    left, right = st.columns(2)

    with left:
        with st.container(border=True):
            st.markdown(f"#### {player_a_name}")

            if higher_a:
                st.write(
                    "Records higher activity in:"
                )
                for metric in higher_a:
                    st.write(f"• {metric}")
            else:
                st.write(
                    "No higher activity among the compared metrics."
                )

    with right:
        with st.container(border=True):
            st.markdown(f"#### {player_b_name}")

            if higher_b:
                st.write(
                    "Records higher activity in:"
                )
                for metric in higher_b:
                    st.write(f"• {metric}")
            else:
                st.write(
                    "No higher activity among the compared metrics."
                )

    st.divider()

    # display full numerical differences
    st.subheader("Complete Comparison Breakdown")

    display_df = results[
        [
            "Metric",
            "Player A /90",
            "Player B /90",
            "Player A Percentile",
            "Player B Percentile",
            "Difference",
        ]
    ].rename(
        columns={
            "Difference": "A - B (Percentile Points)"
        }
    )

    numeric_columns = display_df.select_dtypes(
        include="number"
    ).columns

    st.dataframe(
        display_df.style.format({
            column: "{:.2f}"
            for column in numeric_columns
        }),
        hide_index=True,
        use_container_width=True,
    )

    st.info(
        "These insights describe statistical differences "
        "within the selected positional peer group. "
        "They do not identify an overall winner, measure "
        "tactical suitability, or establish player quality."
    )
