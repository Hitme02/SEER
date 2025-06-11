import streamlit as st
import pandas as pd
import plotly.express as px
from backend.storage_optimizer import optimize_battery_operation

st.set_page_config(page_title="🔋 Energy Storage Optimizer", layout="wide")
st.title("🔋 Smart Battery Optimization")

# Load dataset
try:
    df = pd.read_csv("decrypted/decrypted_usage.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["energy_kwh"] = df["energy_kwh"].astype(float)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# Sidebar configuration
st.sidebar.header("⚙️ Optimization Settings")
battery_capacity = st.sidebar.slider("Battery Capacity (kWh)", 5, 20, 10)
charge_rate = st.sidebar.slider("Charge Rate (kWh)", 1, 5, 2)
discharge_rate = st.sidebar.slider("Discharge Rate (kWh)", 1, 5, 2)
price_per_kwh = st.sidebar.slider("Price per kWh (₹)", 4.0, 10.0, 6.0)

optimized = optimize_battery_operation(
    df,
    capacity_kwh=battery_capacity,
    charge_rate=charge_rate,
    discharge_rate=discharge_rate,
    price_per_kwh=price_per_kwh
)

# Show chart
st.subheader("📈 Energy + Solar + Battery Simulation")
fig = px.line(
    optimized,
    x="timestamp",
    y=["energy_kwh", "solar_kwh", "soc_kwh"],
    labels={"value": "kWh", "timestamp": "Time"},
    title="Energy Usage vs Solar vs Battery SOC"
)
st.plotly_chart(fig, use_container_width=True)

# Show actions
st.subheader("⚡ Battery Actions Log")
st.dataframe(optimized[["timestamp", "action", "soc_kwh", "savings_rs"]].tail(30))

total_savings = optimized["savings_rs"].sum()
st.success(f"✅ Estimated Total Savings: ₹{total_savings:.2f}")
