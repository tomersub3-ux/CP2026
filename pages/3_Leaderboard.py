"""
Leaderboard Page - User rankings.
"""
import streamlit as st
import pandas as pd
from auth import is_logged_in, is_admin, get_current_username, logout
from leaderboard import get_leaderboard

# Redirect if not logged in
if not is_logged_in():
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="Leaderboard | CP Platform", page_icon="🏅", layout="wide")

# Sidebar
with st.sidebar:
    st.markdown(f"### 👋 **{get_current_username()}**")
    if is_admin():
        st.markdown("🛡️ *Admin*")
    st.divider()
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("streamlit_app.py")

# Main content
st.title("🏅 Leaderboard")

# Time filter
time_filter = st.radio(
    "Time Period:",
    ["All Time", "Monthly", "Weekly"],
    horizontal=True
)

filter_map = {
    "All Time": "all",
    "Monthly": "monthly",
    "Weekly": "weekly"
}

# Get leaderboard
leaderboard = get_leaderboard(filter_map[time_filter])

if not leaderboard:
    st.info("No data yet. Solve some problems to appear on the leaderboard!")
else:
    # Show top 3 with special formatting
    if len(leaderboard) >= 1:
        st.markdown("### 🥇 Top Performers")
        
        cols = st.columns(min(3, len(leaderboard)))
        medals = ["🥇", "🥈", "🥉"]
        
        for i, col in enumerate(cols):
            if i < len(leaderboard):
                entry = leaderboard[i]
                with col:
                    st.markdown(f"### {medals[i]} {entry['username']}")
                    st.metric("Points", entry['total_points'])
                    st.caption(f"{entry['solved_count']} problems solved")
        
        st.divider()
    
    # Full table
    st.markdown("### 📊 Full Rankings")
    
    # Create DataFrame
    df = pd.DataFrame(leaderboard)
    df = df.rename(columns={
        "rank": "Rank",
        "username": "Username",
        "solved_count": "Problems Solved",
        "total_points": "Total Points"
    })
    
    # Style the current user
    current_user = get_current_username()
    
    def highlight_user(row):
        if row["Username"] == current_user:
            return ["background-color: #1e3a5f"] * len(row)
        return [""] * len(row)
    
    styled_df = df.style.apply(highlight_user, axis=1)
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True
    )
