
from pathlib import Path

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="ScoutLocal | Scouting Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "player_metrics_with_positions.csv"

MIN_RANKING_MINUTES = 900


@st.cache_data
def load_players():
    if not DATA_PATH.exists():
        return pd.DataFrame()

    return pd.read_csv(DATA_PATH)


df = load_players()


# ---------------------------------------------
# CORPORATE STYLING
# ---------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    .main-header {
        background: linear-gradient(
            120deg,
            #101d32 0%,
            #173c63 65%,
            #215680 100%
        );
        padding: 34px 38px;
        border-radius: 16px;
        color: white;
        margin-bottom: 20px;
    }

    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 750;
        margin-bottom: 10px;
    }

    .main-header p {
        color: #c5d6e9;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .eyebrow {
        color: #86b8ee;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 12px;
    }

    .section-heading {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 12px;
        margin-bottom: 6px;
    }

    .dashboard-card {
        padding: 22px;
        border: 1px solid rgba(128, 145, 165, 0.25);
        border-radius: 14px;
        min-height: 150px;
        margin-bottom: 10px;
    }

    .dashboard-card h3 {
        font-size: 1.05rem;
        margin-bottom: 10px;
    }

    .dashboard-card p {
        color: #8998aa;
        font-size: 0.91rem;
        line-height: 1.6;
        margin-bottom: 0;
    }

    .status-box {
        background: rgba(91, 140, 190, 0.08);
        border-left: 3px solid #4f9ce8;
        padding: 15px 20px;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------
# HEADER
# ---------------------------------------------

st.markdown(
    """
    <div class="main-header">
        <div class="eyebrow">
            SCOUTLOCAL / FOOTBALL INTELLIGENCE
        </div>
        <h1>Scouting Command Centre</h1>
        <p>
            Discover talent. Analyse performance.
            Build evidence-based recruitment decisions.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------
# DATASET OVERVIEW
# ---------------------------------------------

if df.empty:
    st.error(
        "Player data could not be loaded. "
        "Check data/player_metrics_with_positions.csv."
    )
    st.stop()


player_records = len(df)

unique_players = df["player_id"].nunique()

total_clubs = df["team_name"].nunique()

eligible_players = int(
    (
        (df["minutes"] >= MIN_RANKING_MINUTES)
        & (df["primary_position_group"] != "Unknown")
        & (df["primary_position_group"] != "Goalkeeper")
    ).sum()
)

st.markdown(
    '<div class="section-heading">Database Overview</div>',
    unsafe_allow_html=True,
)

st.caption(
    "Indian Super League | 2021/22 Season | "
    "StatsBomb Open Data"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Player Records",
    f"{player_records:,}",
)

col2.metric(
    "Unique Players",
    f"{unique_players:,}",
)

col3.metric(
    "Clubs Covered",
    f"{total_clubs:,}",
)

col4.metric(
    "Ranking-Eligible Records",
    f"{eligible_players:,}",
)

st.caption(
    "Ranking eligibility is based on at least 900 minutes "
    "and an identified outfield position. "
    "Player records may include multiple team entries "
    "for the same footballer."
)

st.divider()


# ---------------------------------------------
# MAIN SCOUTING WORKSPACE
# ---------------------------------------------

st.markdown(
    '<div class="section-heading">Scouting Workspace</div>',
    unsafe_allow_html=True,
)

st.write(
    "Access the tools used to discover players, "
    "evaluate performance and investigate recruitment targets."
)

left, middle, right = st.columns(3, gap="large")

with left:
    st.markdown(
        """
        <div class="dashboard-card">
            <h3>🔎 Player Intelligence</h3>
            <p>
                Explore footballers, filter by playing role,
                rank statistical profiles and investigate
                individual performances.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/Scout.py",
        label="Open Player Intelligence",
        icon="🔎",
        use_container_width=True,
    )

with middle:
    st.markdown(
        """
        <div class="dashboard-card">
            <h3>⚔️ Player Comparison</h3>
            <p>
                Compare footballers in the same position
                using standardized statistics, radar
                charts and scouting insights.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/Compare.py",
        label="Compare Footballers",
        icon="⚔️",
        use_container_width=True,
    )

with right:
    st.markdown(
        """
        <div class="dashboard-card">
            <h3>📋 Recruitment Shortlist</h3>
            <p>
                Organize promising players and prepare
                for future recruitment evaluations
                and tracking.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if (BASE_DIR / "pages" / "Shortlist.py").exists():
        st.page_link(
            "pages/Shortlist.py",
            label="Open Shortlist",
            icon="📋",
            use_container_width=True,
        )
    else:
        st.caption("Shortlist workspace is not available yet.")

st.divider()


# ---------------------------------------------
# UPCOMING RECRUITMENT TOOLS
# ---------------------------------------------

st.markdown(
    '<div class="section-heading">Recruitment Operations</div>',
    unsafe_allow_html=True,
)

st.caption(
    "These tools are part of the next development stages."
)

report_col, pipeline_col = st.columns(2, gap="large")

with report_col:
    with st.container(border=True):
        st.subheader("📝 Scouting Reports")

        st.write(
            "Record your own assessments of a player, "
            "including technical ability, tactical awareness, "
            "strengths, weaknesses and supporting evidence."
        )

        st.info("Coming next: Report Builder")

with pipeline_col:
    with st.container(border=True):
        st.subheader("🎯 Recruitment Pipeline")

        st.write(
            "Track candidates through your scouting process, "
            "from initial identification to recruitment "
            "recommendation."
        )

        st.info("Planned: Recruitment tracking")

st.divider()


# ---------------------------------------------
# CURRENT DATA COVERAGE
# ---------------------------------------------

st.markdown(
    '<div class="section-heading">Data Coverage</div>',
    unsafe_allow_html=True,
)

coverage_col, learning_col = st.columns(
    [1.3, 1],
    gap="large",
)

with coverage_col:
    with st.container(border=True):
        st.subheader("🌍 Competition Coverage")

        st.markdown("**Indian Super League**")
        st.caption("2021/22 Season")

        st.write(
            f"{total_clubs:,} clubs represented, "
            f"{unique_players:,} unique footballers "
            "and position-specific scouting metrics."
        )

        st.caption(
            "Additional leagues and seasons will be "
            "introduced after the multi-league data "
            "pipeline is implemented."
        )

with learning_col:
    with st.container(border=True):
        st.subheader("📚 ScoutLocal Academy")

        st.write(
            "Learn football scouting statistics, "
            "percentile rankings and performance "
            "interpretation through beginner-friendly "
            "explanations and interactive examples."
        )

        st.caption(
            "Currently accessible through the "
            "learning tabs in Scout and Compare."
        )


# ---------------------------------------------
# FOOTER
# ---------------------------------------------

st.divider()

st.caption(
    "ScoutLocal | Football Scouting & Recruitment Intelligence "
    "| Powered by StatsBomb Open Data"
)
