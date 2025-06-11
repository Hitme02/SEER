import pandas as pd

rolling_stats = {}

def is_anomaly(home_id, value, window=50, threshold=2.5):
    if home_id not in rolling_stats:
        rolling_stats[home_id] = []

    values = rolling_stats[home_id]
    values.append(value)

    if len(values) > window:
        values.pop(0)

    mean = sum(values) / len(values)
    std = (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5
    lower, upper = mean - threshold * std, mean + threshold * std

    return value < lower or value > upper

def load_anomaly_results(path="decrypted/anomaly_results.csv"):
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df[["timestamp", "home_id", "energy_kwh", "is_anomaly"]]
