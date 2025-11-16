# Title: feat: Refactor genetic algorithm (selection, elitism, multi-obj) + analytics export

## Summary
Brief summary of changes.

## Changes
- evolution.py: OO refactor; Pareto non-dominated sorting; crowding distance; tournament/roulette selection; elitism
- analytics.py: JSON/CSV export per generation; includes pareto_rank and crowding_distance
- web_app/: Streamlit demo (reads metrics JSON)
- tests/: unit + multiobj + convergence
- .github/workflows/ci.yml: matrix + artifacts

## How to test
- Run unit tests: pytest -q
- Run sample GA with seed to produce output/evolution_metrics.json
- Launch demo: streamlit run web_app/app.py

## Notes
- MLflow is optional and guarded; add MLflow tracking URI via mlflow_config if desired.

## Checklist
- [ ] Lint & format
- [ ] Tests pass
- [ ] Documentation updated