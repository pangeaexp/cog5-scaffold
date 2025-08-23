"""OO Genetic Algorithm with selection strategies, elitism and multi-objective support,
including non-dominated sorting and crowding distance for Pareto ranking.
"""
import random
import time
from typing import List, Callable, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field



@dataclass(eq=False)
class Individual:
    genotype: List[Any]
    phenotype: Optional[Any] = None
    fitness: List[float] = field(default_factory=list)
    id: str = field(default_factory=lambda: f"ind_{int(time.time()*1000)}_{random.randint(0, 10000)}")
    pareto_rank: Optional[int] = None
    crowding_distance: Optional[float] = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Individual) and self.id == other.id

    def evaluate(self, objectives: List[Callable]):
        # phenotype fallback to genotype if not set
        vals = []
        for obj in objectives:
            inp = self.phenotype if self.phenotype is not None else self.genotype
            vals.append(float(obj(inp)))
        self.fitness = vals

def dominates(a: Individual, b: Individual) -> bool:
    """Return True if a dominates b (assuming minimization)."""
    less_or_equal = all(x <= y for x, y in zip(a.fitness, b.fitness))
    strictly_less = any(x < y for x, y in zip(a.fitness, b.fitness))
    return less_or_equal and strictly_less

def non_dominated_sort(population: List[Individual]) -> List[List[Individual]]:
    """Non-dominated sorting -> returns list of fronts (front0 = best)."""
    fronts: List[List[Individual]] = []
    # use dictionaries keyed by object identity
    S = {p: [] for p in population}  # dominated set
    n = {p: 0 for p in population}   # domination count
    for p in population:
        S[p] = []
        n[p] = 0
    for p in population:
        for q in population:
            if p is q:
                continue
            if dominates(p, q):
                S[p].append(q)
            elif dominates(q, p):
                n[p] += 1
    current_front = [p for p in population if n[p] == 0]
    while current_front:
        fronts.append(current_front)
        next_front: List[Individual] = []
        for p in current_front:
            for q in S[p]:
                n[q] -= 1
                if n[q] == 0:
                    next_front.append(q)
        current_front = next_front
    # assign ranks
    for rank, front in enumerate(fronts):
        for ind in front:
            ind.pareto_rank = rank
    return fronts

def crowding_distance(front: List[Individual]) -> None:
    """Compute crowding distance in-place for a front (higher = more isolated)."""
    if not front:
        return
    num_obj = len(front[0].fitness)
    for ind in front:
        ind.crowding_distance = 0.0
    for m in range(num_obj):
        front.sort(key=lambda ind: ind.fitness[m])
        # extremes get infinite distance to preserve them
        front[0].crowding_distance = float("inf")
        front[-1].crowding_distance = float("inf")
        min_val = front[0].fitness[m]
        max_val = front[-1].fitness[m]
        if max_val == min_val:
            # all equal on this objective -> no contribution
            continue
        for i in range(1, len(front) - 1):
            prev_val = front[i - 1].fitness[m]
            next_val = front[i + 1].fitness[m]
            # normalized difference
            dist = (next_val - prev_val) / (max_val - min_val)
            # accumulate
            if front[i].crowding_distance != float("inf"):
                front[i].crowding_distance += dist

class Selection:
    @staticmethod
    def tournament(population: List[Individual], k: int, rng: random.Random) -> Individual:
        contenders = rng.sample(population, k)
        # prefer lower pareto_rank, tie-breaker: higher crowding_distance
        def sort_key(ind: Individual):
            rank = ind.pareto_rank if ind.pareto_rank is not None else 0
            # negative crowding so larger distance becomes smaller key (we want max)
            cd = ind.crowding_distance if ind.crowding_distance is not None else 0.0
            return (rank, -cd)
        winner = min(contenders, key=sort_key)
        return winner

    @staticmethod
    def roulette(population: List[Individual], rng: random.Random) -> Individual:
        # aggregated fitness: invert (minimization) and prefer better pareto ranks
        vals = []
        for ind in population:
            scalar = sum(ind.fitness)
            # weight by rank: lower rank (0) -> boost
            rank_bonus = 1.0 / (1.0 + (ind.pareto_rank or 0))
            vals.append(rank_bonus * (1.0 / (1.0 + scalar)))
        total = sum(vals)
        if total <= 0:
            return rng.choice(population)
        r = rng.random() * total
        upto = 0.0
        for ind, v in zip(population, vals):
            upto += v
            if upto >= r:
                return ind
        return population[-1]

