import pandas as pd
from sklearn.ensemble import IsolationForest

def train_model(df: pd.DataFrame):
    """
    Trains IsolationForest on energy_kwh.
    """
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(df[["energy_kwh"]])
    return model

def detect_anomalies(model, df: pd.DataFrame):
    """
    Adds 'is_anomaly_ml' column to the dataframe.
    """
    df["is_anomaly_ml"] = model.predict(df[["energy_kwh"]]) == -1
    return df
