
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from scoutlocal.database.scouting_db import (
    initialize_database,
    save_scouting_report,
    get_player_reports,
    get_all_reports,
    update_scouting_report,
    delete_scouting_report,
)

from scoutlocal.reports.pdf_export import generate_scouting_pdf

st.set_page_config(
    page_title="ScoutLocal | Scouting Reports",
    layout="wide",
)

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "player_metrics_with_positions.csv"
)


@st.cache_data
def load_players():
    return pd.read_csv(DATA_PATH)


initialize_database()
df = load_players()

st.title("Scouting Reports")
st.caption(
    "Create and manage evidence-based player assessments."
)

# Two main report sections
create_tab, history_tab = st.tabs([
    "Create Report",
    "Report History",
])


# --------------------------------------------------
# CREATE REPORT
# --------------------------------------------------

with create_tab:
    st.subheader("New Player Assessment")

    players = df.copy()

    players["label"] = (
        players["player_name"].astype(str)
        + " | "
        + players["team_name"].astype(str)
        + " | "
        + players["primary_position_group"].astype(str)
    )

    # Automatically select the player chosen in Scout,
    # if one is available.
    selected_id = st.session_state.get("selected_player_id")
    selected_team_id = st.session_state.get("selected_team_id")

    default_index = 0

    if selected_id is not None and selected_team_id is not None:
        matching = players[
            (players["player_id"] == selected_id)
            & (players["team_id"] == selected_team_id)
        ]

        if not matching.empty:
            default_index = players.index.get_loc(
                matching.index[0]
            )

    selected_index = st.selectbox(
        "Select Player",
        options=players.index.tolist(),
        index=default_index,
        format_func=lambda i: players.loc[i, "label"],
    )

    player = players.loc[selected_index]

    st.info(
        f"Selected player: {player['player_name']} | "
        f"{player['team_name']} | "
        f"{player['primary_position_group']}"
    )

    with st.form("scouting_report_form"):

        left, right = st.columns(2)

        with left:
            scout_name = st.text_input(
                "Scout Name",
                placeholder="Your name or initials",
            )

            observation_date = st.date_input(
                "Observation Date",
                value=date.today(),
            )

            match_context = st.text_input(
                "Match / Observation Context",
                placeholder="e.g. Hyderabad vs Jamshedpur",
            )

        with right:
            recommendation = st.selectbox(
                "Recruitment Recommendation",
                [
                    "Monitor",
                    "Investigate Further",
                    "Shortlist",
                    "Not Recommended",
                ],
            )

        st.subheader("Player Evaluation")

        st.caption(
            "Ratings are scout assessments, not "
            "automatically calculated statistics."
        )

        rating1, rating2, rating3 = st.columns(3)

        with rating1:
            technical = st.select_slider(
                "Technical Ability",
                options=[1, 2, 3, 4, 5],
                value=3,
            )

        with rating2:
            tactical = st.select_slider(
                "Tactical Understanding",
                options=[1, 2, 3, 4, 5],
                value=3,
            )

        with rating3:
            physical = st.select_slider(
                "Physical Attributes",
                options=[1, 2, 3, 4, 5],
                value=3,
            )

        strengths = st.text_area(
            "Player Strengths",
            placeholder=(
                "Describe observed strengths and "
                "support them with examples."
            ),
        )

        weaknesses = st.text_area(
            "Development Areas",
            placeholder=(
                "Describe limitations or areas "
                "that require further evaluation."
            ),
        )

        observations = st.text_area(
            "Detailed Scouting Observations",
            height=180,
            placeholder=(
                "Record tactical behaviour, decision-making, "
                "technical actions and match context."
            ),
        )

        submitted = st.form_submit_button(
            "Save Scouting Report",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not scout_name.strip():
                st.error(
                    "Please enter the scout's name "
                    "before saving."
                )
            elif not observations.strip():
                st.error(
                    "Please record at least one scouting "
                    "observation before saving."
                )
            else:
                report = {
                    "player_id": int(player["player_id"]),
                    "team_id": int(player["team_id"]),
                    "player_name": str(player["player_name"]),
                    "team_name": str(player["team_name"]),
                    "position": str(
                        player["primary_position_group"]
                    ),
                    "scout_name": scout_name.strip(),
                    "observation_date": observation_date.isoformat(),
                    "match_context": match_context.strip(),
                    "technical_rating": technical,
                    "tactical_rating": tactical,
                    "physical_rating": physical,
                    "strengths": strengths.strip(),
                    "weaknesses": weaknesses.strip(),
                    "observations": observations.strip(),
                    "recommendation": recommendation,
                }

                report_id = save_scouting_report(report)

                st.success(
                    f"Scouting report #{report_id} "
                    "saved successfully."
                )


# --------------------------------------------------
# REPORT HISTORY
# --------------------------------------------------

with history_tab:
    st.subheader("Saved Scouting Reports")

    reports = get_all_reports()

    if not reports:
        st.info(
            "No scouting reports have been saved yet."
        )

    else:
        history = pd.DataFrame(reports)

        st.dataframe(
            history[
                [
                    "id",
                    "player_name",
                    "team_name",
                    "position",
                    "scout_name",
                    "observation_date",
                    "recommendation",
                ]
            ].rename(columns={
                "id": "Report ID",
                "player_name": "Player",
                "team_name": "Club",
                "position": "Position",
                "scout_name": "Scout",
                "observation_date": "Observation Date",
                "recommendation": "Recommendation",
            }),
            hide_index=True,
            use_container_width=True,
        )

        st.divider()

        report_options = {
            f"#{report['id']} | "
            f"{report['player_name']} | "
            f"{report['observation_date']}": report
            for report in reports
        }

        selected_report = st.selectbox(
            "Open Scouting Report",
            list(report_options.keys()),
        )

        report = report_options[selected_report]

        with st.container(border=True):
            st.subheader(report["player_name"])

            st.caption(
                f"{report['team_name']} | "
                f"{report['position']}"
            )

            st.write(
                f"**Scout:** {report['scout_name']}"
            )

            st.write(
                f"**Observation Date:** "
                f"{report['observation_date']}"
            )

            st.write(
                f"**Match Context:** "
                f"{report['match_context'] or 'Not specified'}"
            )

            st.write(
                f"**Recommendation:** "
                f"{report['recommendation']}"
            )

            st.divider()

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Technical",
                f"{report['technical_rating']}/5",
            )

            c2.metric(
                "Tactical",
                f"{report['tactical_rating']}/5",
            )

            c3.metric(
                "Physical",
                f"{report['physical_rating']}/5",
            )

            st.markdown("#### Strengths")
            st.write(
                report["strengths"] or "Not recorded"
            )

            st.markdown("#### Development Areas")
            st.write(
                report["weaknesses"] or "Not recorded"
            )

            st.markdown("#### Scouting Observations")
            st.write(report["observations"])

            st.divider()

            # Generate a PDF of the currently selected report.
            pdf_data = generate_scouting_pdf(report)

            st.download_button(
                label="Export Scouting Report (PDF)",
                data=pdf_data,
                file_name=(
                    f"ScoutLocal_Report_{report['id']}.pdf"
                ),
                mime="application/pdf",
                type="primary",
                use_container_width=True,
                key=f"export_report_{report['id']}",
            )

            # EDIT EXISTING SCOUTING REPORT
            st.divider()

            with st.expander("Edit This Report"):

                st.caption(
                    "Update your scouting assessment. "
                    "Changes will be saved to the existing report."
                )

                with st.form(
                    f"edit_report_form_{report['id']}"
                ):

                    edit_scout_name = st.text_input(
                        "Scout Name",
                        value=report["scout_name"] or "",
                    )

                    edit_match_context = st.text_input(
                        "Match / Observation Context",
                        value=report["match_context"] or "",
                    )

                    edit_recommendation = st.selectbox(
                        "Recruitment Recommendation",
                        [
                            "Monitor",
                            "Investigate Further",
                            "Shortlist",
                            "Not Recommended",
                        ],
                        index=(
                            [
                                "Monitor",
                                "Investigate Further",
                                "Shortlist",
                                "Not Recommended",
                            ].index(report["recommendation"])
                            if report["recommendation"] in [
                                "Monitor",
                                "Investigate Further",
                                "Shortlist",
                                "Not Recommended",
                            ]
                            else 0
                        ),
                    )

                    st.markdown("#### Scout Evaluation")

                    rating_options = [1, 2, 3, 4, 5]

                    edit_technical = st.select_slider(
                        "Technical Ability",
                        options=rating_options,
                        value=report["technical_rating"] or 3,
                    )

                    edit_tactical = st.select_slider(
                        "Tactical Understanding",
                        options=rating_options,
                        value=report["tactical_rating"] or 3,
                    )

                    edit_physical = st.select_slider(
                        "Physical Attributes",
                        options=rating_options,
                        value=report["physical_rating"] or 3,
                    )

                    edit_strengths = st.text_area(
                        "Player Strengths",
                        value=report["strengths"] or "",
                    )

                    edit_weaknesses = st.text_area(
                        "Development Areas",
                        value=report["weaknesses"] or "",
                    )

                    edit_observations = st.text_area(
                        "Detailed Scouting Observations",
                        value=report["observations"] or "",
                        height=180,
                    )

                    save_changes = st.form_submit_button(
                        "Save Report Changes",
                        type="primary",
                        use_container_width=True,
                    )

                    if save_changes:
                        if not edit_scout_name.strip():
                            st.error(
                                "Please enter a scout name."
                            )

                        elif not edit_observations.strip():
                            st.error(
                                "Scouting observations cannot be empty."
                            )

                        else:
                            updated = update_scouting_report(
                                report["id"],
                                {
                                    "scout_name": edit_scout_name.strip(),
                                    "match_context": edit_match_context.strip(),
                                    "technical_rating": edit_technical,
                                    "tactical_rating": edit_tactical,
                                    "physical_rating": edit_physical,
                                    "strengths": edit_strengths.strip(),
                                    "weaknesses": edit_weaknesses.strip(),
                                    "observations": edit_observations.strip(),
                                    "recommendation": edit_recommendation,
                                },
                            )

                            if updated:
                                st.success(
                                    "Scouting report updated successfully."
                                )
                                st.rerun()
                            else:
                                st.error(
                                    "Report could not be updated."
                                )

            # DELETE EXISTING SCOUTING REPORT
            st.divider()

            with st.expander("Delete This Report"):
                st.warning(
                    "Deleting this scouting report is permanent. "
                    "This action cannot be undone."
                )

                confirm_delete = st.checkbox(
                    f"I confirm that I want to permanently "
                    f"delete report #{report['id']}.",
                    key=f"confirm_delete_{report['id']}",
                )

                if st.button(
                    "Delete Report Permanently",
                    disabled=not confirm_delete,
                    key=f"delete_report_{report['id']}",
                    use_container_width=True,
                ):
                    deleted = delete_scouting_report(
                        report["id"]
                    )

                    if deleted:
                        st.session_state[
                            "report_deleted_message"
                        ] = (
                            f"Report #{report['id']} "
                            "was deleted successfully."
                        )
                        st.rerun()
                    else:
                        st.error(
                            "Report could not be deleted."
                        )


st.divider()

st.caption(
    "ScoutLocal | Scouting assessments are subjective "
    "observations and should be supported by evidence."
)
