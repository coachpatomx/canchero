# Functional Design — U1 Motor de Periodización

**Fase**: CONSTRUCCIÓN → Functional Design (por unidad)
**Unidad**: U1 — Motor de Periodización (paquete reutilizable `periodization_engine/`)
**Fuentes directas**: `knowledge-base/metodologia-fmf.md` (C3, C4), `requirements.md` (RF-1, RF-4, RF-10 parte determinista, RNF-5, RNF-7), `component-methods.md` (C1).
**Decisiones aplicadas**: D4 (6 modelos de periodización), Q1=A (paquete reutilizable sin fútbol), Q5=C (dos modos de armado: completo y por partes).
**Modo de ritmo**: B (unidad completa).

---

## 1. Propósito y fronteras

U1 es el **núcleo determinista** del agente. Dada una definición de temporada y un modelo de periodización, produce el árbol completo macrociclo → mesociclos → microciclos → huecos de sesión, con las cargas (volumen/intensidad) distribuidas según la metodología.

**Principio rector (RF-10, RNF-5)**: mismas entradas → mismo árbol. Sin aleatoriedad, sin estado oculto, sin I/O. Todo es función pura de sus argumentos.

**Frontera dura (RNF-7)**: el motor **no conoce nada de fútbol**. No sabe de jugadores, conos, balones ni formatos. Habla de *ciclos, fases, cargas y slots* en términos abstractos del deporte. Un futuro agente de natación debe poder reutilizarlo sin tocar una línea.

**Lo que U1 NO hace**:
- No elige ejercicios (eso es U2).
- No dibuja (eso es U3).
- No lee/escribe disco (eso es U4).
- No llama al LLM (eso es U5).
- No decide fechas de calendario reales más allá de contar semanas/días; el mapeo a fechas concretas lo hace el orquestador (U5) a partir de la fecha de inicio.

---

## 2. Modelo de dominio (entidades)

Todas las entidades son **inmutables** (se construyen y no se mutan; las ediciones producen copias nuevas). Los textos visibles al usuario son **bilingües** (D6): cada etiqueta lleva `{ es, en }`, pero el motor no traduce — solo transporta claves i18n; la UI resuelve el idioma.

### 2.1 SeasonParams (entrada)
Parámetros de temporada que da el usuario (formulario o entrevista).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `startDate` | Date | Inicio de la temporada/macrociclo. |
| `endDate` | Date | Fin previsto. (o `durationWeeks`) |
| `durationWeeks` | Int | Alternativa a endDate; si ambos, se valida coherencia. |
| `trainingDaysPerWeek` | Int | Días de entrenamiento por semana (p. ej. 3–5). |
| `matchesPerWeek` | Int (0,1,2) | Partidos por semana en competencia (afecta estructura de microciclo, C4). |
| `competitionType` | Enum | `league` \| `shortTournament` \| `cup` \| `friendlyOnly` — informa duraciones de período. |
| `category` | Opcional String | Categoría/edad (informativo; no altera la matemática del motor en v1). |
| `objectives` | List<ObjectiveTag> | Objetivos de temporada (claves abstractas, p. ej. `physical.endurance`, `tactical.pressing`). |
| `seasonStartFitness` | Enum | `low` \| `medium` \| `high` — modula la rampa inicial de carga. |

**Validaciones** (fallan con error de dominio, no excepción silenciosa):
- `durationWeeks` ≥ 4 (mínimo para un macro con sentido; por debajo se marca degradado — ver RF-11, lo gestiona U5).
- `trainingDaysPerWeek` entre 1 y 7.
- `endDate` > `startDate` si ambos presentes.

### 2.2 PeriodizationModel
Descriptor de un modelo (precargado o personalizado).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | ModelId | p. ej. `traditional`, `blocks`, `atr`, `tactical`, `structured`, `football_gonzalez`. |
| `name` | I18nText | Nombre bilingüe. |
| `source` | Enum | `builtin` \| `custom`. |
| `rules` | ModelRules | Reglas que gobiernan la derivación (ver §4). |

