
import pandas as pd
import streamlit as st

from scoutlocal.database.recruitment_db import (
    RECRUITMENT_STATUSES,
    RECRUITMENT_PRIORITIES,
    initialize_recruitment_database,
    get_recruitment_targets,
    update_recruitment_target,
    remove_recruitment_target,
)


st.set_page_config(
    page_title="ScoutLocal | Recruitment Shortlist",
    layout="wide",
)

from scoutlocal.database.scouting_db import get_player_reports

initialize_recruitment_database()




st.title("Recruitment Shortlist")

st.caption(
    "Manage recruitment targets, scouting priorities "
    "and player evaluation progress."
)

targets = get_recruitment_targets()


total_targets = len(targets)

active_targets = sum(
    target["status"] != "Archived"
    for target in targets
)

shortlisted_targets = sum(
    target["status"] == "Shortlisted"
    for target in targets
)

recommended_targets = sum(
    target["status"] == "Recommended"
    for target in targets
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Targets",
    total_targets,
)

col2.metric(
    "Active Targets",
    active_targets,
)

col3.metric(
    "Shortlisted",
    shortlisted_targets,
)

col4.metric(
    "Recommended",
    recommended_targets,
)

st.divider()
st.subheader("Recruitment Pipeline")

st.caption(
    "Track players through each stage of "
    "the recruitment process."
)

pipeline_stages = [
    "Identified",
    "Under Review",
    "Shortlisted",
    "Recommended",
]

pipeline_columns = st.columns(
    4,
    gap="small",
)

for column, stage in zip(
    pipeline_columns,
    pipeline_stages,
):

    stage_targets = [
        target
        for target in targets
        if target["status"] == stage
    ]

    with column:
        with st.container(border=True):

            st.markdown(f"**{stage}**")

            st.metric(
                "Players",
                len(stage_targets),
            )

            st.divider()

            if not stage_targets:
                st.caption("No players")

            else:
                for target in stage_targets:

                    st.markdown(
                        f"**{target['player_name']}**"
                    )

                    st.caption(
                        f"{target['team_name']} | "
                        f"Priority: {target['priority']}"
                    )

                    if st.button(
                        "Manage Player",
                        key=f"pipeline_manage_{target['id']}",
                        use_container_width=True,
                    ):
                        st.session_state[
                            "selected_recruitment_id"
                        ] = int(target["id"])

                        st.rerun()

                    st.divider()


archived_count = sum(
    target["status"] == "Archived"
    for target in targets
)

st.caption(
    f"Archived recruitment targets: {archived_count}"
)

st.divider()


# filters
st.subheader("Recruitment Database")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    status_filter = st.selectbox(
        "Recruitment Status",
        ["All Statuses"] + RECRUITMENT_STATUSES,
    )

with filter_col2:
    priority_filter = st.selectbox(
        "Recruitment Priority",
        ["All Priorities"] + RECRUITMENT_PRIORITIES,
    )

with filter_col3:
    search = st.text_input(
        "Search Player",
        placeholder="Search player or club name...",
    )
# apply filters
filtered = targets

if status_filter != "All Statuses":
    filtered = [
        target
        for target in filtered
        if target["status"] == status_filter
    ]

if priority_filter != "All Priorities":
    filtered = [
        target
        for target in filtered
        if target["priority"] == priority_filter
    ]

if search.strip():
    query = search.strip().casefold()

    filtered = [
        target
        for target in filtered
        if (
            query in target["player_name"].casefold()
            or query in target["team_name"].casefold()
        )
    ]

#Database Table
if not filtered:

    st.info(
        "No recruitment targets match your search. "
        "Add players from Scout or adjust your filters."
    )

