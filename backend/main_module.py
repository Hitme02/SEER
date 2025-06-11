# Paste the modular code from STEP 1 here
# --- Imports ---
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tensorflow.keras.models import load_model
import tenseal as ts
import matplotlib.pyplot as plt

from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import MeanSquaredError as MSE

# --- 1. Load and preprocess data ---
def load_and_preprocess(filepath="household_power_consumption.txt"):
    df = pd.read_csv(filepath, sep=";", na_values="?", low_memory=False)
    df['Datetime'] = pd.to_datetime(df['Date'] + " " + df['Time'], format="%d/%m/%Y %H:%M:%S")
    df.set_index("Datetime", inplace=True)
    df.drop(['Date', 'Time'], axis=1, inplace=True)
    df = df.astype(float).interpolate()
    data = df['Global_active_power'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)
    return data_scaled, scaler

# --- 2. Create sequences for LSTM ---
def create_lstm_sequences(data, window_size=5):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size])
    return np.array(X), np.array(y)

# --- 3. Load trained LSTM model ---
from tensorflow.keras.models import load_model

def load_lstm_model(model_path="nig.h5"):
    try:
        # Load and compile in one step — safer if model was saved with compile=True
        model = load_model(model_path)
    except Exception as e:
        print("🔁 Trying manual compile...")
        model = load_model(model_path, compile=False)
        from tensorflow.keras.losses import MeanSquaredError
        model.compile(optimizer='adam', loss=MeanSquaredError())
    return model


# --- 4. Set up CKKS context ---
def get_ckks_context():
    context = ts.context(
        ts.SCHEME_TYPE.CKKS,
        poly_modulus_degree=8192,
        coeff_mod_bit_sizes=[60, 40, 40, 60]
    )
    context.global_scale = 2 ** 40
    context.generate_galois_keys()
    return context

# --- 5. Encrypted inference simulation ---
def run_encrypted_inference(model, X_test, y_test, scaler, context, max_samples=100):
    preds, actuals = [], []
    for i in range(min(len(X_test), max_samples)):
        sample = X_test[i].flatten()
        enc_sample = ts.ckks_vector(context, sample)
        dec_sample = np.array(enc_sample.decrypt()).reshape((5, 1))
        pred_scaled = model.predict(dec_sample[np.newaxis, :, :])[0][0]
        pred = scaler.inverse_transform([[pred_scaled]])[0][0]
        actual = scaler.inverse_transform(y_test[i].reshape(1, -1))[0][0]
        preds.append(pred)
        actuals.append(actual)
    return actuals, preds

# --- 6. Evaluate metrics ---
def evaluate_predictions(actuals, preds):
    mae = mean_absolute_error(actuals, preds)
    rmse = np.sqrt(mean_squared_error(actuals, preds))
    r2 = r2_score(actuals, preds)
    return {"MAE": mae, "RMSE": rmse, "R2": r2}

# --- 7. Plot results ---
def plot_predictions(actuals, preds):
    plt.figure(figsize=(10,6))
    plt.plot(actuals, label='Actual')
    plt.plot(preds, label='Predicted')
    plt.title('Actual vs Predicted Global Active Power (Encrypted Inference)')
    plt.xlabel('Sample Index')
    plt.ylabel('Global Active Power (kWh)')
    plt.legend()
    plt.grid(True)
    plt.show()