### 2.3 ModelRules (el corazón configurable — RF-4)
Conjunto declarativo de reglas que cada modelo rellena. Mantenerlo **como datos** (no código) permite `registerCustomModel` sin recompilar.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `periodPlan` | List<PeriodTemplate> | Secuencia de períodos y su duración relativa/absoluta. |
| `mesoPattern` | MesoPattern | Cómo partir cada período en mesociclos (tipos y nº). |
| `microPattern` | MicroPattern | Cómo partir cada mesociclo en microciclos y qué tipo asignar. |
| `loadModel` | LoadModel | Cómo calcular volumen/intensidad por microciclo y la curva intra-microciclo. |
| `restartInCompetition` | Bool | Si reinicia ciclos en plena competencia (caso González). |

### 2.4 Jerarquía de ciclos (salida)

```
Macrocycle
 ├── periods: List<Period>            # Preparatorio, Competitivo, Transitorio (o variante del modelo)
 └── mesocycles: List<Mesocycle>
      └── microcycles: List<Microcycle>
           └── sessionSlots: List<SessionSlot>
```

**Macrocycle**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | MacrocycleId | Identificador estable (hash determinista de entradas — ver §6). |
| `modelId` | ModelId | Modelo usado. |
| `totalWeeks` | Int | Duración total. |
| `periods` | List<Period> | Períodos ordenados. |
| `provenance` | Provenance | Qué entradas lo generaron (trazabilidad, RNF-5). |

**Period**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `kind` | Enum | `preparatory` \| `competitive` \| `transition` (+ variantes del modelo: `resistance`/`strength`/`speed`/`recovery` para González). |
| `stage` | Enum | `general` \| `special` \| `precompetitive` \| `competitive` \| `transition` (etapas de C3). |
| `startWeek` / `endWeek` | Int | Rango en semanas (1-based). |

**Mesocycle**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `type` | Enum | `base` \| `development` \| `stabilization` \| `competitive` \| `recovery` (C3). |
| `periodRef` | PeriodId | Período al que pertenece. |
| `startWeek` / `endWeek` | Int | Rango. |
| `objectiveFocus` | List<ObjectiveTag> | Subconjunto de objetivos del macro priorizados aquí. |

**Microcycle**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `type` | Enum | `introductory` \| `developmental` \| `shock` \| `recovery` \| `precompetitive` \| `competition` (tabla C3). |
| `weekIndex` | Int | Semana dentro del macro (1-based). |
| `matchesThisWeek` | Int | 0/1/2 (de SeasonParams o ajuste). |
| `targetVolumePct` | Int (0–100) | % volumen objetivo (de la tabla C3). |
| `targetIntensityPct` | Int (0–100) | % intensidad objetivo (de la tabla C3). |
| `phases` | List<MicroPhase> | Fases del microciclo (C4): recuperadora, estimuladora, optimización, competitiva. |

**SessionSlot** (el "hueco" que U2/U5 rellenarán con ejercicios)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `dayIndex` | Int | Día dentro del microciclo. |
| `microPhase` | Enum | Fase del microciclo a la que pertenece ese día (C4). |
| `relativeToMatch` | Int | Días respecto al partido (p. ej. -1, +1). `null` si no hay partido. |
| `targetLoad` | LoadPoint | `{ volumePct, intensityPct }` para ese día (curva intra-microciclo). |
| `sessionType` | Enum | `selective` \| `complex` \| `supplementary` (C5), sugerido por el motor; U5 puede cambiarlo. |

**LoadCurve / LoadPoint** — serie de puntos `{ unitIndex, volumePct, intensityPct }` para gráficas (U3).

**Provenance** — `{ seasonParamsHash, modelId, engineVersion }`. Permite afirmar "esta sesión viene de este macro con estas reglas" (RF-1, RNF-5).

---

## 3. API pública (contrato)

Firmas conceptuales (lenguaje-agnóstico; stack se fija en NFR). Todas **puras**.

```
buildMacrocycle(season: SeasonParams, model: PeriodizationModel) -> Result<Macrocycle, DomainError>
deriveMesocycles(macro: Macrocycle, model: PeriodizationModel) -> List<Mesocycle>
deriveMicrocycles(meso: Mesocycle, macro: Macrocycle, model: PeriodizationModel) -> List<Microcycle>
deriveSessionSlots(micro: Microcycle, model: PeriodizationModel) -> List<SessionSlot>
computeLoadCurve(cycle: Macrocycle | Mesocycle | Microcycle) -> LoadCurve
listModels() -> List<PeriodizationModel>              # 6 builtin + custom registrados
getModel(id: ModelId) -> Result<PeriodizationModel, DomainError>
registerCustomModel(def: ModelDefinition) -> Result<PeriodizationModel, DomainError>   # RF-4
```

