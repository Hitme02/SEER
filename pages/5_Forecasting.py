import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

from backend.main_module import (
    load_and_preprocess, create_lstm_sequences, load_lstm_model,
    get_ckks_context, run_encrypted_inference, evaluate_predictions
)

st.set_page_config(page_title="📈 Forecasting Module", layout="wide")
st.title("🔮 Forecasting with CKKS Encrypted LSTM")

# Load everything
model_path = "models/nig.h5"
data_path = "data/household_power_consumption.txt"

with st.spinner("Loading model and preparing data..."):
    data_scaled, scaler = load_and_preprocess(data_path)
    X, y = create_lstm_sequences(data_scaled)
    model = load_lstm_model(model_path)
    context = get_ckks_context()

# Only forecast future (test) portion
train_size = min(4000, int(len(X) * 0.8))
X_test, y_test = X[train_size:], y[train_size:]

# User input
max_samples = min(2000, len(X_test))
num_samples = st.slider("🔢 How many future points to simulate?", 10, max_samples, 100)

if st.button("▶️ Run Forecast"):
    actuals, preds = [], []
    placeholder_chart = st.empty()
    progress = st.progress(0)

    for i in range(num_samples):
        actual, pred = run_encrypted_inference(
            model, X_test[i:i+1], y_test[i:i+1], scaler, context, max_samples=1
        )
        actuals.append(actual[0])
        preds.append(pred[0])

        fig, ax = plt.subplots()
        ax.plot(actuals, label="Actual", color="green")
        ax.plot(preds, label="Predicted", color="blue")
        ax.set_title("Live Forecasting (CKKS Encrypted)")
        ax.set_xlabel("Sample Index")
        ax.set_ylabel("Power (kWh)")
        ax.grid(True)
        ax.legend()
        placeholder_chart.pyplot(fig)
        progress.progress((i + 1) / num_samples)

    st.success("✅ Forecasting completed.")
    metrics = evaluate_predictions(np.array(actuals), np.array(preds))
    st.subheader("📊 Evaluation Metrics")
    st.write(f"MAE: `{metrics['MAE']:.4f}` kWh")
    st.write(f"RMSE: `{metrics['RMSE']:.4f}` kWh")
    st.write(f"R² Score: `{metrics['R2']:.4f}`")
