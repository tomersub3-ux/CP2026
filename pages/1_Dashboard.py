"""
Dashboard Page - User profile, stats, and Codeforces sync.
"""
import streamlit as st
from auth import (
    is_logged_in, is_admin, get_current_username, get_current_user_id,
    logout, change_password, update_cf_handle, get_user_cf_handle
)
from codeforces_api import validate_handle, sync_user_progress, get_user_info
from leaderboard import get_user_stats

# Redirect if not logged in
if not is_logged_in():
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="Dashboard | CP Platform", page_icon="📊", layout="wide")

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
st.title("📊 Dashboard")

user_id = get_current_user_id()

# Stats section
st.subheader("📈 Your Stats")
stats = get_user_stats(user_id)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🏅 Rank", f"#{stats['rank']}" if stats['rank'] else "N/A")
with col2:
    st.metric("✅ Problems Solved", stats['solved_count'])
with col3:
    st.metric("⭐ Total Points", stats['total_points'])

st.divider()

# Codeforces section
st.subheader("🔗 Codeforces Integration")

current_handle = get_user_cf_handle(user_id)
if current_handle:
    st.success(f"Connected: **{current_handle}**")
    
    # Show CF info
    cf_info = get_user_info(current_handle)
    if cf_info:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CF Rating", cf_info.get("rating", "Unrated"))
        with col2:
            st.metric("CF Rank", cf_info.get("rank", "unrated").title())

col1, col2 = st.columns(2)

with col1:
    with st.form("cf_handle_form"):
        new_handle = st.text_input("Codeforces Handle", value=current_handle or "")
        if st.form_submit_button("Update Handle"):
            if new_handle:
                valid, msg = validate_handle(new_handle)
                if valid:
                    success, update_msg = update_cf_handle(user_id, new_handle)
                    if success:
                        st.success(f"{msg}")
                        st.rerun()
                    else:
                        st.error(update_msg)
                else:
                    st.error(msg)
            else:
                update_cf_handle(user_id, "")
                st.info("Handle cleared.")
                st.rerun()

with col2:
    if current_handle:
        if st.button("🔄 Sync Progress", use_container_width=True, type="primary"):
            with st.spinner("Syncing with Codeforces..."):
                count, msg = sync_user_progress(user_id, current_handle)
                if count > 0:
                    st.success(msg)
                    st.rerun()
                else:
                    st.info(msg)

st.divider()

# Password change section
st.subheader("🔐 Change Password")

with st.form("password_form"):
    current_pwd = st.text_input("Current Password", type="password")
    new_pwd = st.text_input("New Password", type="password")
    confirm_pwd = st.text_input("Confirm New Password", type="password")
    
    if st.form_submit_button("Change Password"):
        if new_pwd != confirm_pwd:
            st.error("New passwords do not match.")
        else:
            success, msg = change_password(user_id, current_pwd, new_pwd)
            if success:
                st.success(msg)
            else:
                st.error(msg)
