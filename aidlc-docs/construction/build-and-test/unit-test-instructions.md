# Instrucciones de Tests Unitarios y PBT

## Ejecutar toda la suite
```bash
.venv/bin/python -m pytest -q
# Resultado esperado: 80 passed
```

## Por unidad
```bash
.venv/bin/python -m pytest tests/test_engine_examples.py tests/test_engine_properties.py -q   # U1
.venv/bin/python -m pytest tests/test_football_domain.py -q                                   # U2
.venv/bin/python -m pytest tests/test_diagrams.py -q                                          # U3
.venv/bin/python -m pytest tests/test_persistence.py -q                                       # U4
.venv/bin/python -m pytest tests/test_orchestrator.py tests/test_webapp.py -q                 # U5
.venv/bin/python -m pytest tests/test_player_tracking.py -q                                   # U6
```

## Pruebas Basadas en Propiedades (PBT, extensión parcial)
Usan Hypothesis. Propiedades clave:
- U1: suma de semanas, cobertura de microciclos, rangos de carga, tapering, **determinismo**, trazabilidad, round-trip, sin-imports-de-fútbol.
- U2: coherencia tarea↔fase, herencia de carga, round-trip, formato como datos.
- U3: SVG bien formado (parseo XML), conteo de jugadores, determinismo, puntos de gráfica.
- U4: round-trip de persistencia, HTML determinista, historial, sin `.tmp`, degradación PDF.
- U5: plan↔semanas, sesión alineada = full, LLM-off determinista, secreto nunca en config.
- U6: inmutabilidad, rango de progreso, mastered (>90%), round-trip.

## Notas
- `conftest.py` añade la raíz a `sys.path`.
- `test_webapp.py` se **omite** automáticamente si FastAPI no está instalado (no falla).
- No se requiere red; el LLM por defecto es NullConnector.
