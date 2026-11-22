
from pathlib import Path

import pandas as pd
import streamlit as st

from scoutlocal.metrics.profiles import SCOUTING_PROFILES
from scoutlocal.ui.player_header import render_player_header
from scoutlocal.ui.radar_chart import render_radar_chart
from scoutlocal.ui.metrics_card import (
    render_player_metrics,
    render_metric_breakdown,
)
from scoutlocal.ui.scouting_insights import render_scouting_insights
from scoutlocal.ui.metric_glossary import render_metric_glossary
from scoutlocal.ui.view_mode import (
    render_view_mode,
    is_beginner_mode,
)
from scoutlocal.ui.scouting_filters import render_advanced_filters
from scoutlocal.database.scouting_db import get_player_reports

st.set_page_config(
    page_title="ScoutLocal | Talent Intelligence",
    page_icon="SL",
    layout="wide",
)

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "player_metrics_with_positions.csv"
)

MIN_MINUTES = 900
PAGE_SIZE = 8


@st.cache_data
def load_players():
    return pd.read_csv(DATA_PATH)


def metric_label(metric):
    return metric.removesuffix("_per90").replace("_", " ").title()


# Role presets use the metrics already available in ScoutLocal.
# Any unavailable metric is excluded automatically.
ROLE_PRESETS = {
    "Full Back": {
        "All-Round Full-Back": [],
        "Attacking Full-Back": [
            "progressive_carries_per90",
            "final_third_entries_per90",
            "progressive_passes_per90",
        ],
        "Defensive Full-Back": [
            "tackles_won_per90",
            "interceptions_won_per90",
        ],
    },
    "Center Back": {
        "All-Round Centre-Back": [],
        "Ball-Progressing Centre-Back": [
            "progressive_passes_per90",
            "progressive_carries_per90",
        ],
        "Defensive Centre-Back": [
            "tackles_won_per90",
            "interceptions_won_per90",
        ],
    },
    "Defensive Midfielder": {
        "All-Round Defensive Midfielder": [],
        "Ball-Winning Midfielder": [
            "tackles_won_per90",
            "interceptions_won_per90",
        ],
    },
    "Central Midfielder": {
        "All-Round Central Midfielder": [],
        "Progressive Midfielder": [
            "progressive_passes_per90",
            "progressive_carries_per90",
            "final_third_entries_per90",
        ],
    },
    "Attacking Midfielder": {
        "All-Round Attacking Midfielder": [],
        "Progressive Attacking Midfielder": [
            "progressive_passes_per90",
            "progressive_carries_per90",
            "final_third_entries_per90",
        ],
    },
    "Winger": {
        "All-Round Winger": [],
        "Direct Winger": [
            "progressive_carries_per90",
            "final_third_entries_per90",
        ],
    },
    "Forward": {
        "All-Round Forward": [],
        "Link-Up Forward": [
            "progressive_passes_per90",
            "final_third_entries_per90",
        ],
    },
}


def get_role_options(position):
    presets = ROLE_PRESETS.get(position, {})

    if not presets:
        return {"General Statistical Profile": []}

    return presets


def get_focus_metrics(position, role, dataframe):
    available = [
        metric
        for metric in SCOUTING_PROFILES.get(position, [])
        if metric in dataframe.columns
    ]

    requested = ROLE_PRESETS.get(position, {}).get(role, [])

    # An empty preset means use the entire positional profile.
    if not requested:
        return available

    focus = [
        metric
        for metric in requested
        if metric in available
    ]

    return focus if focus else available


def calculate_percentiles(dataframe, position):
    eligible = dataframe[
        (dataframe["primary_position_group"] == position)
        & (dataframe["minutes"] >= MIN_MINUTES)
    ].copy()

    for metric in SCOUTING_PROFILES.get(position, []):
        if metric not in eligible.columns:
            continue

        eligible[f"pct_{metric}"] = (
            eligible[metric]
            .rank(method="average", pct=True)
            .mul(100)
        )

    return eligible