### Dos modos de armado (Q5=C)
- **Completo**: `buildMacrocycle` + encadenar las tres `derive*` de una pasada → árbol entero.
- **Por partes**: el llamador (U5) invoca nivel a nivel, muestra el resultado parcial, el usuario valida/ajusta, y pasa al siguiente nivel. El motor es apátrida, así que ambos modos usan las mismas funciones; la diferencia es solo quién las orquesta y cuándo.

El motor expone un helper de conveniencia `buildFullTree(season, model) -> Result<Macrocycle, DomainError>` que hace el encadenado completo, para el modo completo.

---

## 4. Reglas de derivación por nivel (especificación desde C3/C4)

### 4.1 Macro → Períodos
Según `model.rules.periodPlan`. Para el **modelo Tradicional** (plantilla base de C3):
- Preparatorio: ~40–55% del total (etapas general ~2/3, especial ~1/3).
- Competitivo: ~35–50%.
- Transitorio: ~5–12% (mínimo 1 semana, recomendado 4–6 si hay espacio).
- Los porcentajes se escalan a `totalWeeks` y se redondean repartiendo el residuo al preparatorio.

Para **González (fútbol, torneos cortos)**: `restartInCompetition = true`. En vez de un preparatorio largo, genera **ciclos cortos** Resistencia→Fuerza→Velocidad→Recuperación de 4–9 semanas, reiniciando dentro del período competitivo. El primer ciclo termina 2ª–3ª semana del torneo.

Para **ATR / Bloques / Táctica / Estructurado**: cada uno rellena `periodPlan`/`mesoPattern` con su lógica (ver §5). La estructura de datos es la misma; cambian los valores.

### 4.2 Período → Mesociclos (`mesoPattern`)
- Preparatorio general → mesociclos `base`/`development` (eleva volumen).
- Preparatorio especial → `development`/`stabilization`.
- Competitivo → `competitive` alternando con `stabilization`/`recovery`.
- Transitorio → `recovery`.
- Duración de cada mesociclo: **2–8 microciclos** (C3); el patrón del modelo fija el objetivo y el motor ajusta para encajar en las semanas del período.

### 4.3 Mesociclo → Microciclos (`microPattern` + tabla de cargas C3)
Asigna a cada semana un `type` y sus `targetVolumePct`/`targetIntensityPct` desde la tabla C3:

| Tipo microciclo | Intensidad % | Volumen % |
|-----------------|--------------|-----------|
| Introductorio/ajuste | 40–60 | 10–30 |
| Desarrollador/ordinario | 60–80 | 30–50 |
| Choque/impacto | 90–100 | 30–50 |
| Recuperación | <50 | 10–30 |
| Precompetitivo | 70–100 | 10–30 |
| Competencia | 90–100 | 10–30 |

El motor toma el **punto medio del rango** como valor determinista por defecto, modulado por `seasonStartFitness` (rampa inicial). Un modelo custom puede fijar valores exactos.

Secuencia típica dentro de un mesociclo de desarrollo: introductorio → desarrollador → desarrollador → choque → recuperación (patrón ondulante). Cada modelo define su propia ondulación en `microPattern`.

### 4.4 Microciclo → SessionSlots (fases C4 + curva intra-microciclo)
- Nº de slots = `trainingDaysPerWeek`.
- Se asigna cada día a una **fase del microciclo** (C4) según `matchesThisWeek` y la distancia al partido:
  - 1 partido/semana: día +1 recuperadora → días centrales estimuladora → días -2/-1 optimización → día de partido competitiva.
  - 0 partidos: todo estimulador/desarrollador (pretemporada).
  - 2 partidos: dos mini-ciclos dentro de la semana.
- La **curva de carga intra-microciclo** concentra la carga en los días centrales (estimuladora) y la baja hacia el partido (optimización), reflejando la respuesta biológica buscada (C4).
- `sessionType` sugerido: complejo por defecto en días centrales; selectivo/suplementario en recuperación.

---

## 5. Los 6 modelos precargados (D4) — reglas diferenciadoras

