# Functional Design — U2 Dominio Fútbol (+ adaptado)

**Fase**: CONSTRUCCIÓN → Functional Design (U2)
**Unidad**: U2 — Dominio Fútbol, en `app/football_domain/` (+ submódulo `adapted/`)
**Fuentes directas**: `knowledge-base/metodologia-fmf.md` (C1 jerarquía del juego, C2 estructuras, C4 tipos de tarea/23 parámetros, C6 estrategias y fundamentos), `session-output-reference.md` (modelo de Tarea/Sesión), `requirements.md` (RF-7, RF-8, RF-9, soporte a RF-1/RF-5/RF-11), `component-methods.md` (C2, C3).
**Decisiones aplicadas**: D6 (bilingüe), RF-8 ampliado (4 modalidades adaptadas reales: PC, Down, ciegos, amputados), Q4 (fútbol 11 base + catálogo extensible).

---

## 1. Propósito y fronteras

U2 pone **el fútbol** sobre el esqueleto abstracto de U1. Convierte un `SessionSlot` (hueco con fase y carga objetivo que produce U1) en **sugerencias de tareas de fútbol** coherentes, y define todo el vocabulario de dominio: formatos, ejercicios, biblioteca, modelo de juego, aspectos del jugador.

**Depende de U1** (consume sus tipos: `SessionSlot`, `MicroPhase`, etc.). **No depende** de U3/U4/U5/U6.

**Frontera con U1 (RNF-7)**: U1 no sabe de fútbol; U2 sí importa de U1, nunca al revés.

**Lo que U2 NO hace**:
- No dibuja (entrega datos de tarea; U3 los renderiza).
- No persiste (entrega objetos; U4 los guarda).
- No orquesta la cadena macro→sesión (eso es U5/PlanningService).
- No gestiona objetivos individuales por jugador (eso es U6; U2 solo define demarcaciones y aspectos).

---

## 2. Formatos de fútbol (`FootballFormat`)

Un formato es **datos de configuración** (no código), de modo que añadir uno nuevo no toca lógica (RF-7).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | FormatId | `football_11`, `football_7`, `futsal`, `blind_5`, `cp_7`, `amputee`, `down` ... |
| `name` | I18nText | Nombre bilingüe. |
| `players_on_field` | Int | Jugadores por equipo en cancha. |
| `field_length_m` / `field_width_m` | Float | Dimensiones estándar. |
| `match_duration_min` | Int | Duración reglamentaria. |
| `is_adapted` | Bool | Si requiere el submódulo de adaptaciones. |
| `adaptation_profile` | AdaptationProfile \| null | Perfil de adaptación (ver §5) si `is_adapted`. |
| `rules_notes` | List<RuleNote> | Reglas destacadas (cada una con `validated: bool`). |
| `positions` | List<Position> | Demarcaciones del formato (para roster y aspectos). |

**Validación**: `players_on_field` ≥ 1; dimensiones > 0.

### Formatos precargados en v1
| id | Tipo | Jugadores | Cancha aprox. | adaptado |
|----|------|-----------|---------------|----------|
| `football_11` | convencional (base) | 11 | 105×68 | no |
| `football_7` | convencional | 7 | 60×40 | no (estructura lista) |
| `futsal` | convencional | 5 | 40×20 | no (estructura lista) |
| `blind_5` | adaptado — ciegos (B1) | 5 | 40×20 c/vallas | sí |
| `cp_7` | adaptado — parálisis cerebral | 7 | 70×50 | sí |
| `down` | adaptado — discapacidad intelectual/Down | 11 o 7 config | según nivel | sí |
| `amputee` | adaptado — amputados | 7 (6+portero) | 70×60 | sí |

> Las reglas finas de `cp_7`, `down`, `amputee` llevan `validated=false` hasta que el usuario (experto) las revise. `blind_5` se modela con más confianza (dominio del usuario).

---

## 3. Modelo de ejercicio / tarea (`Exercise`)

