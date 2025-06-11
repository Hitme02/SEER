import streamlit as st
from login import login_page

def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.home_id = None

    if not st.session_state.authenticated:
        login_page()
    else:
        st.switch_page("pages/0_Home.py")

if __name__ == "__main__":
    main()