def build_player_metrics(player, reference, position):
    metrics = []

    for metric in SCOUTING_PROFILES.get(position, []):
        if metric not in player.index:
            continue

        raw_value = player.get(metric)
        percentile = None

        if (
            float(player["minutes"]) >= MIN_MINUTES
            and not reference.empty
            and metric in reference.columns
        ):
            ranking = (
                reference[metric]
                .rank(method="average", pct=True)
                .mul(100)
            )

            result = ranking.get(player.name)

            if pd.notna(result):
                percentile = float(result)

        metrics.append({
            "metric": metric,
            "value": (
                float(raw_value)
                if pd.notna(raw_value)
                else None
            ),
            "percentile": percentile,
        })

    return metrics


def candidate_key(player):
    return (
        int(player["player_id"]),
        int(player["team_id"]),
    )


def show_player_intelligence(player, dataframe):
    position = str(player["primary_position_group"])

    reference = dataframe[
        (dataframe["primary_position_group"] == position)
        & (dataframe["minutes"] >= MIN_MINUTES)
    ].copy()

    metrics = build_player_metrics(
        player,
        reference,
        position,
    )

    render_player_header(
        player,
        competition="Indian Super League",
        season="2021/22",
    )

    if float(player["minutes"]) < MIN_MINUTES:
        st.warning(
            "This footballer has fewer than 900 recorded "
            "minutes. Per-90 data is displayed, but "
            "positional percentile rankings are unavailable."
        )

    overview, breakdown, insights, reports_tab, academy = st.tabs([
    "Overview",
    "Statistics",
    "Scouting Insights",
    "Reports",
    "Learn",
])

    with overview:
        render_player_metrics(
            player,
            len(reference),
            metrics,
        )

        render_radar_chart(
            metrics,
            str(player["player_name"]),
        )

        if is_beginner_mode():
            st.info(
                "A radar chart shows how a player's "
                "statistical activity compares with others "
                "in the same position. Higher values are "
                "not automatically better football ability."
            )

    with breakdown:
        render_metric_breakdown(metrics)

    with insights:
        render_scouting_insights(
            metrics,
            len(reference),
        )

    # Display saved reports for the selected player
    with reports_tab:
        st.subheader("Scouting Report History")

        player_reports = get_player_reports(
            int(player["player_id"]),
            int(player["team_id"]),
        )

        st.metric("Saved Reports", len(player_reports))

        if not player_reports:
            st.info(
                "No scouting reports have been saved "
                "for this player yet."
            )
        else:
            for report in player_reports:
                title = (
                    f"Report #{report['id']} | "
                    f"{report['observation_date']} | "
                    f"{report['recommendation']}"
                )

                with st.expander(title):
                    st.write(
                        f"**Scout:** {report['scout_name']}"
                    )

                    st.write(
                        f"**Match Context:** "
                        f"{report['match_context'] or 'Not recorded'}"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Technical",
                        f"{report['technical_rating']}/5"
                        if report["technical_rating"] is not None
                        else "Not rated",
                    )

                    col2.metric(
                        "Tactical",
                        f"{report['tactical_rating']}/5"
                        if report["tactical_rating"] is not None
                        else "Not rated",
                    )

                    col3.metric(
                        "Physical",
                        f"{report['physical_rating']}/5"
                        if report["physical_rating"] is not None
                        else "Not rated",
                    )

                    st.markdown("**Strengths**")
                    st.write(report["strengths"] or "Not recorded")

                    st.markdown("**Development Areas**")
                    st.write(report["weaknesses"] or "Not recorded")

                    st.markdown("**Observations**")
                    st.write(report["observations"] or "Not recorded")

        st.caption(
            "Scouting reports are retrieved from "
            "your ScoutLocal database."
        )

    with academy:
        render_metric_glossary([
            item["metric"]
            for item in metrics
        ])


# -----------------------------------------------------
# DATA AND HEADER
# -----------------------------------------------------

