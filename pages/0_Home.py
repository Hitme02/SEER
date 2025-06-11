# --- pages/0_Home.py ---

import streamlit as st
from utils.auth import check_session, logout
import pandas as pd
import random
import numpy as np
import tenseal as ts

check_session()
st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")
st.title("🏡 Smart Energy Dashboard")

st.success(f"Welcome {st.session_state.role.capitalize()}: {st.session_state.home_id if st.session_state.role == 'home' else 'admin01'}")

# Admin Metrics Section
if st.session_state.role == "admin":
    st.markdown("""
    <div style='border: 1px solid #444; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;'>
        <h4>📊 Grid Overview</h4>
        <p style='font-size: 0.95rem;'>
            This Smart Energy Analytics dashboard enables real-time monitoring of energy usage across homes,
            detects anomalies using machine learning, and ensures privacy using encrypted and differentially private data.
            Admins can visualize usage trends, analyze encrypted billing, and manage per-home metrics securely.
        </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🏠 Total Homes", 3)
    with col2:
        st.metric("⚡ Total Usage Today", "52.9 kWh")

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("📋 Per-Home Usage Details"):
        dummy_data = {
            "Home ID": [f"home_{i:03d}" for i in range(1, 11)],
            "Usage (kWh)": [round(random.uniform(10, 50), 2) for _ in range(10)]
        }
        df = pd.DataFrame(dummy_data)
        st.dataframe(df, use_container_width=True)

st.divider()

# --- Slab Billing + CKKS Encryption + Differential Privacy Demo ---

st.header("🔐 Slab Billing with CKKS & Differential Privacy")

st.markdown("""
Secure billing using encrypted energy data and privacy-preserving techniques like Differential Privacy.
""")

# BBMP tiered billing function
def compute_bbmp_bill(units):
    total = 0
    if units <= 50:
        total += units * 4.15
    elif units <= 100:
        total += 50 * 4.15 + (units - 50) * 5.60
    elif units <= 200:
        total += 50 * 4.15 + 50 * 5.60 + (units - 100) * 7.15
    else:
        total += 50 * 4.15 + 50 * 5.60 + 100 * 7.15 + (units - 200) * 8.20
    return total

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 0

if st.sidebar.button("🔁 Reset Simulation"):
    st.session_state.step = 0

energy = st.sidebar.slider("Energy Usage (kWh)", 50.0, 500.0, 120.0, step=1.0)

# Noise selection buttons
st.markdown("#### 🔧 Choose Privacy Noise Level:")
noise_col1, noise_col2, noise_col3 = st.columns(3)
if "noise_level" not in st.session_state:
    st.session_state.noise_level = "Medium"

if noise_col1.button("Low"):
    st.session_state.noise_level = "Low"
if noise_col2.button("Medium"):
    st.session_state.noise_level = "Medium"
if noise_col3.button("High"):
    st.session_state.noise_level = "High"

st.info(f"Current Noise Level: `{st.session_state.noise_level}`")

# CKKS context setup
context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=8192, coeff_mod_bit_sizes=[60, 40, 40, 60])
context.generate_galois_keys()
context.global_scale = 2 ** 40

# Step-by-step simulation
if st.session_state.step >= 0:
    st.progress(1, text="Step 1: Energy Input")
    st.metric("⚙️ Input Usage", f"{energy} kWh")

if st.session_state.step >= 1:
    bill_amount = compute_bbmp_bill(energy)
    st.progress(2, text="Step 2: Bill Computation")
    st.metric("💸 Raw Bill", f"₹{bill_amount:.2f}")

if st.session_state.step >= 2:
    encoded = ts.ckks_vector(context, [bill_amount])
    st.progress(3, text="Step 3: Bill Encrypted with CKKS")
    st.code(f"ts.ckks_vector(context, [{bill_amount}])")

if st.session_state.step >= 3:
    decrypted = encoded.decrypt()[0]
    st.progress(4, text="Step 4: Decryption Complete")
    st.metric("🔓 Decrypted Bill", f"₹{decrypted:.2f}")

if st.session_state.step >= 4:
    noise_map = {"Low": 1.0, "Medium": 3.0, "High": 6.0}
    noise_scale = noise_map[st.session_state.noise_level]
    dp_noise = np.random.laplace(loc=0.0, scale=noise_scale)
    noisy_bill = decrypted + dp_noise
    st.progress(5, text="Step 5: Differential Privacy Applied")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("📉 Noise Added", f"₹{dp_noise:.2f}")
    with col2:
        st.metric("🔐 Final Privatized Bill", f"₹{noisy_bill:.2f}")

    st.bar_chart({"Original": [decrypted], "Noisy": [noisy_bill]})

# Step advance button
if st.session_state.step < 5:
    if st.button("➡️ Next Step"):
        st.session_state.step += 1
