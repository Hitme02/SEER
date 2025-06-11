# --- pages/4_Token_Trading.py ---

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import cm
import random
import pandas as pd
import json

from backend.trading import simulate_token_trading, PowerAwareGraph, SmartGridGraph

def plot_graph(graph, net_energy, powers, highlight_path=None):
    pos = nx.spring_layout(graph, seed=42)
    values = list(net_energy.values())
    max_abs_val = max(abs(v) for v in values) if values else 1
    norm = mcolors.Normalize(vmin=-max_abs_val, vmax=max_abs_val)
    cmap = cm.RdYlGn
    node_colors = [cmap(norm(net_energy.get(node, 0))) for node in graph.nodes]

    fig, ax = plt.subplots(figsize=(8, 6))
    nx.draw_networkx(graph, pos, node_color=node_colors, with_labels=True, node_size=700, ax=ax)

    if highlight_path:
        path_edges = list(zip(highlight_path, highlight_path[1:]))
        nx.draw_networkx_edges(graph, pos, edgelist=path_edges, edge_color='blue', width=3, ax=ax)

    for node, (x, y) in pos.items():
        ax.text(x, y - 0.1, f"P:{powers[node]:.2f}", fontsize=8, ha='center')

    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    fig.colorbar(sm, ax=ax).set_label('Net Energy')
    ax.set_title("🔌 Smart Grid (Color = Net Energy, Label = Power)")
    ax.axis('off')
    st.pyplot(fig)
    plt.clf()

st.set_page_config(page_title="Token Trading", layout="wide")
st.title("⚡ Power-Aware Token Trading Simulator")

st.sidebar.header("📊 Graph Config")
num_nodes = st.sidebar.slider("Nodes", 5, 20, 6)
connection_density = st.sidebar.slider("Density", 0.1, 1.0, 0.5)
seed = st.sidebar.number_input("Random seed", value=42, step=1)
random.seed(seed)

grid = SmartGridGraph(num_nodes=num_nodes, connection_density=connection_density)
edge_list = grid.get_edge_list()
powers = {i: round(random.uniform(0.5, 2.0), 2) for i in range(num_nodes)}
power_graph = PowerAwareGraph(num_nodes, edge_list, powers)
graph = power_graph.get_graph()

default_net = {i: round(random.uniform(-5, 5), 1) for i in range(num_nodes)}
net_energy = {i: st.sidebar.number_input(f"Node {i}", value=default_net[i], step=0.1) for i in range(num_nodes)}

st.markdown("### 🧠 Grid Visualization")
plot_graph(graph, net_energy, powers)

wallet, trades_log = simulate_token_trading(power_graph, net_energy.copy())

st.markdown("### 💸 Final Wallet Balances")
st.table({k: v['tokens'] for k, v in wallet.items()})

# --- Metrics ---
total_tokens = sum(t["tokens"] for t in trades_log)
total_cost = sum(t["tokens"] * t["path_cost"] for t in trades_log)
naive_cost = sum(t["tokens"] * (len(t["path_route"]) - 1) for t in trades_log)
savings = naive_cost - total_cost

st.markdown("### 📈 Power-Aware Trading Insights")
col1, col2, col3 = st.columns(3)
col1.metric("Total Tokens Traded", total_tokens)
col2.metric("Power-Aware Total Cost", f"{total_cost:.2f}")
col3.metric("Estimated Cost Saved", f"{savings:.2f}")

# --- Display Trades ---
toggle_mode = st.radio("Select Trade Display Mode:", ["🔁 Step-by-Step", "📋 Show All At Once"])

if toggle_mode == "📋 Show All At Once":
    if trades_log:
        st.dataframe(pd.DataFrame(trades_log))
    else:
        st.info("⚠️ No trades were executed.")
else:
    st.markdown("### 👣 Step-by-Step Trade Execution")

    if 'trade_index' not in st.session_state:
        st.session_state.trade_index = -1

    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Next"):
            if st.session_state.trade_index < len(trades_log) - 1:
                st.session_state.trade_index += 1
    with col2:
        if st.button("➖ Back"):
            if st.session_state.trade_index > -1:
                st.session_state.trade_index -= 1

    if trades_log and st.session_state.trade_index >= 0:
        partial = trades_log[:st.session_state.trade_index + 1]
        st.dataframe(pd.DataFrame(partial))
        st.markdown("### 🔍 Last Trade Route")
        last = partial[-1]
        plot_graph(graph, net_energy, powers, highlight_path=last["path_route"])
    elif not trades_log:
        st.info("❌ No trades to display.")
    else:
        st.info("Click ➕ to step through the trade log.")

# --- Export ---
st.markdown("### 📄 Export")
col1, col2 = st.columns(2)
with col1:
    if trades_log and st.button("Export Trades as CSV"):
        csv = pd.DataFrame(trades_log).to_csv(index=False)
        st.download_button("Download CSV", csv, "trades.csv", "text/csv")
with col2:
    if st.button("Export Wallets as JSON"):
        st.download_button("Download JSON", json.dumps(wallet, indent=2), "wallets.json", "application/json")
