"""
Problems Page - Browse and track problem completions.
"""
import streamlit as st
from auth import is_logged_in, is_admin, get_current_username, get_current_user_id, logout
from models import get_session, Problem, Submission
from leaderboard import get_user_solved_problems
from datetime import datetime

# Redirect if not logged in
if not is_logged_in():
    st.switch_page("streamlit_app.py")

st.set_page_config(page_title="Problems | CP Platform", page_icon="📚", layout="wide")

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
st.title("📚 Problems")

user_id = get_current_user_id()
solved_ids = get_user_solved_problems(user_id)

# Get all problems
session = get_session()
try:
    problems = session.query(Problem).order_by(Problem.created_at.desc()).all()
    
    if not problems:
        st.info("No problems added yet. Ask an admin to add some!")
    else:
        # Stats
        st.markdown(f"**{len(problems)} problems** available | **{len(solved_ids)} solved** by you")
        st.divider()
        
        # Filter
        filter_option = st.radio(
            "Filter:",
            ["All", "Unsolved", "Solved"],
            horizontal=True
        )
        
        # Display problems
        for problem in problems:
            is_solved = problem.id in solved_ids
            
            # Apply filter
            if filter_option == "Unsolved" and is_solved:
                continue
            if filter_option == "Solved" and not is_solved:
                continue
            
            with st.container():
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                
                with col1:
                    status_icon = "✅" if is_solved else "⬜"
                    title_text = f"{status_icon} **{problem.title}**"
                    st.markdown(title_text)
                    if problem.problem_url:
                        st.markdown(f"[🔗 Open Problem]({problem.problem_url})")
                
                with col2:
                    st.metric("Points", problem.points)
                
                with col3:
                    if problem.cf_contest_id:
                        st.caption(f"CF: {problem.cf_contest_id}{problem.cf_problem_index}")
                    else:
                        st.caption("Custom")
                
                with col4:
                    if not is_solved:
                        if st.button("Mark Solved", key=f"solve_{problem.id}"):
                            new_session = get_session()
                            try:
                                sub = Submission(
                                    user_id=user_id,
                                    problem_id=problem.id,
                                    solved_at=datetime.utcnow()
                                )
                                new_session.add(sub)
                                new_session.commit()
                                st.rerun()
                            finally:
                                new_session.close()
                    else:
                        st.success("Solved!")
                
                st.divider()
finally:
    session.close()
