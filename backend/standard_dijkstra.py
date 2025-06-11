import random
import networkx as nx

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
            for j in range(i+1, self.num_nodes):
                if random.random() < density:
                    weight = random.randint(1, 20)
                    self.edges[i].append((j, weight))
                    self.edges[j].append((i, weight))
                    self.graph.add_edge(i, j, weight=weight)
                    self.edge_list.append((i, j, weight))

    def dijkstra(self, source):
        dist = {node: float('inf') for node in range(self.num_nodes)}
        dist[source] = 0
        prev = {node: None for node in range(self.num_nodes)}
        visited = set()
        steps = []

        while len(visited) < self.num_nodes:
            u = min((node for node in range(self.num_nodes) if node not in visited), key=lambda x: dist[x], default=None)
            if u is None: break
            visited.add(u)
            steps.append((u, dict(dist)))
            for v, weight in self.edges[u]:
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    prev[v] = u

        paths = {node: self._reconstruct_path(prev, source, node) for node in range(self.num_nodes)}
        return dist, paths, steps

    def _reconstruct_path(self, prev, src, tgt):
        path = []
        while tgt is not None:
            path.insert(0, tgt)
            tgt = prev[tgt]
        return path if path[0] == src else []

    def get_graph(self):
        return self.graph

    def get_edge_list(self):
        return self.edge_list

    def random_source(self):
        return random.randint(0, self.num_nodes - 1)
