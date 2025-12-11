"""
Competitive Programming Platform - Main Entry Point
"""
import streamlit as st
from auth import (
    ensure_db_initialized, login, register, logout,
    is_logged_in, is_admin, get_current_username
)

# Initialize database on startup
ensure_db_initialized()

# Page config
st.set_page_config(
    page_title="CP Platform",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def show_login_page():
    """Display login/register forms."""
    st.markdown('<p class="main-header">🏆 CP Platform</p>', unsafe_allow_html=True)
    st.markdown("A competitive programming practice platform with Codeforces integration.")
    
    st.divider()
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit:
                if login(username, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_btn = st.form_submit_button("Register", use_container_width=True)
            
            if register_btn:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = register(new_username, new_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)


def show_home_page():
    """Display home page for logged-in users."""
    # Sidebar with user info
    with st.sidebar:
        st.markdown(f"### 👋 Welcome, **{get_current_username()}**!")
        if is_admin():
            st.markdown("🛡️ *Admin*")
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Main content
    st.markdown('<p class="main-header">🏆 CP Platform</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 Dashboard")
        st.markdown("View your profile, stats, and sync with Codeforces.")
        if st.button("Go to Dashboard →", key="dash_btn"):
            st.switch_page("pages/1_Dashboard.py")
    
    with col2:
        st.markdown("### 📚 Problems")
        st.markdown("Browse and solve competitive programming problems.")
        if st.button("View Problems →", key="prob_btn"):
            st.switch_page("pages/2_Problems.py")
    
    with col3:
        st.markdown("### 🏅 Leaderboard")
        st.markdown("See how you rank against other users.")
        if st.button("View Leaderboard →", key="lead_btn"):
            st.switch_page("pages/3_Leaderboard.py")
    
    if is_admin():
        st.divider()
        st.markdown("### 🛡️ Admin Panel")
        st.markdown("Add and manage problems.")
        if st.button("Go to Admin Panel →", key="admin_btn"):
            st.switch_page("pages/4_Admin.py")


# Main routing
if is_logged_in():
    show_home_page()
else:
    show_login_page()
