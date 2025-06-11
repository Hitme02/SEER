import pandas as pd

def load_decrypted_usage(path="decrypted/decrypted_usage.csv"):
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df[["timestamp", "home_id", "energy_kwh"]]
