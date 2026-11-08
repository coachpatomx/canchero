# Code Generation Plan — U1 Motor de Periodización

**Fase**: CONSTRUCCIÓN → Code Generation (U1)
**Destino del código**: `periodization_engine/` (workspace root `/kiro`). Docs aquí.

## Pasos

- [x] 1. `periodization_engine/errors.py` — `DomainError` (enum + mensaje i18n), `Ok`/`Err`/`Result`.
- [x] 2. `periodization_engine/domain.py` — `I18nText`, enums, dataclasses frozen (SeasonParams, PeriodizationModel, ModelRules, Macrocycle, Period, Mesocycle, Microcycle, SessionSlot, LoadPoint, LoadCurve, Provenance).
- [x] 3. `periodization_engine/loadtable.py` — tabla C3 de % carga por tipo de microciclo.
- [x] 4. `periodization_engine/models/` — los 6 modelos builtin como `ModelRules` + registry (listModels/getModel/registerCustomModel).
- [x] 5. `periodization_engine/engine.py` — funciones puras: buildMacrocycle, deriveMesocycles, deriveMicrocycles, deriveSessionSlots, computeLoadCurve, buildFullTree; hash determinista; reparto de semanas robusto (Hamilton).
- [x] 6. `periodization_engine/serialization.py` — to_dict/from_dict (round-trip, RNF-6).
- [x] 7. `periodization_engine/__init__.py` — API pública + ENGINE_VERSION.
- [x] 8. `pyproject.toml` — metadata del paquete + deps de test (hypothesis, pytest).
- [x] 9. `tests/test_engine_examples.py` — 11 ejemplos concretos por modelo.
- [x] 10. `tests/test_engine_properties.py` — 7 propiedades PBT + round-trip con Hypothesis.
- [x] 11. Crear venv, instalar hypothesis/pytest, ejecutar tests → **18 passed**.
- [x] 12. Resumen en `code/code-summary.md`.
