# Functional Design — U6 Seguimiento Individual por Deportista

**Fase**: CONSTRUCCIÓN → Functional Design (U6)
**Unidad**: U6 — Seguimiento Individual, en `app/player_tracking/`
**Fuentes directas**: `knowledge-base/metodologia-fmf.md` (Manual 1: Potenciar/Mejorar/Eliminar; C2 estructuras del futbolista; C1 arquitectura del modelo de juego), `session-output-reference.md` (roster por demarcación + objetivos individuales de la plantilla mejorada), `component-methods.md` (C4 PlayerTracking).
**Decisiones aplicadas**: U6 = opción A (v1, unidad propia); D6 (bilingüe).

---

## 1. Propósito y fronteras

U6 gestiona **las personas**: el roster por demarcación, los **objetivos individuales** con la metodología FMF (Potenciar / Mejorar / Eliminar), las observaciones ligadas a sesiones/microciclos, y la ficha/dossier por jugador. Alimenta el bloque de objetivos individuales de la sesión (plantilla mejorada).

**Depende de**: U2 (demarcaciones/posiciones del formato). **Lo consume**: U5 (el orquestador inserta los objetivos individuales en la SessionDoc; U4 los exporta).

**Lo que U6 NO hace**:
- No genera planificación ni tareas (U1/U2/U5).
- No persiste por su cuenta (entrega objetos; U4 los guarda con el plan o aparte).

---

## 2. Metodología de objetivos (Manual 1 FMF)

Cada objetivo individual se clasifica en una de tres categorías:
- **Potenciar** (`potentiate`): fortalezas a llevar más arriba.
- **Mejorar** (`improve`): aspectos en desarrollo.
- **Eliminar** (`eliminate`): errores/hábitos a erradicar.

Un objetivo se considera **dominado** cuando supera un umbral de acierto (criterio FMF: > 90%). Se registra un progreso 0–100.

Marco de contenido: los objetivos se anclan al vocabulario de **fundamentos** (FID/FGL/FCU/FCL de C1/C2) y a los aspectos del futbolista (condicional, coordinativa, cognoscitiva, socioafectiva...). ~4 fundamentos por mes como guía.

---

## 3. Modelo de dominio (entidades inmutables)

### Player
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | str | Id del jugador. |
| `name` | str | Nombre (PII real del usuario; uso local). |
| `position_key` | str | Demarcación (clave de Position de U2). |
| `objectives` | tuple<IndividualObjective> | Objetivos individuales. |

### IndividualObjective
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | str | Id del objetivo. |
| `category` | Enum | `potentiate` \| `improve` \| `eliminate`. |
| `content` | I18nText | Qué se trabaja (bilingüe). |
| `fundamental` | Enum \| null | FID/FGL/FCU/FCL (C1/C2), opcional. |
| `progress_pct` | int (0–100) | Avance; `mastered` si > 90. |

### Observation
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | str | Id. |
| `session_ref` | str | Id de sesión/microciclo al que se liga (trazabilidad). |
| `note` | I18nText | Observación. |
| `created_at` | str | ISO-8601 (inyectado, no reloj interno). |

### Roster
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `team_name` | str | Nombre del equipo. |
| `players` | tuple<Player> | Jugadores por demarcación. |

### PlayerDossier (salida consolidada)
`{ player, objectives_by_category, observations, mastered_count }`.

---

## 4. API pública (contrato) — alineada con component-methods.md

```
create_roster(team_name: str, players: list<PlayerSpec>) -> Roster
add_player(roster: Roster, spec: PlayerSpec) -> Roster
set_individual_objectives(roster, player_id, objectives: list<IndividualObjective>) -> Result<Roster, DomainError>
update_progress(roster, player_id, objective_id, progress_pct: int) -> Result<Roster, DomainError>
add_observation(roster, player_id, session_ref, note: I18nText, created_at) -> Result<Roster, DomainError>
get_player_dossier(roster, player_id) -> Result<PlayerDossier, DomainError>
get_session_individual_goals(roster, session_ref) -> list<PlayerGoal>
    # Objetivos a imprimir en la sesión (plantilla mejorada). Formato ligero:
    # {player_name, position, category, content} -> encaja en SessionDoc.individual_goals.
```

Todas puras/inmutables: las operaciones devuelven un Roster nuevo (no mutan).

---

## 5. Integración con la sesión (plantilla mejorada)

`get_session_individual_goals(roster, session_ref)` produce la lista de objetivos individuales que el orquestador (U5) inserta en `SessionDoc.individual_goals`, y que U4 exporta en el bloque "Objetivos individuales" del HTML/PDF. Formato de cada entrada: `{ player, position, category, goal }` — compatible con lo que U4 ya renderiza.

Criterio de selección v1: para una sesión, se listan los objetivos **no dominados** (progress ≤ 90) de los jugadores, priorizando `eliminate` > `improve` > `potentiate`.

---

## 6. Determinismo y verificación (PBT parcial)

- Todas las operaciones son deterministas (sin reloj interno; `created_at` inyectado).
- Propiedades:
  1. **Inmutabilidad**: `set_individual_objectives` devuelve un roster nuevo; el original no cambia.
  2. **Rango de progreso**: `update_progress` rechaza valores fuera de 0–100.
  3. **Mastered**: un objetivo con progress > 90 cuenta como dominado en el dossier.
  4. **Trazabilidad de observaciones**: toda observación referencia una sesión.
  5. **Round-trip**: Roster serializa/deserializa igual (RNF-6, para que U4 lo guarde).
  6. **Selección de objetivos de sesión**: solo no-dominados, orden eliminate→improve→potentiate.

---

## 7. Errores
`Result`/`DomainError`. Variantes: `PlayerNotFound`, `ObjectiveNotFound`, `InvalidProgress`.

---

## 8. Estructura de código prevista

```
app/
└── player_tracking/
    ├── __init__.py       # API pública de U6
    ├── models.py         # Player, IndividualObjective, Observation, Roster, enums
    ├── tracking.py       # operaciones (create_roster, set_objectives, update_progress, dossier...)
    └── serialization.py  # to_dict/from_dict de Roster (round-trip, RNF-6)
```
