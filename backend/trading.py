# --- backend/trading.py ---

import random
import networkx as nx
import json

class SmartGridGraph:
    def __init__(self, num_nodes, connection_density=0.5):
        self.num_nodes = num_nodes
        self.edges = {i: [] for i in range(num_nodes)}
        self.graph = nx.Graph()
        self.edge_list = []
        self._generate_random_edges(connection_density)

    def _generate_random_edges(self, density):
        self.graph.add_nodes_from(range(self.num_nodes))
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                if random.random() < density:
                    weight = random.randint(1, 20)
                    self.edges[i].append((j, weight))
                    self.edges[j].append((i, weight))
                    self.graph.add_edge(i, j, weight=weight)
                    self.edge_list.append((i, j, weight))

    def get_edge_list(self):
        return self.edge_list

    def get_num_nodes(self):
        return self.num_nodes

class PowerAwareGraph:
    def __init__(self, num_nodes, edge_list, powers=None):
        self.num_nodes = num_nodes
        self.graph = nx.Graph()
        self.powers = powers or {i: round(random.uniform(0.5, 2.0), 2) for i in range(num_nodes)}
        self._use_edge_list(edge_list)

    def _use_edge_list(self, edge_list):
        self.graph.add_nodes_from(range(self.num_nodes))
        for u, v, base_cost in edge_list:
            power_weighted_cost = round(base_cost / (self.powers[u] * self.powers[v]), 2)
            self.graph.add_edge(u, v, weight=power_weighted_cost)

    def dijkstra(self, source):
        dist = {node: float('inf') for node in self.graph.nodes}
        dist[source] = 0
        prev = {node: None for node in self.graph.nodes}
        visited = set()
        steps = []

        while len(visited) < len(self.graph.nodes):
            u = min((node for node in self.graph.nodes if node not in visited), key=lambda x: dist[x], default=None)
            if u is None:
                break
            visited.add(u)
            steps.append((u, dict(dist)))
            for v in self.graph.neighbors(u):
                weight = self.graph[u][v]['weight']
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    prev[v] = u

        paths = {node: self._reconstruct_path(prev, source, node) for node in self.graph.nodes}
        return dist, paths, steps

    def _reconstruct_path(self, prev, src, tgt):
        path = []
        while tgt is not None:
            path.insert(0, tgt)
            tgt = prev[tgt]
        return path if path and path[0] == src else []

    def get_graph(self):
        return self.graph

    def get_powers(self):
        return self.powers

def simulate_token_trading(power_graph, net_energy):
    wallet = {}
    trades_log = []

    for home, balance in net_energy.items():
        wallet[home] = {"tokens": max(0, int(balance))}

    surplus_nodes = [h for h in net_energy if net_energy[h] > 0]
    deficit_nodes = [h for h in net_energy if net_energy[h] < 0]

    for surplus_home in surplus_nodes:
        tokens_available = wallet[surplus_home]["tokens"]
        path_costs, path_routes, _ = power_graph.dijkstra(surplus_home)

        sorted_deficits = sorted(deficit_nodes, key=lambda h: path_costs.get(h, float('inf')))

        for deficit_home in sorted_deficits:
            if tokens_available <= 0:
                break
            if deficit_home not in path_costs or path_costs[deficit_home] == float('inf'):
                continue

            need = abs(net_energy[deficit_home])
            transfer = min(tokens_available, int(need))

            if transfer <= 0:
                continue

            wallet[surplus_home]["tokens"] -= transfer
            wallet[deficit_home] = wallet.get(deficit_home, {"tokens": 0})
            wallet[deficit_home]["tokens"] += transfer

            net_energy[surplus_home] -= transfer
            net_energy[deficit_home] += transfer
            tokens_available -= transfer

            trades_log.append({
                "from": surplus_home,
                "to": deficit_home,
                "tokens": transfer,
                "path_cost": path_costs[deficit_home],
                "path_route": path_routes[deficit_home]
            })

    return wallet, trades_log
