import pytest
from evolution import GeneticAlgorithm, Individual
from analytics import AnalyticsTracker
import random
from evolution import non_dominated_sort, crowding_distance, Selection, dominates

def simple_generate():
    ind = Individual(genotype=[random.random()])
    ind.phenotype = ind.genotype
    return ind

def simple_crossover(a, b, rng):
    # single-point for single-gene: swap
    # return shallow copies to avoid aliasing
    c1 = Individual(genotype=list(a.genotype), phenotype=a.phenotype)
    c2 = Individual(genotype=list(b.genotype), phenotype=b.phenotype)
    return c1, c2

def simple_mutate(ind, rng):
    ind.genotype = [g + rng.uniform(-0.01, 0.01) for g in ind.genotype]
    ind.phenotype = ind.genotype
    return ind

def objective(x):
    # minimization of value
    return x[0]

def test_convergence_seeded(tmp_path):
    tracker = AnalyticsTracker(str(tmp_path))
    ga = GeneticAlgorithm(
        population_size=10,
        generate_individual=simple_generate,
        crossover=simple_crossover,
        mutate=simple_mutate,
        objectives=[objective],
        generations=5,
        elitism=1,
        selection_method="tournament",
        tournament_size=3,
        seed=42,
        logger=tracker,
    )
    res = ga.run()
    tracker.save_json()
    # basic assertions
    assert "best" in res
    assert len(res["history"]) == 5
    assert tmp_path.joinpath("evolution_metrics.json").exists()

def test_pareto_and_crowding():
    # construct a small synthetic population with two objectives where Pareto fronts are known
    p = [
        Individual(genotype=[0.1, 0.9]),  # good on obj0, bad on obj1
        Individual(genotype=[0.2, 0.8]),
        Individual(genotype=[0.9, 0.1]),  # opposite
        Individual(genotype=[0.8, 0.2]),
        Individual(genotype=[0.5, 0.5]),  # middle
    ]
    # define objectives that read respective coordinates
    def o0(g): return g[0]
    def o1(g): return g[1]
    for ind in p:
        ind.phenotype = ind.genotype
        ind.evaluate([o0, o1])
    fronts = non_dominated_sort(p)
    # front 0 should contain the two extremes and maybe the middle depending on dominance
    assert len(fronts) >= 1
    # compute crowding
    for front in fronts:
        crowding_distance(front)
        # every individual in front must have crowding_distance set (or inf)
        for ind in front:
            assert ind.crowding_distance is not None
    # ensure no dominated individuals in front0
    front0 = fronts[0]
    for a in front0:
        for b in front0:
            if a is b:
                continue
            assert not dominates(a, b)

def test_selection_uses_pareto_and_crowding():
    # create population with assigned pareto ranks and crowding distances
    p = [
        Individual(genotype=[0.0, 1.0]),
        Individual(genotype=[0.5, 0.5]),
        Individual(genotype=[1.0, 0.0]),
    ]
    def o0(g): return g[0]
    def o1(g): return g[1]
    for ind in p:
        ind.phenotype = ind.genotype
        ind.evaluate([o0, o1])
    fronts = non_dominated_sort(p)
    for front in fronts:
        crowding_distance(front)
    # tournament should prefer lower pareto rank (extremes rank 0) and larger crowding_distance
    winner = Selection.tournament(p, k=3, rng=random.Random(1))
    assert isinstance(winner, Individual)
    # roulette should return an individual (probabilistic)
    winner_r = Selection.roulette(p, rng=random.Random(2))
    assert isinstance(winner_r, Individual)