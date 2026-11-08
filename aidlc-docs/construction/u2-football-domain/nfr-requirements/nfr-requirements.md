# NFR Requirements — U2 Dominio Fútbol

**Fase**: CONSTRUCCIÓN → NFR Requirements (U2)
**Hereda**: stack y criterios de U1 (Python 3.11+, inmutabilidad, determinismo, PBT parcial).

## 1. Tecnología
- Python 3.11+ (mismo stack que U1). Paquete `app/football_domain/`.
- **Depende de** `periodization_engine` (U1) para tipos como `SessionSlot`, `MicroPhase`. Importación unidireccional (U2→U1).
- Núcleo sin dependencias de terceros en runtime (catálogos como datos Python). Serialización vía stdlib `json`/`dataclasses`.

## 2. NFR aplicables
| NFR | Aplica | Cómo |
|-----|--------|------|
| RNF-2 offline | Sí | Catálogos y sugerencias 100% locales; sin red. |
| RNF-4 tecnología | Sí | Python, stdlib. |
| RNF-5 trazabilidad | Sí | La tarea hereda carga/objetivo del slot de U1; verificado por PBT. |
| RNF-6 portabilidad | Sí | Exercise/Format serializables a dict JSON (round-trip). |
| RNF-7 reutilizable | N/A directo | U2 es específico de fútbol; respeta la frontera con el motor. |
| D6 bilingüe | Sí | I18nText en todo texto de usuario. |

## 3. Rendimiento
- `suggest_tasks_for_phase` y `apply_adaptations` son O(catálogo); instantáneos a escala humana (< 50 ms).

## 4. Calidad / verificación (PBT parcial)
- Las 6 propiedades del Functional Design §9 con Hypothesis.
- Round-trip de serialización de `Exercise` y `FootballFormat`.

## 5. Restricciones
- Sin reloj del sistema ni aleatoriedad en la lógica de sugerencia (determinismo).
- Reglas finas de modalidades no-ciegos con `validated=false` hasta revisión del usuario; nunca presentarlas como verificadas.
