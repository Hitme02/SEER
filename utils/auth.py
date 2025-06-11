import streamlit as st
import time

SESSION_TIMEOUT = 30 * 60  # 30 minutes

def check_session():
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.error("Please log in first.")
        st.stop()

    if time.time() - st.session_state.get("login_time", 0) > SESSION_TIMEOUT:
        st.warning("⏱️ Session timed out. Please log in again.")
        logout()
        st.stop()

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()
