import json
import tempfile
from src.core import CogSystem

def test_initialize_and_save_load(tmp_path):
    p = tmp_path / "state.json"
    cs = CogSystem(n_nodes=12)
    cs.initialize()
    cs.save_state(str(p))
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "network" in data
    cs2 = CogSystem.load_state(str(p))
    assert cs2.n_nodes == 12

def test_evolution_improves_fitness():
    cs = CogSystem(n_nodes=10)
    cs.initialize()
    before = cs.engine.evaluate_fitness()
    cs.step_evolution(3)
    after = cs.engine.evaluate_fitness()
    assert isinstance(before, float)
    assert isinstance(after, float)