class GeneticAlgorithm:
    def __init__(self,
                 population_size: int,
                 generate_individual: Callable[[], Individual],
                 crossover: Callable[[Individual, Individual, random.Random], Tuple[Individual, Individual]],
                 mutate: Callable[[Individual, random.Random], Individual],
                 objectives: List[Callable],
                 generations: int = 100,
                 crossover_rate: float = 0.8,
                 mutation_rate: float = 0.01,
                 elitism: int = 0,
                 selection_method: str = "tournament",
                 tournament_size: int = 3,
                 multiobj_mode: str = "pareto",
                 scalar_weights: Optional[List[float]] = None,
                 seed: Optional[int] = None,
                 logger: Optional[Any] = None):
        self.population_size = population_size
        self.generate_individual = generate_individual
        self.crossover = crossover
        self.mutate = mutate
        self.objectives = objectives
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism = elitism
        self.selection_method = selection_method
        self.tournament_size = tournament_size
        self.multiobj_mode = multiobj_mode
        self.scalar_weights = scalar_weights
        self.logger = logger
        self.rng = random.Random(seed)

    def _init_population(self) -> List[Individual]:
        pop = [self.generate_individual() for _ in range(self.population_size)]
        for ind in pop:
            ind.evaluate(self.objectives)
        # initial ranking
        if len(self.objectives) > 1 or self.multiobj_mode == "pareto":
            fronts = non_dominated_sort(pop)
            for front in fronts:
                crowding_distance(front)
        return pop

    def _select_parent(self, population: List[Individual]) -> Individual:
        if self.selection_method == "tournament":
            return Selection.tournament(population, self.tournament_size, self.rng)
        elif self.selection_method == "roulette":
            return Selection.roulette(population, self.rng)
        else:
            raise ValueError("Unknown selection method")

    def _compute_scalar_fitness(self, ind: Individual) -> float:
        if self.scalar_weights:
            return sum(w * f for w, f in zip(self.scalar_weights, ind.fitness))
        return sum(ind.fitness)

    def _elitism_select(self, population: List[Individual]) -> List[Individual]:
        if self.elitism <= 0:
            return []
        # ensure pareto ranks + crowding distances available
        if len(self.objectives) > 1 or self.multiobj_mode == "pareto":
            fronts = non_dominated_sort(population)
            for front in fronts:
                crowding_distance(front)
            # flatten by rank then crowding desc
            sorted_pop = []
            for front in fronts:
                sorted_front = sorted(front, key=lambda i: (i.pareto_rank, - (i.crowding_distance or 0.0)))
                sorted_pop.extend(sorted_front)
            return sorted_pop[: self.elitism]
        else:
            sorted_pop = sorted(population, key=lambda i: self._compute_scalar_fitness(i))
            return sorted_pop[: self.elitism]

    def run(self) -> Dict[str, Any]:
        history = []
        population = self._init_population()
        for gen in range(self.generations):
            gen_start = time.time()
            # ensure pareto and crowding info up-to-date
            if len(self.objectives) > 1 or self.multiobj_mode == "pareto":
                fronts = non_dominated_sort(population)
                for front in fronts:
                    crowding_distance(front)
            elites = self._elitism_select(population)
            new_pop = elites.copy()
            while len(new_pop) < self.population_size:
                parent1 = self._select_parent(population)
                parent2 = self._select_parent(population)
                if self.rng.random() < self.crossover_rate:
                    child1, child2 = self.crossover(parent1, parent2, self.rng)
                else:
                    # make shallow copies to avoid aliasing parents if no crossover
                    child1 = Individual(genotype=list(parent1.genotype), phenotype=parent1.phenotype)
                    child2 = Individual(genotype=list(parent2.genotype), phenotype=parent2.phenotype)
                if self.rng.random() < self.mutation_rate:
                    child1 = self.mutate(child1, self.rng)
                if self.rng.random() < self.mutation_rate:
                    child2 = self.mutate(child2, self.rng)
                for c in (child1, child2):
                    c.evaluate(self.objectives)
                    new_pop.append(c)
                    if len(new_pop) >= self.population_size:
                        break
            population = new_pop[: self.population_size]
            # update ranking for logging
            if len(self.objectives) > 1 or self.multiobj_mode == "pareto":
                fronts = non_dominated_sort(population)
                for front in fronts:
                    crowding_distance(front)
            best = min(population, key=lambda i: (i.pareto_rank if i.pareto_rank is not None else 0,
                                                 - (i.crowding_distance or 0.0),
                                                 self._compute_scalar_fitness(i)))
            metrics = {
                "generation": gen,
                "best_fitness": best.fitness,
                "best_pareto_rank": best.pareto_rank,
                "best_crowding_distance": best.crowding_distance,
                "avg_fitness": float(sum(self._compute_scalar_fitness(i) for i in population) / len(population)),
                "duration": time.time() - gen_start,
            }
            if self.logger:
                self.logger.log_generation(gen, population, metrics)
            history.append(metrics)
        best_overall = min(population, key=lambda i: (i.pareto_rank if i.pareto_rank is not None else 0,
                                                     - (i.crowding_distance or 0.0),
                                                     self._compute_scalar_fitness(i)))
        return {"best": best_overall, "history": history}

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

__all__ = ["Individual", "GeneticAlgorithm", "non_dominated_sort", "crowding_distance"]
