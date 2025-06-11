# 🔍 SEER – Smart Energy Encryption & Reporting

**SEER** is a comprehensive Smart Grid analytics and visualization dashboard designed for privacy-preserving energy management. It integrates real-time usage monitoring, anomaly detection, encrypted forecasting, billing, and reporting modules—all built with a secure, scalable, and visually rich Streamlit interface.

---

## 📁 Project Structure

```
SEER/
│
├── backend/                  # Reusable logic (models, encryption, utilities)
│   ├── anomaly_model.py
│   ├── main_module.py        # LSTM + CKKS code
│   └── data_handler.py
│
├── data/                     # Input raw datasets (excluded from GitHub)
│
├── decrypted/                # Output for decrypted + noisy usage
│   ├── decrypted_usage.csv
│   └── anomaly_results.csv
│
├── pages/                    # Multi-page Streamlit app
│   ├── 0_Home.py
│   ├── 1_Real_Time_Usage.py
│   ├── 2_Anomaly_Detection.py
│   ├── 3_Billing.py
│   └── 5_Forecasting.py
│
├── utils/                    # Auth & helpers
│   └── auth.py
│
├── requirements.txt
└── README.md                 # You're here
```

---

## ⚙️ Features Overview

### ✅ 1. Real-Time Usage Monitoring
- Streams live power data from dataset.
- Adds differential privacy using Laplace noise.
- Automatically updates dashboards.

### ✅ 2. Anomaly Detection
- Uses Isolation Forest to detect anomalies.
- Visualizes energy outliers per home.
- Explains anomalous patterns.

### ✅ 3. Forecasting (LSTM + CKKS)
- LSTM model trained on global power data.
- Forecasting via CKKS homomorphic encryption.
- Graphs actual vs predicted values in real time.

### ✅ 4. Billing (Encrypted)
- Tiered BBMP/BESCOM-style billing slabs.
- CKKS encrypts bills, applies noise, decrypts final.
- Visual simulation of privacy-aware billing.

### ✅ 5. Reporting & Admin Control
- View per-home usage table.
- Slab-based billing comparisons.
- Data visualization & metrics for each home.

---

## 🔒 Security & Privacy

- **Differential Privacy**: Adds tunable Laplace noise to obfuscate exact readings.
- **CKKS Encryption**: Homomorphic encryption allows secure inference without decrypting data.
- **Session-Based Auth**: Ensures role-based access to dashboards.

---

## 🚀 How to Run

1. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Ensure CKKS (TenSEAL) and TensorFlow installed**
   - Use Python 3.10+
   - Avoid pushing `venv/` to GitHub due to size.

3. **Launch Streamlit app:**
   ```
   streamlit run pages/0_Home.py
   ```

---

## 📈 Screenshots

| Feature | Snapshot |
|--------|----------|
| Home Dashboard | ✅ Metrics + Per-Home Usage |
| CKKS Billing | ✅ Encrypted bill vector, step-by-step |
| Anomaly Detection | ✅ Shows noisy data and flags |
| Forecasting | ✅ Real-time simulation with CKKS inference |

---

## 🧠 Future Enhancements
- MQTT support for IoT device integration
- Battery storage simulation
- PDF report export
- Grid health monitoring
- AI Chatbot For interfacing

---

## 📜 Credits
- Powered by Streamlit, TensorFlow, scikit-learn, TenSEAL
- Developed by [@Hitme02](https://github.com/Hitme02), [@chhavipareek](https://github.com/chhavi-pareek) and [@advyy100i](https://github.com/advyy100i)

