import streamlit as st
import time

# Simulated user database
USER_DB = {
    "user01": {"password": "home123", "role": "home", "home_id": "home_001"},
    "user02": {"password": "home456", "role": "home", "home_id": "home_002"},
    "admin01": {"password": "admin123", "role": "admin", "home_id": None}
}

def check_session():
    if not st.session_state.get("authenticated", False):
        st.error("❌ Please log in to continue.")
        st.stop()

    # Session timeout (30 mins)
    if time.time() - st.session_state.get("login_time", 0) > 1800:
        st.warning("⏳ Session timed out. Please log in again.")
        logout()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def validate_user(username, password):
    user = USER_DB.get(username)
    if user and user["password"] == password:
        return user
    return None
