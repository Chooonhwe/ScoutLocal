
import streamlit as st


# beginner-friendly scouting lessons
METRIC_GLOSSARY = {
    "interceptions_won_per90": {
        "title": "Interceptions Won",
        "category": "Defending",
        "definition": (
            "How often a player intercepts an opponent's pass "
            "and wins possession, adjusted per 90 minutes."
        ),
        "example": (
            "A defender anticipates a pass, steps into its path, "
            "and wins possession for their team."
        ),
        "importance": (
            "Helps scouts examine defensive anticipation "
            "and involvement in recovering possession."
        ),
        "caution": (
            "A player with more interceptions is not automatically "
            "a better defender. Team tactics and playing position matter."
        ),
    },
    "tackles_won_per90": {
        "title": "Tackles Won",
        "category": "Defending",
        "definition": (
            "The frequency of successful tackles credited "
            "to a player per 90 minutes."
        ),
        "example": (
            "A full-back challenges an opponent in possession "
            "and wins the ball through a tackle."
        ),
        "importance": (
            "Helps describe a player's recorded defensive activity."
        ),
        "caution": (
            "Tackle counts are affected by defensive opportunities. "
            "Fewer tackles can reflect different team tactics."
        ),
    },
    "progressive_carries_per90": {
        "title": "Progressive Carries",
        "category": "Ball Progression",
        "definition": (
            "The frequency of carries that advance the ball "
            "significantly toward the opponent's goal."
        ),
        "example": (
            "A midfielder receives the ball and carries it "
            "forward into a more advanced attacking area."
        ),
        "importance": (
            "Helps scouts identify players who advance possession "
            "by moving with the ball."
        ),
        "caution": (
            "A high carrying count does not establish that a player "
            "makes better decisions or creates more chances."
        ),
    },
    "progressive_passes_per90": {
        "title": "Progressive Passes",
        "category": "Passing",
        "definition": (
            "The frequency of passes that advance the ball "
            "significantly toward the opponent's goal."
        ),
        "example": (
            "A central midfielder sends a forward pass "
            "that meaningfully advances possession."
        ),
        "importance": (
            "Helps describe how frequently a player "
            "progresses possession through passing."
        ),
        "caution": (
            "Progressive passes are not the same as assists, "
            "and more progressive passes do not always mean "
            "more effective attacking play."
        ),
    },
    "final_third_entries_per90": {
        "title": "Final Third Entries",
        "category": "Attacking",
        "definition": (
            "How often a player advances the ball into "
            "the attacking third of the pitch."
        ),
        "example": (
            "A full-back plays a pass from midfield "
            "into the attacking third."
        ),
        "importance": (
            "Helps describe how often a player contributes "
            "to moving possession into advanced areas."
        ),
        "caution": (
            "Entering the final third does not necessarily "
            "result in a shot or a scoring opportunity."
        ),
    },
}


# common football analytics concepts
CONCEPT_GLOSSARY = {
    "Per 90 Minutes": {
        "definition": (
            "A statistic standardized to 90 minutes of playing time."
        ),
        "formula": "Total recorded actions / Minutes played * 90",
        "example": (
            "A player makes 12 tackles in 360 minutes. "
            "Their tackles per 90 is 3.00."
        ),
    },
    "Percentile Rank": {
        "definition": (
            "A player's relative statistical ranking "
            "within a defined comparison group."
        ),
        "formula": (
            "ScoutLocal ranks eligible positional players "
            "and expresses their relative rank on a 0–100 scale."
        ),
        "example": (
            "A player ranked at the 90th percentile has "
            "relatively high recorded activity among their peers. "
            "This is not a 90% success rate."
        ),
    },
    "Radar Chart": {
        "definition": (
            "A visual chart that displays several statistical "
            "measures around a central point."
        ),
        "formula": "Each axis represents a different metric.",
        "example": (
            "A full-back can have high carrying and interception "
            "percentiles but a lower progressive passing percentile."
        ),
    },
}


def metric_label(metric):
    return (
        metric.removesuffix("_per90")
        .replace("_", " ")
        .title()
    )


