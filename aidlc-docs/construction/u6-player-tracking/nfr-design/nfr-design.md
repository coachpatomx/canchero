# NFR Design — U6 Seguimiento Individual

## 1. Estructura
`app/player_tracking/` (ver Functional Design §8).

## 2. Patrones
| NFR | Decisión |
|-----|----------|
| Inmutabilidad | dataclasses frozen; operaciones con `replace`/reconstrucción devuelven Roster nuevo. |
| Determinismo | sin reloj; `created_at` recibido como parámetro. |
| Serialización (RNF-6) | to_dict/from_dict con enums→value, I18nText→{es,en}; round-trip por PBT. |
| Integración sesión | `get_session_individual_goals` devuelve dicts ligeros compatibles con `SessionDoc.individual_goals` (U4/U5). |
| PII | nombres se guardan tal cual (datos del usuario, uso local); no se loguean ni se envían fuera. |

## 3. Test
`tests/test_player_tracking.py`: ejemplos (Potenciar/Mejorar/Eliminar, dossier, mastered) + propiedades (inmutabilidad, rango, round-trip, selección). Integración con U5: el orquestador inserta los goals en la sesión.
