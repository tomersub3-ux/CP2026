"""
Admin Page - Add and manage problems.
"""
import streamlit as st
from auth import is_logged_in, is_admin, get_current_username, get_current_user_id, logout
from models import get_session, Problem
import re

# Redirect if not logged in or not admin
if not is_logged_in():
    st.switch_page("streamlit_app.py")

if not is_admin():
    st.error("Access denied. Admin only.")
    st.stop()

st.set_page_config(page_title="Admin | CP Platform", page_icon="🛡️", layout="wide")

# Sidebar
with st.sidebar:
    st.markdown(f"### 🛡️ **{get_current_username()}** (Admin)")
    st.divider()
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("streamlit_app.py")
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("streamlit_app.py")

# Main content
st.title("🛡️ Admin Panel")

tab1, tab2 = st.tabs(["➕ Add Problem", "📋 Manage Problems"])

with tab1:
    st.subheader("Add New Problem")
    
    with st.form("add_problem_form"):
        title = st.text_input("Problem Title *", placeholder="e.g., Two Sum")
        problem_url = st.text_input("Problem URL", placeholder="https://codeforces.com/...")
        points = st.number_input("Points *", min_value=1, max_value=1000, value=10)
        
        st.markdown("#### Codeforces Details (Optional)")
        st.caption("For auto-sync with Codeforces submissions")
        
        col1, col2 = st.columns(2)
        with col1:
            cf_contest_id = st.number_input("Contest ID", min_value=0, value=0, help="e.g., 1234")
        with col2:
            cf_problem_index = st.text_input("Problem Index", placeholder="e.g., A, B1, C")
        
        submitted = st.form_submit_button("Add Problem", type="primary", use_container_width=True)
        
        if submitted:
            if not title:
                st.error("Title is required.")
            else:
                session = get_session()
                try:
                    # Parse CF URL if provided
                    parsed_contest = cf_contest_id if cf_contest_id > 0 else None
                    parsed_index = cf_problem_index.strip().upper() if cf_problem_index else None
                    
                    # Try to extract from URL if not provided
                    if problem_url and not parsed_contest:
                        match = re.search(r'codeforces\.com/(?:contest|problemset/problem)/(\d+)/(\w+)', problem_url)
                        if match:
                            parsed_contest = int(match.group(1))
                            parsed_index = match.group(2).upper()
                    
                    problem = Problem(
                        title=title,
                        problem_url=problem_url if problem_url else None,
                        points=points,
                        cf_contest_id=parsed_contest,
                        cf_problem_index=parsed_index,
                        added_by=get_current_user_id()
                    )
                    session.add(problem)
                    session.commit()
                    st.success(f"Problem '{title}' added with {points} points!")
                except Exception as e:
                    session.rollback()
                    st.error(f"Error: {str(e)}")
                finally:
                    session.close()

with tab2:
    st.subheader("Existing Problems")
    
    session = get_session()
    try:
        problems = session.query(Problem).order_by(Problem.created_at.desc()).all()
        
        if not problems:
            st.info("No problems added yet.")
        else:
            for problem in problems:
                with st.expander(f"📝 {problem.title} ({problem.points} pts)"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**URL:** {problem.problem_url or 'N/A'}")
                        if problem.cf_contest_id:
                            st.markdown(f"**CF:** Contest {problem.cf_contest_id}, Problem {problem.cf_problem_index}")
                        st.caption(f"Added: {problem.created_at.strftime('%Y-%m-%d %H:%M')}")
                    
                    with col2:
                        if st.button("🗑️ Delete", key=f"del_{problem.id}"):
                            del_session = get_session()
                            try:
                                del_session.query(Problem).filter(Problem.id == problem.id).delete()
                                del_session.commit()
                                st.rerun()
                            finally:
                                del_session.close()
    finally:
        session.close()
