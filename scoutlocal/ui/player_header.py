
from html import escape

import streamlit as st


# display the player's main information card
def render_player_header(player, competition=None, season=None):
    name = escape(str(player["player_name"]))
    team = escape(str(player["team_name"]))
    position = escape(str(player["primary_position_group"]))

    # build competition details when available
    details = []

    if competition:
        details.append(escape(str(competition)))

    if season:
        details.append(escape(str(season)))

    competition_text = " | ".join(details)

    st.markdown(
        f"""
<div style="background:linear-gradient(120deg,#16243A,#0B1423);border:1px solid #263852;border-radius:16px;padding:30px;margin-bottom:20px;">
    <p style="color:#60A5FA;font-size:12px;font-weight:700;letter-spacing:2px;margin:0;">
        PLAYER SCOUTING REPORT
    </p>
    <h1 style="color:white;font-size:36px;margin:14px 0 8px;">
        {name}
    </h1>
    <p style="color:#D5E3F3;font-size:16px;margin:0;">
        {team} | {position}
    </p>
    <p style="color:#91A8C5;font-size:13px;margin:10px 0 0;">
        {competition_text}
    </p>
</div>
        """,
        unsafe_allow_html=True,
    )
