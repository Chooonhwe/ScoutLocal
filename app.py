
import streamlit as st

# configure the dashboard
st.set_page_config(
    page_title="ScoutLocal | Home",
    page_icon="⚽",
    layout="wide",
)

# scoutlocal home page
st.markdown(
    """
<div style="padding:40px;background:linear-gradient(120deg,#16243A,#0B1423);border:1px solid #263852;border-radius:16px;">
    <p style="color:#60A5FA;letter-spacing:2px;font-size:13px;font-weight:700;">FOOTBALL INTELLIGENCE PLATFORM</p>
    <h1 style="color:white;font-size:46px;margin:12px 0;">SCOUTLOCAL</h1>
    <p style="color:#A8BCD3;font-size:17px;">
        Discover talent. Analyse performance. Make smarter recruitment decisions.
    </p>
</div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.header("Your Football Intelligence Workspace")

st.write(
    "ScoutLocal brings player discovery, statistical analysis, "
    "comparisons and recruitment scouting together in one platform."
)

st.divider()

# main navigation cards
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.subheader("🔎 Discover Players")
        st.write("Search players using advanced statistical and positional filters.")
        st.page_link("pages/Discover.py", label="Open Player Discovery")

    with st.container(border=True):
        st.subheader("📊 Player Profiles")
        st.write("Explore scouting statistics, percentiles and player insights.")
        st.page_link("pages/Player_Profile.py", label="View Player Profiles")

with col2:
    with st.container(border=True):
        st.subheader("⚔️ Compare Players")
        st.write("Compare players through positional metrics and visual analysis.")
        st.page_link("pages/Compare.py", label="Open Comparisons")

    with st.container(border=True):
        st.subheader("⭐ Recruitment Shortlist")
        st.write("Organise and review potential recruitment targets.")
        st.page_link("pages/Shortlist.py", label="Open Shortlist")

st.divider()

st.caption("ScoutLocal | Football Scouting & Recruitment Analytics")
