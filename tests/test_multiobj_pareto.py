import pytest
from evolution import Individual, non_dominated_sort, crowding_distance, dominates

def test_known_front_and_crowding():
    # Create 6 individuals forming two clear Pareto-optimal extremes and others dominated
    inds = [
        Individual(genotype=[0.0, 1.0]),
        Individual(genotype=[0.1, 0.9]),
        Individual(genotype=[0.9, 0.1]),
        Individual(genotype=[1.0, 0.0]),
        Individual(genotype=[0.5, 0.5]),
        Individual(genotype=[0.2, 0.8]),
    ]
    def o0(g): return g[0]
    def o1(g): return g[1]
    for ind in inds:
        ind.phenotype = ind.genotype
        ind.evaluate([o0, o1])
    fronts = non_dominated_sort(inds)
    # front0 should contain [0.0,1.0] and [1.0,0.0]
    assert any(ind.genotype == [0.0, 1.0] for ind in fronts[0])
    assert any(ind.genotype == [1.0, 0.0] for ind in fronts[0])
    # compute crowding and ensure extremes get infinite distance
    for front in fronts:
        crowding_distance(front)
        if len(front) >= 2:
            assert any(ind.crowding_distance == float("inf") for ind in front)
    # ensure no dominated pairs in first front
    for a in fronts[0]:
        for b in fronts[0]:
            if a is b:
                continue
            assert not dominates(a, b)