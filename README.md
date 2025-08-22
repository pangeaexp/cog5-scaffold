# Sistema Cognitivo Autónomo — Quinta Generación (cog5)

Descripción breve:

El proyecto "cog5" es un scaffold reproducible que implementa una versión simulada del
Sistema Cognitivo Autónomo de Quinta Generación descrito en la especificación. Está pensado
para servir como base para prototipado, experimentación y futuras integraciones con ML real.

Características principales:
- Arquitectura modular: core, nodes, evolution, analytics, viz, logger, cli
- Simulación de 36 nodos con métricas de metacognición distribuida
- Inicialización dinámica de red neuronal (simulada con graph  weights)
- Algoritmo genético básico para evolución cognitiva
- Reportes JSON/HTML y visualizaciones (network 3D, radar)
- Tests básicos y CI

Quickstart:

1) Crear entorno virtual y instalar:

   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\\Scripts\\activate
   pip install --upgrade pip
   pip install -e .

2) Ejecutar demo de inicialización y generación de report:

   cog5 init --nodes 36 --out demo_state.json
   cog5 evolve --generations 5 --state demo_state.json --out demo_evolved.json
   cog5 report --state demo_evolved.json --out report.html

3) Ejecutar tests:

   pytest -q

Estructura:

 (lista de archivos)

Licencia: MIT

Notas éticas y consideraciones: transparencia, control humano, límites de autonomía.

# cog5_scaffold — minimal additions

Archivos añadidos:
- logger.py — logger central con rotating file + optional JSON
- core.py — validación de paths, límites de upload, wrapper de subprocess con timeout
- api/observability.py — /healthz y /metrics (Flask + prometheus_client)
- models/* — IModel, FakeModel, factory
- tests/* — tests básicos
- .github/workflows/ci.yml — CI snippet con cache pip y soporte Poetry / requirements.txt

Ajusta rutas e imports según tu layout.