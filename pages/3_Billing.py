
# --- pages/3_Billing.py ---
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import numpy as np
import tenseal as ts
from backend.main_module import load_lstm_model, get_ckks_context, run_encrypted_inference, load_and_preprocess, create_lstm_sequences

st.set_page_config(page_title="Encrypted Billing", layout="wide")
st.title("💰 Smart Billing Module (CKKS + Forecasting)")

# Load trained LSTM model and scaler
model = load_lstm_model("models/nig.h5")
data_scaled, scaler = load_and_preprocess("data/household_power_consumption.txt")
X, y = create_lstm_sequences(data_scaled)
context = get_ckks_context()

# Get the most recent prediction from forecasting module
X_input = X[-1:]
y_input = y[-1:]
_, forecasted_vals = run_encrypted_inference(model, X_input, y_input, scaler, context, max_samples=1)
predicted_kwh = forecasted_vals[0]

st.metric("🔮 Forecasted Usage (kWh)", f"{predicted_kwh:.2f}")

# BBMP/BESCOM tiered billing function
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

# Step 1: Compute raw bill
bill_amount = compute_bbmp_bill(predicted_kwh)
st.subheader("🧮 Step 1: Compute Bill")
st.metric("💵 Raw Bill (Unencrypted)", f"₹{bill_amount:.2f}")

# Step 2: Encrypt bill using CKKS
st.subheader("🔐 Step 2: Encrypt Bill")
enc_vector = ts.ckks_vector(context, [bill_amount])
decrypted_vec = enc_vector.decrypt()

with st.expander("🔍 View CKKS Encrypted Vector"):
    st.code(decrypted_vec, language="python")

# Step 3: Apply Differential Privacy (DP)
st.subheader("🛡️ Step 3: Apply Differential Privacy")
privacy_level = st.radio("Select Privacy Level", ["Low", "Medium", "High"], horizontal=True)
dp_noise = {"Low": np.random.laplace(0, 1), "Medium": np.random.laplace(0, 3), "High": np.random.laplace(0, 6)}[privacy_level]
noisy_bill = bill_amount + dp_noise
st.metric("🔐 Final Noisy Bill", f"₹{noisy_bill:.2f}")
st.caption(f"Added Laplace noise: ₹{dp_noise:.2f}")