df = load_players()

st.title("ScoutLocal | Talent Intelligence")

st.caption(
    "Discover, evaluate and investigate footballers "
    "using transparent statistical evidence."
)

render_view_mode()

st.divider()

# -----------------------------------------------------
# SCOUTING SEARCH
# -----------------------------------------------------

st.subheader("01 / Build Your Scouting Search")

search_left, search_middle, search_right = st.columns(3)

positions = sorted(SCOUTING_PROFILES.keys())

with search_left:
    selected_position = st.selectbox(
        "Playing Position",
        positions,
        index=positions.index("Full Back")
        if "Full Back" in positions else 0,
    )

role_options = get_role_options(selected_position)

with search_middle:
    selected_role = st.selectbox(
        "Scouting Objective",
        list(role_options.keys()),
        help=(
            "Choose the statistical characteristics "
            "you want to explore."
        ),
    )

with search_right:
    minimum_minutes = st.number_input(
        "Minimum Minutes Played",
        min_value=0,
        value=900,
        step=90,
    )

search_col, team_col = st.columns([2, 1])

with search_col:
    player_search = st.text_input(
        "Search by Player Name",
        placeholder="Optional — leave blank to discover players",
    )

with team_col:
    team_options = ["All Clubs"] + sorted(
        df["team_name"].dropna().unique().tolist()
    )

    selected_team = st.selectbox(
        "Club",
        team_options,
    )

focus_metrics = get_focus_metrics(
    selected_position,
    selected_role,
    df,
)

with st.expander("How this scouting search works"):
    st.write(
        "ScoutLocal ranks statistical activity within "
        "the selected playing position. The current "
        "ranking reference includes players with at "
        "least 900 minutes."
    )

    st.markdown("**Metrics used for this search:**")

    for metric in focus_metrics:
        st.write(f"• {metric_label(metric)}")

    st.caption(
        "This is a transparent statistical comparison, "
        "not an AI prediction or an overall ability rating."
    )

# -----------------------------------------------------
# BUILD THE TALENT LEADERBOARD
# -----------------------------------------------------

eligible = calculate_percentiles(
    df,
    selected_position,
)

candidates = df[
    df["primary_position_group"] == selected_position
].copy()

candidates = candidates[
    candidates["minutes"] >= minimum_minutes
]

if selected_team != "All Clubs":
    candidates = candidates[
        candidates["team_name"] == selected_team
    ]

if player_search.strip():
    candidates = candidates[
        candidates["player_name"].str.contains(
            player_search.strip(),
            case=False,
            regex=False,
            na=False,
        )
    ]

percentile_columns = [
    f"pct_{metric}"
    for metric in focus_metrics
    if f"pct_{metric}" in eligible.columns
]

if percentile_columns:
    eligible["scouting_fit"] = eligible[
        percentile_columns
    ].mean(axis=1, skipna=False)

    candidates = candidates.join(
        eligible[["scouting_fit"]],
        how="left",
    )
else:
    candidates["scouting_fit"] = float("nan")

# Apply advanced scouting filters before displaying results.
# Preserve the original candidate indices so player selection
# and positional percentile calculations stay consistent.

candidates = render_advanced_filters(
    candidates=candidates,
    eligible=eligible,
    focus_metrics=focus_metrics,
)

# Rank matching candidates by statistical fit.
candidates = candidates.sort_values(
    ["scouting_fit", "minutes", "player_name"],
    ascending=[False, False, True],
    na_position="last",
)

# -----------------------------------------------------
# SUMMARY
# -----------------------------------------------------

st.divider()
st.subheader("02 / Talent Leaderboard")

total_found = len(candidates)
total_ranked = int(
    candidates["scouting_fit"].notna().sum()
)
clubs_found = candidates["team_name"].nunique()

summary1, summary2, summary3 = st.columns(3)

summary1.metric("Candidates Found", total_found)
summary2.metric("Ranked Candidates", total_ranked)
summary3.metric("Clubs Represented", clubs_found)