Diseñado para cubrir la **plantilla mejorada** (materiales, cargas, volumen, aspectos). Es la pieza que U3 dibuja y U4 guarda/exporta.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | ExerciseId | Identificador (para biblioteca, RF-9). |
| `name` | I18nText | Nombre bilingüe. |
| `task_type` | Enum | `general` \| `directed` \| `special` \| `competitive` (especificidad, C4). |
| `didactic_strategy` | Enum | juegos de percepción, juegos de posición, chunks, juegos de línea, SSP, circuitos/estaciones (C6). |
| `objective` | I18nText | Consigna/objetivo de la tarea. |
| `duration_min` | Int | Duración. |
| `space` | SpaceSpec | Dimensiones + categoría (reducido/pequeño/medio/grande/real, C6). |
| `n_players` | PlayerSetup | Situación preferencial (p. ej. 2c1, 8c8+4) y comodines. |
| `materials` | List<Material> | Conos, balones, petos, mini-porterías, y adaptados (balón sonoro, guías...). |
| `load` | LoadSpec | `{ volume, intensity }` relativos (heredan del slot de U1). |
| `aspects` | AspectTags | Técnico / táctico / físico / psicológico (C2/C4) — claves de contenido. |
| `game_model_refs` | List<GameModelRef> | Fase/momento/fundamento del juego que trabaja (C1). |
| `constraints` | List<Constraint> | Normativas/gradiente (facilita/dificulta, C6). |
| `diagram_spec` | DiagramSpec | Datos para que U3 dibuje (jugadores, conos, balones, zonas, flechas). **No es el SVG**, son los datos. |
| `lang_available` | List<Lang> | Idiomas en que está redactada (D6). |

### Enums de dominio (claves estables en inglés + etiquetas bilingües)
- `TaskType`: general, directed, special, competitive (C4).
- `DidacticStrategy`: perception_games, position_games, chunks, line_games, ssp, circuits (C6).
- `SpaceCategory`: reduced, small, medium, large, real (C6).

---

## 4. Vocabulario de modelo de juego (`GameModelVocabulary`) — C1/C2

Catálogo bilingüe que etiqueta los contenidos (lo consumen las tareas y, más tarde, U3 para zonas de cancha y U6 para objetivos).

- **Dinámicas**: con balón / sin balón.
- **Fases**: ataque organizado, transición def-ataque, defensa organizada, transición ataque-def.
- **Momentos** (alimentan zonas de diagrama, C1): inicio estático/dinámico, progresión, ataque en ¾, finalización; pérdidas en zona avanzada/media/baja; recuperaciones.
- **Fundamentos**: FID (individual por demarcación), FGL (grupal de línea), FCU (colectivo universal), FCL (colectivo de línea).
- **Clasificadores**: dinámico/estructural; paralelo complementario/opuesto.

---

## 5. Submódulo adaptado (`adapted/`) — RF-8

### AdaptationProfile (datos por modalidad)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `disability_domain` | Enum | `visual` \| `cerebral_palsy` \| `intellectual` \| `amputee`. |
| `classification` | List<ClassTag> | Clasificación funcional (p. ej. B1/B2/B3 para visual; FT1–FT3 para PC). |
| `material_adaptations` | List<Material> | Balón sonoro, guías/llamador, antifaz, vallas laterales (ciegos); muletas (amputados); etc. |
| `rule_adaptations` | List<RuleNote> | Sin fuera de juego, saque con una mano, zonas, "voy" al presionar, etc. Cada una `validated: bool`. |
| `communication_mode` | List<Enum> | sonoro, verbal, visual, señas — relevante para consignas y diagramas. |
| `coaching_notes` | I18nText | Orientaciones pedagógicas específicas (p. ej. orientación por sonido). |

### Perfiles precargados (v1)
1. **`blind_5` — visual (ciegos)**: balón sonoro, guía tras portería, antifaz obligatorio (salvo portero), vallas laterales, grito "voy" al ir por el balón, orientación por sonido. *Modelado con confianza (dominio del usuario).*
2. **`cp_7` — parálisis cerebral**: campo/equipo reducido, sin fuera de juego, saque de banda con una mano permitido, clasificación FT1–FT3. *`validated=false`.*
3. **`down` — discapacidad intelectual/Down**: reglas base con adaptaciones de clasificación y ritmo; énfasis en consignas claras y repetición. *`validated=false`.*
4. **`amputee` — amputados**: jugadores de campo con muletas (sin prótesis en juego), portero con amputación de brazo; sin contacto de muleta con balón. *`validated=false`.*

### `apply_adaptations(exercise, format)`
Si `format.is_adapted`, inyecta en la tarea: materiales adaptados, notas de regla aplicables, modo de comunicación, y ajusta `diagram_spec` (p. ej. añade zonas y vallas en ciegos). Si el formato no es adaptado, es no-op (devuelve la tarea igual). **Determinista**.

---

## 6. API pública (contrato) — alineada con component-methods.md

```
list_formats() -> List<FootballFormat>
get_format(id: FormatId) -> Result<FootballFormat, DomainError>
register_format(def: FootballFormat) -> Result<FootballFormat, DomainError>   # extensible (RF-7)

create_exercise(spec: ExerciseSpec) -> Result<Exercise, DomainError>
get_library(filter: ExerciseFilter) -> List<Exercise>        # datos en memoria; U4 persiste

suggest_tasks_for_phase(slot: SessionSlot, format: FootballFormat) -> List<Exercise>
    # Núcleo de U2: dado el hueco de U1 (fase + carga) y el formato, propone
    # tareas coherentes (tipo de tarea + estrategia didáctica según la fase, C5/C6).
    # Determinista: mismas entradas -> mismas sugerencias (base reglada).

get_game_model_vocabulary(lang: Lang) -> GameModelVocabulary

# Submódulo adaptado
is_adapted(format: FootballFormat) -> Bool
apply_adaptations(exercise: Exercise, format: FootballFormat) -> Exercise
```

