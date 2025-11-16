import math
import statistics
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional

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


class AnalyticsTracker:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.generations: List[Dict[str, Any]] = []

    def log_generation(self, gen: int, population: List[Any], metrics: Dict[str, Any]):
        # record minimal representation to keep files small
        pop_record = []
        for ind in population:
            pop_record.append({
                "id": getattr(ind, "id", None),
                "fitness": getattr(ind, "fitness", None),
                "genotype": getattr(ind, "genotype", None),
                "pareto_rank": getattr(ind, "pareto_rank", None),
                "crowding_distance": getattr(ind, "crowding_distance", None),
            })
        entry = {
            "generation": gen,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": metrics,
            "best": pop_record[0] if pop_record else None,
            "population": pop_record,
        }
        self.generations.append(entry)

    def save_json(self, path: Optional[str] = None):
        path = path or f"{self.output_dir}/evolution_metrics.json"
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(self.generations, fh, indent=2)

    def save_csv(self, path: Optional[str] = None):
        path = path or f"{self.output_dir}/evolution_metrics.csv"
        # flatten: one row per individual per generation
        fieldnames = ["generation", "timestamp", "ind_id", "fitness", "genotype", "pareto_rank", "crowding_distance"]
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for gen in self.generations:
                for ind in gen.get("population", []):
                    writer.writerow({
                        "generation": gen["generation"],
                        "timestamp": gen["timestamp"],
                        "ind_id": ind.get("id"),
                        "fitness": json.dumps(ind.get("fitness")),
                        "genotype": json.dumps(ind.get("genotype")),
                        "pareto_rank": ind.get("pareto_rank"),
                        "crowding_distance": ind.get("crowding_distance"),
                    })

    def log_mlflow(self, run_name: str, params: Dict[str, Any]):
        try:
            import mlflow

            mlflow.start_run(run_name=run_name)
            for k, v in params.items():
                mlflow.log_param(k, v)
            # log generation metrics as artifacts
            tmp_json = f"{self.output_dir}/evolution_metrics.json"
            self.save_json(tmp_json)
            mlflow.log_artifact(tmp_json, artifact_path="metrics")
            mlflow.end_run()
        except Exception:
            # mlflow is optional; fail silently if not installed/configured
            pass