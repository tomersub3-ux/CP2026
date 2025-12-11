"""
Authentication module for Competitive Programming Platform.
Handles login, registration, password change, and session management.
"""
import streamlit as st
from models import User, get_session, init_db


def ensure_db_initialized():
    """Ensure database is initialized."""
    init_db()


def login(username: str, password: str) -> bool:
    """
    Attempt to log in a user.
    Returns True if successful, False otherwise.
    """
    session = get_session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if user and user.check_password(password):
            st.session_state["user_id"] = user.id
            st.session_state["username"] = user.username
            st.session_state["is_admin"] = user.is_admin
            st.session_state["logged_in"] = True
            return True
        return False
    finally:
        session.close()


def register(username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success, message).
    """
    if len(username) < 3:
        return False, "Username must be at least 3 characters."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    
    session = get_session()
    try:
        # Check if username exists
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            return False, "Username already taken."
        
        # Create new user
        user = User(username=username, is_admin=False)
        user.set_password(password)
        session.add(user)
        session.commit()
        return True, "Registration successful! Please log in."
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


def change_password(user_id: int, current_password: str, new_password: str) -> tuple[bool, str]:
    """
    Change user password.
    Returns (success, message).
    """
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters."
    
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found."
        
        if not user.check_password(current_password):
            return False, "Current password is incorrect."
        
        user.set_password(new_password)
        session.commit()
        return True, "Password changed successfully!"
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


def logout():
    """Log out current user."""
    for key in ["user_id", "username", "is_admin", "logged_in"]:
        if key in st.session_state:
            del st.session_state[key]


def is_logged_in() -> bool:
    """Check if user is logged in."""
    return st.session_state.get("logged_in", False)


def is_admin() -> bool:
    """Check if current user is admin."""
    return st.session_state.get("is_admin", False)


def get_current_user_id() -> int | None:
    """Get current user ID."""
    return st.session_state.get("user_id")


def get_current_username() -> str | None:
    """Get current username."""
    return st.session_state.get("username")


def update_cf_handle(user_id: int, cf_handle: str) -> tuple[bool, str]:
    """Update user's Codeforces handle."""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "User not found."
        
        user.cf_handle = cf_handle.strip() if cf_handle else None
        session.commit()
        return True, "Codeforces handle updated!"
    except Exception as e:
        session.rollback()
        return False, f"Error: {str(e)}"
    finally:
        session.close()


def get_user_cf_handle(user_id: int) -> str | None:
    """Get user's Codeforces handle."""
    session = get_session()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        return user.cf_handle if user else None
    finally:
        session.close()