else:

    table = pd.DataFrame(filtered)

    display_columns = [
        "player_name",
        "team_name",
        "position",
        "status",
        "priority",
        "updated_at",
    ]

    st.dataframe(
        table[display_columns].rename(
            columns={
                "player_name": "Player",
                "team_name": "Club",
                "position": "Position",
                "status": "Status",
                "priority": "Priority",
                "updated_at": "Last Updated",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

    st.divider()


# evidence

    st.divider()

    st.subheader("Scouting Evidence")

    st.caption(
        "Review saved scouting assessments before "
        "making recruitment decisions."
    )

    player_reports = get_player_reports(
        int(target["player_id"]),
        int(target["team_id"]),
    )

    st.metric(
        "Available Scouting Reports",
        len(player_reports),
    )

    if not player_reports:
        st.info(
            "No scouting reports have been recorded "
            "for this player and club yet."
        )

    else:
        for report in player_reports:

            report_title = (
                f"Report #{report['id']} | "
                f"{report['observation_date']} | "
                f"{report['recommendation']}"
            )

            with st.expander(report_title):

                st.markdown(
                    f"**Scout:** {report['scout_name']}"
                )

                st.markdown(
                    f"**Match Context:** "
                    f"{report['match_context'] or 'Not recorded'}"
                )

                st.divider()

                # Scout evaluation ratings
                rating_col1, rating_col2, rating_col3 = (
                    st.columns(3)
                )

                rating_fields = [
                    (
                        rating_col1,
                        "Technical",
                        "technical_rating",
                    ),
                    (
                        rating_col2,
                        "Tactical",
                        "tactical_rating",
                    ),
                    (
                        rating_col3,
                        "Physical",
                        "physical_rating",
                    ),
                ]

                for column, label, field in rating_fields:
                    rating = report[field]

                    column.metric(
                        label,
                        f"{rating}/5"
                        if rating is not None
                        else "Not rated",
                    )

                st.divider()

                st.markdown("**Strengths**")

                st.write(
                    report["strengths"]
                    or "Not recorded"
                )

                st.markdown("**Development Areas**")

                st.write(
                    report["weaknesses"]
                    or "Not recorded"
                )

                st.markdown("**Detailed Observations**")

                st.write(
                    report["observations"]
                    or "Not recorded"
                )

                st.markdown("**Scout Recommendation**")

                st.write(
                    report["recommendation"]
                )

    st.caption(
        "These reports are human scouting assessments. "
        "Ratings and recommendations are not automatically "
        "generated from player statistics."
    )

# Manage Recruitment Target
    st.subheader("Manage Recruitment Target")

    options = {
        (
            f"{target['player_name']} | "
            f"{target['team_name']} | "
            f"Target #{target['id']}"
        ): target
        for target in filtered
    }

    option_labels = list(options.keys())

    selected_target_id = st.session_state.get(
        "selected_recruitment_id"
    )

    default_index = 0

    for index, label in enumerate(option_labels):

        if options[label]["id"] == selected_target_id:
            default_index = index
            break

    # Synchronize the selector with the pipeline selection.
    # The key is reset only when the pipeline button selects
    # a different target.
    selected_label_key = "recruitment_player_selector"

    if selected_target_id is not None:

        desired_label = next(
            (
                label
                for label in option_labels
                if options[label]["id"] == selected_target_id
            ),
            None,
        )

        if desired_label is not None:
            st.session_state[selected_label_key] = desired_label

    elif (
        selected_label_key in st.session_state
        and st.session_state[selected_label_key]
        not in option_labels
    ):
        st.session_state[selected_label_key] = option_labels[0]

    def clear_pipeline_selection():
        st.session_state.pop(
            "selected_recruitment_id",
            None,
        )

    selected_label = st.selectbox(
        "Select Recruitment Target",
        option_labels,
        index=default_index,
        key=selected_label_key,
        on_change=clear_pipeline_selection,
    )

    target = options[selected_label]

    st.markdown(
        f"**{target['player_name']}** — "
        f"{target['team_name']}"
    )

    st.caption(
        f"Position: {target['position']} | "
        f"Current Status: {target['status']} | "
        f"Priority: {target['priority']}"
    )


    # --------------------------------------------------
    # EDIT RECRUITMENT TARGET
    # --------------------------------------------------

    with st.form(
        f"recruitment_edit_form_{target['id']}"
    ):

        status = st.selectbox(
            "Recruitment Status",
            RECRUITMENT_STATUSES,
            index=RECRUITMENT_STATUSES.index(
                target["status"]
            ),
        )

        priority = st.selectbox(
            "Recruitment Priority",
            RECRUITMENT_PRIORITIES,
            index=RECRUITMENT_PRIORITIES.index(
                target["priority"]
            ),
        )

        notes = st.text_area(
            "Recruitment Notes",
            value=target["notes"] or "",
            height=170,
            placeholder=(
                "Why is this player being considered? "
                "What should be investigated further?"
            ),
        )

        save_changes = st.form_submit_button(
            "Save Recruitment Changes",
            type="primary",
            use_container_width=True,
        )

        if save_changes:

            updated = update_recruitment_target(
                target_id=int(target["id"]),
                status=status,
                priority=priority,
                notes=notes.strip(),
            )

            if updated:
                st.success(
                    "Recruitment target updated successfully."
                )

                st.rerun()

            else:
                st.error(
                    "Unable to update this recruitment target."
                )
#Remove Recruitment Target
    st.divider()

    with st.expander("Remove Recruitment Target"):

        st.warning(
            "Removing this player from recruitment targets "
            "will not delete their saved scouting reports."
        )

        confirm_remove = st.checkbox(
            (
                f"I confirm that I want to remove "
                f"{target['player_name']}."
            ),
            key=f"confirm_remove_{target['id']}",
        )

        if st.button(
            "Remove Target",
            disabled=not confirm_remove,
            key=f"remove_target_{target['id']}",
            use_container_width=True,
        ):

            removed = remove_recruitment_target(
                int(target["id"])
            )

            if removed:

                st.session_state.pop(
                    "selected_recruitment_id",
                    None,
                )

                st.session_state.pop(
                    "recruitment_player_selector",
                    None,
                )

                st.success(
                    "Recruitment target removed successfully."
                )

                st.rerun()

            else:
                st.error(
                    "Unable to remove recruitment target."
                )

st.divider()

st.caption(
    "ScoutLocal | Recruitment information "
    "is stored in the local SQLite database."
)
