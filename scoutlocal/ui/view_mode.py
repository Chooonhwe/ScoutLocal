
import streamlit as st


# initialize the preferred explanation mode
def init_view_mode():
    if "view_mode" not in st.session_state:
        st.session_state["view_mode"] = "Beginner"


# display a reusable viewing mode selector
def render_view_mode():
    init_view_mode()

    return st.segmented_control(
        "Explanation Level",
        options=["Beginner", "Advanced"],
        key="view_mode",
        help=(
            "Beginner explains statistics in simple language. "
            "Advanced displays more technical scouting details."
        ),
    )


# check whether beginner explanations are enabled
def is_beginner_mode():
    init_view_mode()
    return st.session_state["view_mode"] == "Beginner"
