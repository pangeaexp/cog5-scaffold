import random
from typing import Any

class GeneticEngine:
    def __init__(self, network, metrics, mutation_rate: float = 0.05, crossover_rate: float = 0.5):
        self.network = network
        self.metrics = metrics
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        # internal generation counter
        self.generation = 0

    def _mutate(self):
        # mutate some edges' weights
        for u, v, d in list(self.network.graph.edges(data=True)):
            if random.random() < self.mutation_rate:
                old = d.get("weight", 0)
                delta = random.uniform(-0.5, 0.5)
                new = max(-1.0, min(1.0, old + delta))
                self.network.graph[u][v]["weight"] = new
                self.network.nodes[u].connections[v] = new

    def _crossover(self):
        # simple crossover: randomly rewire a small subset of edges
        if random.random() > self.crossover_rate:
            return
        nodes = list(self.network.graph.nodes)
        a = random.choice(nodes)
        b = random.choice(nodes)
        # swap outgoing neighbors sets partially
        outs_a = list(self.network.graph.successors(a))
        outs_b = list(self.network.graph.successors(b))
        for i in range(min(len(outs_a), len(outs_b))):
            if random.random() < 0.5:
                wa = self.network.graph[a][outs_a[i]]["weight"]
                wb = self.network.graph[b][outs_b[i]]["weight"]
                self.network.graph[a][outs_a[i]]["weight"] = wb
                self.network.graph[b][outs_b[i]]["weight"] = wa
                self.network.nodes[a].connections[outs_a[i]] = wb
                self.network.nodes[b].connections[outs_b[i]] = wa

    def evaluate_fitness(self):
        # Placeholder fitness combining density and mean abs weight (more connectivity  moderate weights)
        density = self.network.density()
        mean_w = self.network.mean_abs_weight()
        fitness = (1.0 - abs(0.5 - mean_w)) * density
        # track in metrics
        self.metrics.data.setdefault("fitness_history", []).append(fitness)
        return fitness

    def evolve_one_generation(self):
        self._mutate()
        self._crossover()
        fitness = self.evaluate_fitness()
        self.generation += 1
        return {"generation": self.generation, "fitness": fitness}
