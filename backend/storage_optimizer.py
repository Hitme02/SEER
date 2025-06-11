import pandas as pd
import numpy as np
from datetime import datetime

def simulate_solar_generation(timestamps):
    """Simulate solar generation curve with higher generation in daytime."""
    return [
        max(0, 2 * np.sin((ts.hour - 6) * np.pi / 12))  # Peak around noon
        for ts in timestamps
    ]

def optimize_battery_operation(data, capacity_kwh=10, charge_rate=2, discharge_rate=2, initial_soc=0, price_per_kwh=6.0):
    data = data.copy()
    data["solar_kwh"] = simulate_solar_generation(data["timestamp"])
    data["net_usage_kwh"] = data["energy_kwh"] - data["solar_kwh"]

    soc = initial_soc
    actions = []

    for _, row in data.iterrows():
        net = row["net_usage_kwh"]
        if net > 0:  # Consumption exceeds solar
            discharge = min(discharge_rate, soc, net)
            soc -= discharge
            action = f"Discharge {discharge:.2f} kWh"
        else:  # Excess solar, try to store
            charge = min(charge_rate, capacity_kwh - soc, -net)
            soc += charge
            action = f"Charge {charge:.2f} kWh"
        actions.append((soc, action))

    data["soc_kwh"] = [a[0] for a in actions]
    data["action"] = [a[1] for a in actions]
    data["savings_rs"] = data["soc_kwh"].diff().fillna(0) * price_per_kwh

    return data[["timestamp", "energy_kwh", "solar_kwh", "net_usage_kwh", "soc_kwh", "action", "savings_rs"]]
