# Code Generation Plan — U2 Dominio Fútbol

**Destino**: `app/football_domain/` (workspace root). Depende de `periodization_engine` (U1).

## Pasos
- [x] 1. `app/__init__.py` — marca el paquete de la aplicación.
- [x] 2. `app/football_domain/game_model.py` — enums de dominio + GameModelVocabulary (C1/C2) bilingüe.
- [x] 3. `app/football_domain/exercise.py` — Exercise, ExerciseSpec, SpaceSpec, Material, LoadSpec, AspectTags, enums, DiagramSpec.
- [x] 4. `app/football_domain/adapted/profiles.py` — 4 perfiles (ciegos, PC, Down, amputados) con RuleNote(validated).
- [x] 5. `app/football_domain/formats.py` — FootballFormat + registry (7 precargados) + unvalidated_rules.
- [x] 6. `app/football_domain/adapted/apply.py` — apply_adaptations (idempotente, no-op convencional).
- [x] 7. `app/football_domain/suggest.py` — suggest_tasks_for_phase (tabla fase→tarea, herencia de carga).
- [x] 8. `app/football_domain/library.py` — biblioteca en memoria.
- [x] 9. `app/football_domain/serialization.py` — to_dict/from_dict de Exercise y FootballFormat.
- [x] 10. `__init__.py` de football_domain y adapted — API pública.
- [x] 11. `tests/test_football_domain.py` — 9 ejemplos + 4 propiedades PBT + round-trip; `conftest.py` para sys.path.
- [x] 12. Ejecutar pytest completo (U1+U2) → **31 passed**.
- [x] 13. Resumen en `code/code-summary.md`.