if is_beginner_mode():
    st.info(
        "Players are ordered by their average percentile "
        "across the selected scouting metrics. "
        "This shows statistical fit for your search, "
        "not who is the best footballer."
    )

# -----------------------------------------------------
# RESULTS AND INTELLIGENCE WORKSPACE
# -----------------------------------------------------

results_col, intelligence_col = st.columns(
    [1, 1.65],
    gap="large",
)

with results_col:
    st.markdown("#### Player Database")

    st.caption(
        f"{len(candidates)} player records match your scouting search."
    )

    if candidates.empty:
        st.info(
            "No players match your filters. "
            "Try changing the position, club, or minimum minutes."
        )

    else:
        # Prepare a clean table for player discovery.
        leaderboard = candidates[
            [
                "player_name",
                "team_name",
                "primary_position_group",
                "minutes",
                "scouting_fit",
            ]
        ].copy()

        leaderboard.columns = [
            "Player",
            "Club",
            "Position",
            "Minutes",
            "Statistical Fit",
        ]

        # Select a row to open its player intelligence panel.
        selection_event = st.dataframe(
            leaderboard,
            hide_index=True,
            use_container_width=True,
            height=520,
            on_select="rerun",
            selection_mode="single-row",
            key="scout_player_table",
            column_config={
                "Player": st.column_config.TextColumn(
                    "Player",
                    width="medium",
                ),
                "Club": st.column_config.TextColumn(
                    "Club",
                    width="medium",
                ),
                "Position": st.column_config.TextColumn(
                    "Position",
                    width="medium",
                ),
                "Minutes": st.column_config.NumberColumn(
                    "Minutes",
                    format="%.2f",
                ),
                "Statistical Fit": st.column_config.NumberColumn(
                    "Statistical Fit",
                    format="%.2f",
                    help=(
                        "Average positional percentile across "
                        "the selected scouting metrics. "
                        "Not an overall ability rating."
                    ),
                ),
            },
        )

        st.caption(
            "Click a player row to view their analysis. "
            "Click a column heading to sort the table."
        )

        selected_rows = selection_event.selection.rows

        if selected_rows:
            selected_row = selected_rows[0]

            # Row selections refer to displayed table positions.
            # Use iloc to retrieve the corresponding candidate.
            selected_candidate = candidates.iloc[selected_row]

            st.session_state["scout_selection"] = (
                int(selected_candidate["player_id"]),
                int(selected_candidate["team_id"]),
            )


with intelligence_col:
    st.markdown("#### 03 / Player Intelligence")

    selected_key = st.session_state.get(
        "scout_selection"
    )

    if selected_key is None:
        st.info(
            "Select a player in the database table "
            "to view their complete scouting profile here."
        )

    else:
        selection = candidates[
            (candidates["player_id"] == selected_key[0])
            & (candidates["team_id"] == selected_key[1])
        ]

        if selection.empty:
            st.info(
                "Your previously selected player isn't "
                "in the current results. Choose another "
                "candidate or adjust your filters."
            )
        else:
            selected_player = selection.iloc[0]

            # Keep the selection available for future
            # comparison and recruitment features.
            st.session_state["selected_player_id"] = int(
                selected_player["player_id"]
            )
            st.session_state["selected_team_id"] = int(
                selected_player["team_id"]
            )

            show_player_intelligence(
                selected_player,
                df,
            )

            if st.button(
                "Create Scouting Report",
                type="primary",
                use_container_width=True,
                key="scout_create_report",
            ):
                st.session_state["selected_player_id"] = int(
                    selected_player["player_id"]
                )
                st.session_state["selected_team_id"] = int(
                    selected_player["team_id"]
                )
                st.switch_page("pages/Reports.py")

st.divider()

st.caption(
    "ScoutLocal | StatsBomb Open Data | "
    "Indian Super League 2021/22 | "
    "Statistical scouting support, not a substitute "
    "for match footage and live observation."
)
