import streamlit as st
import time

# Simulated user database
USER_DB = {
    "user01": {"password": "home123", "role": "home", "home_id": "home_001"},
    "user02": {"password": "home456", "role": "home", "home_id": "home_002"},
    "admin01": {"password": "admin123", "role": "admin", "home_id": None}
}

def login_page():
    st.title("🔒 Smart Energy Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = USER_DB.get(username)
        if user and user["password"] == password:
            st.session_state.authenticated = True
            st.session_state.role = user["role"]
            st.session_state.home_id = user["home_id"]
            st.session_state.username = username
            st.session_state.login_time = time.time()
            st.success(f"✅ Logged in as {username} ({user['role']})")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")
