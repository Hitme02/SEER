import streamlit as st
from utils.auth import check_session, logout
import pandas as pd
import plotly.graph_objects as go

check_session()
st.set_page_config(page_title="Anomaly Detection", layout="wide")
st.title("🚨 Anomaly Detection Dashboard")
st.sidebar.button("🚪 Logout", on_click=logout)

def load_anomaly_data():
    df = pd.read_csv("decrypted/anomaly_results.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["is_anomaly_ml"] = df["is_anomaly_ml"].astype(bool)
    df["home_id"] = df["home_id"].astype(str)
    return df

df = load_anomaly_data()

if st.session_state.role == "home":
    home_id = st.session_state.home_id
    st.subheader(f"Anomaly View for: {home_id}")
    filtered = df[df["home_id"] == home_id]
else:
    st.subheader("Admin View: All Homes")
    home_filter = st.selectbox("Select Home", ["All"] + sorted(df["home_id"].unique()))
    filtered = df if home_filter == "All" else df[df["home_id"] == home_filter]

filtered = filtered.dropna(subset=["timestamp", "energy_kwh", "is_anomaly_ml"])

if not filtered.empty:
    fig = go.Figure()

    # Plot actual energy
    fig.add_trace(go.Scatter(
        x=filtered["timestamp"],
        y=filtered["energy_kwh"],
        mode='lines+markers',
        name='Actual Energy (kWh)',
        line=dict(color='blue')
    ))

    # Highlight anomalies with red markers
    anomalies = filtered[filtered["is_anomaly_ml"]]
    fig.add_trace(go.Scatter(
        x=anomalies["timestamp"],
        y=anomalies["energy_kwh"],
        mode='markers',
        name='ML Anomalies',
        marker=dict(color='red', size=10, symbol='x')
    ))

    fig.update_layout(
        title="Energy Usage: Actual vs ML Anomaly Overlay",
        xaxis_title="Time",
        yaxis_title="Energy (kWh)",
        legend=dict(x=1, y=1),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available to plot.")

with st.expander("📋 View Anomalous Events Only"):
    st.dataframe(filtered[filtered["is_anomaly_ml"]], use_container_width=True)
