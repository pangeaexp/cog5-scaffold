import random
import math
from typing import Dict, Any, List
import networkx as nx

class Node:
    def __init__(self, nid: int):
        self.id = nid
        # intrinsic properties
        self.activation = random.random()
        self.bias = random.uniform(-1, 1)
        self.connections: Dict[int, float] = {}

    def to_dict(self):
        return {"id": self.id, "activation": self.activation, "bias": self.bias, "connections": self.connections}

class NodeNetwork:
    def __init__(self, n_nodes: int = 36):
        self.n_nodes = n_nodes
        self.nodes: Dict[int, Node] = {i: Node(i) for i in range(n_nodes)}
        self.graph = nx.DiGraph()

    def initialize_random(self, connectivity: float = 0.15):
        self.graph.clear()
        for i in range(self.n_nodes):
            self.graph.add_node(i)
        for i in range(self.n_nodes):
            for j in range(self.n_nodes):
                if i == j:
                    continue
                if random.random() < connectivity:
                    weight = random.uniform(-1, 1)
                    self.graph.add_edge(i, j, weight=weight)
                    self.nodes[i].connections[j] = weight

    def to_dict(self):
        edges = [{"u": u, "v": v, "weight": d.get("weight", 0)} for u, v, d in self.graph.edges(data=True)]
        return {"n_nodes": self.n_nodes, "nodes": {i: self.nodes[i].to_dict() for i in self.nodes}, "edges": edges}

    def from_dict(self, payload: Dict[str, Any]):
        self.n_nodes = payload.get("n_nodes", self.n_nodes)
        nodes = payload.get("nodes", {})
        self.nodes = {int(k): Node(int(k)) for k in nodes.keys()}
        for k, v in nodes.items():
            n = self.nodes[int(k)]
            n.activation = v.get("activation", n.activation)
            n.bias = v.get("bias", n.bias)
            n.connections = v.get("connections", {})
        self.graph = nx.DiGraph()
        for e in payload.get("edges", []):
            self.graph.add_edge(e["u"], e["v"], weight=e.get("weight", 0))

    def mean_abs_weight(self):
        ws = [abs(d.get("weight", 0)) for _, _, d in self.graph.edges(data=True)]
        return sum(ws) / (len(ws) or 1)

    def density(self):
        possible = self.n_nodes * (self.n_nodes - 1)
        return self.graph.number_of_edges() / possible if possible > 0 else 0.0
