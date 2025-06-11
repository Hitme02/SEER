import streamlit as st
import pandas as pd
import plotly.express as px
from backend.auth import check_session, logout
from backend.data_handler import load_decrypted_usage
from backend.privacy import add_laplace_noise
import time

check_session()
st.set_page_config(page_title="Real-Time Usage (Private)", layout="wide")
st.title("📊 Real-Time Usage with Differential Privacy")

st.sidebar.button("🚪 Logout", on_click=logout)

# 🔐 Slider for epsilon
epsilon = st.slider("Privacy Level (ε):", min_value=0.1, max_value=5.0, step=0.1, value=1.0)
privacy_level = (
    "🔴 High Privacy" if epsilon < 0.5 else
    "🟡 Medium Privacy" if epsilon < 2.0 else
    "🟢 Low Privacy"
)
st.caption(f"Selected ε = {epsilon:.1f} ({privacy_level})")

# Load data
df = load_decrypted_usage()

# Add Laplace noise live
df["noisy_kwh"] = df["energy_kwh"].apply(lambda x: add_laplace_noise(x, epsilon))

# Filter
if st.session_state.role == "home":
    home_id = st.session_state.home_id
    filtered = df[df["home_id"] == home_id]
else:
    home_filter = st.selectbox("Select Home", ["All"] + sorted(df["home_id"].unique()))
    filtered = df if home_filter == "All" else df[df["home_id"] == home_filter]

# Plot
fig = px.line(
    filtered.tail(100),
    x="timestamp",
    y="noisy_kwh",
    color="home_id" if st.session_state.role == "admin" and home_filter == "All" else None,
    title="Energy Usage with Differential Privacy",
    labels={"noisy_kwh": "Noisy Energy (kWh)", "timestamp": "Time"},
    markers=True
)
st.plotly_chart(fig, use_container_width=True)

# Raw Table
with st.expander("📄 View Raw Data with Noise"):
    st.dataframe(filtered.tail(20)[["timestamp", "home_id", "energy_kwh", "noisy_kwh"]])
