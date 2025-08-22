import math
import statistics
from typing import Dict, Any

class MetricsCollector:
    def __init__(self):
        self.data: Dict[str, Any] = {}

    def collect(self, network):
        # compute coherence (inverse of variance of activations), synchronization (mean activation), complexity (edges/nodes), entropy (of weights distribution), potential adaptive (heuristic)
        activations = [network.nodes[i].activation for i in network.nodes]
        coherence = 0.0
        if activations:
            coherence = 1.0 / (1.0 + statistics.pvariance(activations))
        synchronization = statistics.mean(activations) if activations else 0.0
        complexity = network.graph.number_of_edges() / max(1, network.n_nodes)
        weights = [d.get("weight", 0) for _, _, d in network.graph.edges(data=True)]
        if weights:
            # entropy over discretized bins
            bins = 10
            hist = [0] * bins
            for w in weights:
                idx = min(bins - 1, int((w + 1) / 2 * bins))
                hist[idx] = 1
            probs = [h / sum(hist) for h in hist if sum(hist) > 0]
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        else:
            entropy = 0.0
        potential = complexity * (1.0 - abs(0.5 - (statistics.mean([abs(w) for w in weights]) if weights else 0.0)))

        self.data.setdefault("snapshots", []).append({
            "coherence": coherence,
            "synchronization": synchronization,
            "complexity": complexity,
            "entropy": entropy,
            "potential": potential
        })

    def snapshot(self):
        return self.data.get("snapshots", [])[-1] if self.data.get("snapshots") else {}