| Modelo | id | Rasgo clave en `ModelRules` |
|--------|-----|------------------------------|
| Tradicional / lineal (Matveyev) | `traditional` | periodPlan clásico 3 períodos; cargas lineales ascendentes con picos; preparatorio largo. |
| Por bloques (Issurin) | `blocks` | bloques concentrados acumulación→transmutación→realización; pocas capacidades a la vez; alta carga concentrada. |
| ATR | `atr` | mesociclos encadenados Acumulación→Transformación→Realización; residual de cargas. |
| Periodización Táctica (Frade) | `tactical` | morfociclo patrón semanal estable; principios de juego como eje; cargas moduladas por complejidad táctica, no solo físico. |
| Entrenamiento Estructurado (Seirul·lo) | `structured` | estructuras del jugador; microciclos con situaciones simuladoras preferenciales; carga por especificidad. |
| Esquema A. González (fútbol) | `football_gonzalez` | `restartInCompetition=true`; ciclos cortos Resistencia→Fuerza→Velocidad→Recuperación de 4–9 semanas; pensado para torneos cortos (liga MX). |

Todos comparten el **mismo esquema de datos** (`ModelRules`); solo difieren en los valores. Esto es lo que hace que `registerCustomModel` sea trivial: un modelo del usuario es otro `ModelRules` más (RF-4).

---

## 6. Determinismo y trazabilidad (RNF-5)

- `MacrocycleId` = hash determinista de `(SeasonParams normalizados, modelId, engineVersion)`. Mismas entradas → mismo id → mismo árbol.
- Cada entidad hija lleva referencia a su padre (`periodRef`, etc.), de modo que desde un `SessionSlot` se puede remontar a su microciclo, mesociclo, período y macro → cumple "cada sesión sabe a qué objetivo responde" (RF-1).
- `Provenance` guarda el hash de entradas para auditar la coherencia.

---

## 7. Errores de dominio (sin excepciones silenciosas)

`DomainError` con variantes claras y bilingües:
- `InvalidSeasonDuration` (duración < mínimo).
- `InconsistentDates` (endDate ≤ startDate o choca con durationWeeks).
- `UnknownModel` (id no registrado).
- `InvalidModelRules` (custom mal formado: porcentajes fuera de 0–100, patrón vacío).
- `UnsatisfiablePlan` (p. ej. período no cabe en las semanas disponibles).

El motor devuelve `Result` (éxito/error), nunca lanza para flujo de control esperado. U5 traduce el error a mensaje de usuario.

---

## 8. Puntos de verificación (PBT — extensión Activada Parcial)

Como el motor es puro, es candidato ideal para Pruebas Basadas en Propiedades. Propiedades a verificar en Code Generation:

1. **Suma de semanas**: la suma de duraciones de períodos == `totalWeeks` (sin huecos ni solapes).
2. **Cobertura de microciclos**: cada semana del macro pertenece a exactamente un microciclo.
3. **Rangos de carga**: todo `volumePct`/`intensityPct` ∈ [0,100].
4. **Monotonía de la curva competitiva**: en microciclo de 1 partido, la carga de optimización ≤ carga de la fase estimuladora.
5. **Determinismo**: `buildFullTree(s, m)` llamado dos veces con las mismas entradas produce árboles idénticos (mismo id, misma estructura).
6. **Trazabilidad**: todo `SessionSlot` remonta a un `Macrocycle` existente.
7. **Independencia de fútbol**: ningún símbolo del paquete importa/menciona entidades de `app/` (verificación estructural).

---

## 9. Trazabilidad requisitos → diseño

| Requisito | Cubierto por |
|-----------|--------------|
| RF-1 planificación encadenada | §2 jerarquía + §4 derivación + §6 trazabilidad |
| RF-4 periodización configurable | §2.3 ModelRules como datos + `registerCustomModel` + §5 |
| RF-10 (parte determinista) | §1 principio rector + §3 funciones puras |
| RNF-5 coherencia/trazabilidad | §6 + §8 propiedades 1,2,6 |
| RNF-7 motor reutilizable | §1 frontera dura + §8 propiedad 7 |
| D4 (6 modelos) | §5 |
| Q5 (dos modos de armado) | §3 "Dos modos de armado" |

---

## 10. Dependencias e interfaces hacia otras unidades

- **Hacia arriba (consumidores)**: U5 (orquestador) llama la API; U3 consume `LoadCurve`; U2 recibe `SessionSlot` para sugerir tareas.
- **Hacia abajo**: ninguna. U1 no depende de nadie (confirma matriz de dependencias).
- **Contrato estable**: las entidades de §2 y la API de §3 son el contrato público. Cambios aquí impactan a U2/U3/U5, así que se versiona (`engineVersion`).