---

## 7. Regla de coherencia tarea↔fase (C5/C6) — el corazón de `suggest_tasks_for_phase`

Mapeo determinista de la **fase del microciclo/sesión** (que viene en el `SessionSlot` de U1) al **tipo de tarea** y **estrategia didáctica** recomendados (tabla fase×estrategia de C6):

| Fase del slot (U1) | Tipo de tarea (C4) | Estrategia didáctica (C6) | Espacio típico |
|--------------------|--------------------|---------------------------|----------------|
| recovery | general | circuits | reduced/small |
| stimulating (central) | special / competitive | position_games / ssp | medium/large |
| optimization (tapering) | directed / special | chunks / line_games | small/medium |
| competitive (día partido) | competitive | ssp / juego real | real |

La carga de la tarea (`load`) **hereda** del `target_load` del slot (U1), garantizando la trazabilidad de cargas (RNF-5). El objetivo de la tarea se alinea con los `objective_focus` del mesociclo.

---

## 8. Determinismo, idioma y errores

- **Determinismo**: `suggest_tasks_for_phase` y `apply_adaptations` son puras (sin reloj ni aleatoriedad). La "creatividad" (redacción, variantes) es trabajo opcional del LLM en U5, no de U2.
- **Bilingüe (D6)**: todo texto de cara al usuario es `I18nText`. U2 transporta ambos idiomas; no decide cuál mostrar.
- **Errores**: reutiliza `Result`/`DomainError` del motor (U1) para un manejo homogéneo. Nuevas variantes si hace falta: `UnknownFormat`, `InvalidExerciseSpec`, `UnknownAdaptation`.

---

## 9. Puntos de verificación (PBT parcial)

1. **Coherencia tarea↔fase**: toda tarea sugerida para un slot tiene `task_type`/`didactic_strategy` dentro del conjunto permitido para esa fase (tabla §7).
2. **Herencia de carga**: la `load` de la tarea sugerida respeta el `target_load` del slot (no lo excede).
3. **Adaptaciones idempotentes**: `apply_adaptations(apply_adaptations(e,f),f) == apply_adaptations(e,f)` (aplicar dos veces = una vez).
4. **No-op en formato convencional**: `apply_adaptations(e, football_11) == e`.
5. **Round-trip de serialización** de `Exercise` y `FootballFormat` (para que U4 los guarde, RNF-6).
6. **Formato como datos**: registrar un formato nuevo no requiere cambios de código (se añade y aparece en `list_formats`).

---

## 10. Trazabilidad requisitos → diseño

| Requisito | Cubierto por |
|-----------|--------------|
| RF-7 multi-formato | §2 formato como datos + `register_format` + 7 formatos precargados |
| RF-8 fútbol adaptado (4 modalidades) | §5 submódulo + 4 AdaptationProfile + `apply_adaptations` |
| RF-9 biblioteca | §3 Exercise con id + `get_library` (U4 persiste) |
| soporte RF-1 | §7 `suggest_tasks_for_phase` consume el slot de U1 |
| soporte RF-5 | §3 `diagram_spec` (datos para U3) |
| soporte RF-11 | tareas por contenido/condicionante (conducción, espacio reducido) vía ExerciseSpec + fase |
| RNF-5 | §7 herencia de carga + §9 propiedades 1,2 |
| RNF-7 | §1 frontera: U2 importa U1, nunca al revés |
| D6 | §8 I18nText en todo |

---

## 11. Estructura de código prevista (para Code Generation)

```
app/
└── football_domain/
    ├── __init__.py          # API pública de U2
    ├── formats.py           # FootballFormat + registry (7 precargados)
    ├── exercise.py          # Exercise, ExerciseSpec, enums de tarea
    ├── game_model.py        # GameModelVocabulary (C1/C2) bilingüe
    ├── suggest.py           # suggest_tasks_for_phase (regla fase↔tarea, §7)
    ├── library.py           # catálogo de ejercicios en memoria (U4 persiste)
    ├── serialization.py     # to_dict/from_dict de Exercise/Format
    └── adapted/
        ├── __init__.py
        ├── profiles.py      # 4 AdaptationProfile (ciegos, PC, Down, amputados)
        └── apply.py         # apply_adaptations
```
