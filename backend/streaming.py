# --- backend/streaming.py ---

import pandas as pd
import time
from datetime import datetime
import os
from sklearn.ensemble import IsolationForest
from backend.privacy import add_laplace_noise
from backend.encryption import get_ckks_context, encrypt_value, decrypt_value

# ⚙️ Parameters
INPUT_FILE = "data/household_power_consumption.txt"
OUTPUT_FILE = "decrypted/anomaly_results.csv"
DECRYPTED_OUTPUT = "decrypted/decrypted_usage.csv"
EPSILON = 1.5
HOMES = ["home_001", "home_002", "home_003"]

# Load CKKS context
context = get_ckks_context()

# Load and preprocess dataset
df = pd.read_csv(INPUT_FILE, sep=";", low_memory=False)
df = df.replace('?', pd.NA).dropna()
df["timestamp"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%d/%m/%Y %H:%M:%S")
df["Global_active_power"] = df["Global_active_power"].astype(float)
df["energy_kwh"] = df["Global_active_power"] / 60.0
df["home_id"] = [HOMES[i % len(HOMES)] for i in range(len(df))]
df = df[["timestamp", "home_id", "energy_kwh"]]

# Add Laplace noise and train on noisy data
df["noisy_kwh"] = df["energy_kwh"].apply(lambda x: max(0, add_laplace_noise(x, epsilon=EPSILON)))
model = IsolationForest(contamination=0.1, random_state=42)
model.fit(df[["noisy_kwh"]])
print("✅ Anomaly model trained on noisy data.")

# Clear old output
for path in [OUTPUT_FILE, DECRYPTED_OUTPUT]:
    if os.path.exists(path):
        os.remove(path)

# Start streaming
print("🚀 Streaming started...")

for _, row in df.iterrows():
    encrypted = encrypt_value(context, row["energy_kwh"])
    decrypted = decrypt_value(context, encrypted)
    noisy = max(0, add_laplace_noise(decrypted, epsilon=EPSILON))
    is_anomaly = model.predict([[noisy]])[0] == -1

    row_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "home_id": row["home_id"],
        "energy_kwh": round(decrypted, 2),
        "noisy_kwh": round(noisy, 2),
        "is_anomaly": False,
        "is_anomaly_ml": is_anomaly
    }

    for path in [OUTPUT_FILE, DECRYPTED_OUTPUT]:
        write_mode = "a" if os.path.exists(path) else "w"
        header = not os.path.exists(path)
        pd.DataFrame([row_data]).to_csv(path, mode=write_mode, header=header, index=False)

    print("📡 Streamed:", row_data)
    time.sleep(2)