# render an individual lesson
def render_metric_lesson(metric):
    lesson = METRIC_GLOSSARY.get(metric)

    if lesson is None:
        st.subheader(metric_label(metric))
        st.info(
            "A verified explanation for this ScoutLocal "
            "metric has not been added yet."
        )
        return

    st.subheader(lesson["title"])
    st.caption(f"Category: {lesson['category']}")

    with st.container(border=True):
        st.markdown("#### What does it mean?")
        st.write(lesson["definition"])

    with st.container(border=True):
        st.markdown("#### ⚽ Example on the pitch")
        st.write(lesson["example"])

    with st.container(border=True):
        st.markdown("#### 🔍 Why do scouts use it?")
        st.write(lesson["importance"])

    with st.container(border=True):
        st.markdown("#### ⚠️ What should you be careful about?")
        st.write(lesson["caution"])


# interactive lesson for understanding per-90 statistics
def render_per90_explainer():
    st.subheader("Practice: Per 90 Minutes")

    st.write(
        "Players have different amounts of playing time. "
        "Per-90 statistics help compare how frequently "
        "they record actions."
    )

    col1, col2 = st.columns(2)

    with col1:
        actions = st.number_input(
            "Recorded actions",
            min_value=0,
            value=12,
            step=1,
            key="academy_actions",
        )

    with col2:
        minutes = st.number_input(
            "Minutes played",
            min_value=1,
            value=360,
            step=30,
            key="academy_minutes",
        )

    per90 = actions / minutes * 90

    st.metric(
        "Actions per 90 minutes",
        f"{per90:.2f}",
    )

    st.caption(
        f"Calculation: {actions} ÷ {minutes} × 90 "
        f"= {per90:.2f}"
    )

    st.info(
        "A per-90 value is an average rate, not the number "
        "of actions guaranteed in the next match. "
        "Very low playing time can produce unstable rates."
    )


# interactive lesson for understanding percentiles
def render_percentile_explainer():
    st.subheader("Practice: Percentile Rankings")

    percentile = st.slider(
        "Explore a percentile",
        min_value=0,
        max_value=100,
        value=85,
        key="academy_percentile",
    )

    st.progress(percentile / 100)

    st.metric(
        "Example percentile rank",
        f"{percentile:.2f}",
    )

    if percentile >= 80:
        description = (
            "This represents relatively high recorded "
            "activity within the comparison group."
        )
    elif percentile <= 20:
        description = (
            "This represents relatively low recorded "
            "activity within the comparison group."
        )
    else:
        description = (
            "This represents a ranking between the "
            "lower and upper ends of the peer group."
        )

    st.write(description)

    st.warning(
        "A percentile is not a success percentage or "
        "an overall player ability score. ScoutLocal's "
        "ranking also depends on the reference population."
    )


# main interactive learning centre
def render_metric_glossary(metrics):
    st.title("📚 ScoutLocal Academy")

    st.write(
        "Learn how football statistics work, why scouts "
        "use them and how to interpret them correctly."
    )

    lessons_tab, concepts_tab, practice_tab = st.tabs(
        [
            "Football Metrics",
            "Analytics Concepts",
            "Practice",
        ]
    )

    with lessons_tab:
        unique_metrics = list(dict.fromkeys(metrics))

        if not unique_metrics:
            st.info("No metrics are available for this selection.")
        else:
            search = st.text_input(
                "Search a football metric",
                placeholder="Try progressive carries...",
                key="academy_metric_search",
            )

            matching = [
                metric for metric in unique_metrics
                if search.casefold() in metric_label(metric).casefold()
            ]

            if not matching:
                st.info("No matching metrics found.")
            else:
                chosen = st.selectbox(
                    "Choose a metric to learn",
                    options=matching,
                    format_func=metric_label,
                    key="academy_selected_metric",
                )

                render_metric_lesson(chosen)

    with concepts_tab:
        st.subheader("Essential Football Analytics Terms")

        for concept, information in CONCEPT_GLOSSARY.items():
            with st.expander(concept):
                st.write(information["definition"])
                st.markdown("**How it works**")
                st.write(information["formula"])
                st.markdown("**Example**")
                st.write(information["example"])

    with practice_tab:
        render_per90_explainer()

        st.divider()

        render_percentile_explainer()

    st.divider()

    st.caption(
        "ScoutLocal Academy | Educational explanations. "
        "Exact event and metric definitions should be checked "
        "against ScoutLocal's calculation methodology."
    )
