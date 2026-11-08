# NFR Design — U2 Dominio Fútbol

**Fase**: CONSTRUCCIÓN → NFR Design (U2)

## 1. Estructura (ver Functional Design §11)
`app/football_domain/` con submódulo `adapted/`. `__init__.py` re-exporta la API pública.

## 2. Patrones
| NFR | Decisión |
|-----|----------|
| Catálogos como datos (RF-7/RF-8) | Formatos y perfiles de adaptación son instancias de dataclasses frozen en módulos de datos; registry en memoria con `register_format`. |
| Determinismo (RNF-5) | `suggest_tasks_for_phase` usa una tabla fija fase→(tipo,estrategia,espacio) (§7 FD). Sin estado. |
| Herencia de carga | La tarea copia `volume/intensity` del `SessionSlot.target_load` de U1; no recalcula. |
| Idempotencia de adaptaciones | `apply_adaptations` marca la tarea con un set de adaptaciones ya aplicadas; reaplicar no duplica. |
| Serialización (RNF-6) | `to_dict/from_dict` reutiliza el patrón de U1 (enums→value, I18nText→{es,en}); round-trip por PBT. |
| Frontera con U1 | Importa de `periodization_engine`; test estructural verifica que U1 no importa de `app/`. |

## 3. Manejo de `validated`
Cada `RuleNote` lleva `validated: bool`. La API expone un helper `unvalidated_rules(format)` para que U5 muestre un aviso "pendiente de revisión" al entrenador. No bloquea el uso.

## 4. Idioma
Enums con clave inglesa estable + tabla de etiquetas `{es,en}`. U2 no traduce; transporta.

## 5. Test
`tests/` a nivel de proyecto. Hypothesis genera `SessionSlot` (reusando estrategias de U1) + formatos, y verifica las 6 propiedades + round-trip.
