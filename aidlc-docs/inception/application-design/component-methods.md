# Métodos de Componentes — Agente de Fútbol

**Nota**: Firmas de alto nivel (entradas/salidas conceptuales). **Sin lógica detallada** — eso llega en Functional Design por unidad. Lenguaje-agnóstico (el stack se fija en NFR Requirements). Los tipos en `PascalCase` son entidades del dominio.

---

## C1 — PeriodizationEngine (U1)

```
buildMacrocycle(seasonParams: SeasonParams, model: PeriodizationModel) -> Macrocycle
    // Genera el macrociclo (períodos, duración) según el modelo elegido. Determinista.

deriveMesocycles(macro: Macrocycle) -> List<Mesocycle>
    // Deriva mesociclos coherentes (tipo, objetivos, distribución de cargas).

deriveMicrocycles(meso: Mesocycle) -> List<Microcycle>
    // Deriva microciclos (tipo 1/2 partidos, fases, % carga volumen/intensidad).

deriveSessionSlots(micro: Microcycle) -> List<SessionSlot>
    // Define los "huecos" de sesión del microciclo con su fase y carga objetivo.

computeLoadCurve(cycle: Cycle) -> LoadCurve
    // Curva de volumen/intensidad para gráficas (alimenta DiagramRenderer).

listModels() -> List<PeriodizationModel>
    // Modelos precargados (D4) + modelos definidos por el usuario.

registerCustomModel(def: ModelDefinition) -> PeriodizationModel
    // Sobrescribir reglas / definir metodología propia (RF-4).
```

---

## C2 — FootballDomain (U2)

```
listFormats() -> List<FootballFormat>
    // 11, 7, sala, ciegos (+ extensibles). Config: nº jugadores, dimensiones, reglas.

getFormat(id: FormatId) -> FootballFormat

createExercise(spec: ExerciseSpec) -> Exercise
    // Tarea: tipo, duración, dimensiones, materiales, carga, volumen, intensidad,
    // aspectos (téc/tác/fís/psi), ref. a modelo de juego, idioma (es/en).

getLibrary(filter: ExerciseFilter) -> List<Exercise>
    // Biblioteca reutilizable (RF-9).

suggestTasksForPhase(slot: SessionSlot, format: FootballFormat) -> List<Exercise>
    // Tareas coherentes con la fase de sesión (relación vertical, C5) y el formato.

getGameModelVocabulary(lang: Lang) -> GameModelVocabulary
    // Dinámicas/fases/momentos/fundamentos (C1-C2), bilingüe.
```

### C3 — AdaptedFootballModule (submódulo)

```
isAdapted(format: FootballFormat) -> Boolean

applyAdaptations(exercise: Exercise, format: FootballFormat) -> Exercise
    // Inyecta adaptaciones (balón sonoro, guías, zonas, materiales) si el formato lo requiere (RF-8).
```

### C4 — PlayerTracking (U6)

```
createRoster(team: Team, players: List<PlayerSpec>) -> Roster
    // Jugadores por demarcación.

setIndividualObjectives(player: PlayerId, objectives: PotentiateImproveEliminate) -> Player
    // Metodología FMF Manual 1 (Potenciar/Mejorar/Eliminar) + fundamentos por mes.

addObservation(player: PlayerId, sessionRef: SessionId, note: Observation) -> void
    // Observación ligada a sesión/microciclo (trazabilidad).

getPlayerDossier(player: PlayerId) -> PlayerDossier
    // Ficha consolidada (objetivos, observaciones, evolución).

getSessionIndividualGoals(session: SessionId) -> List<PlayerGoal>
    // Objetivos individuales a imprimir en la sesión (plantilla mejorada).
```

---

## C5 — DiagramRenderer (U3)

```
renderTaskDiagram(exercise: Exercise, format: FootballFormat) -> SvgDiagram
    // Cancha esquemática: jugadores, conos, balones, zonas, flechas. SVG (D3).

renderOrganizationDiagram(session: Session) -> SvgDiagram
    // Diagrama de organización general (cancha completa con zonas).

renderLoadChart(loadCurve: LoadCurve) -> SvgChart
    // Gráfica de volumen/intensidad por micro/meso (secundario).
```

---

## C6 — PlanningService (orquestador)

```
generatePlan(input: PlanInput) -> TrainingPlan
    // Flujo agéntico completo macro→meso→micro→sesión (RF-1). Determinista en estructura.
    // input puede venir por formulario (parámetros) o construirse por entrevista (RF-3).

generateSession(slot: SessionSlot, context: PlanContext) -> Session
    // Ensambla una sesión: tareas (C2) coherentes con fase + objetivos individuales (C4)
    // + diagramas (C5) + carga/volumen/materiales. Mantiene trazabilidad a meso/macro.

editPlan(plan: TrainingPlan, change: EditCommand) -> TrainingPlan
    // Aplica edición (desde formulario o chat) y regenera la salida afectada (RF-6).

enrichContent(session: Session, options: LlmOptions) -> Session
    // Enriquecimiento opcional del contenido vía LLM (RF-10). No-op si LLM desactivado.

savePlan(plan: TrainingPlan) -> PlanRef           // -> C7
exportPlanPdf(plan: TrainingPlan, lang: Lang) -> PdfFile   // -> C8
```

---

## C7 — PlanRepository (U4)

```
save(plan: TrainingPlan) -> PlanRef           // JSON en disco (D2)
load(ref: PlanRef) -> TrainingPlan
listHistory(filter: HistoryFilter) -> List<PlanRef>
saveExercise(ex: Exercise) -> ExerciseRef     // biblioteca
loadExercise(ref: ExerciseRef) -> Exercise
    // Todo tras una interfaz de repositorio → permite migrar JSON→SQLite al escalar.
```

## C8 — Exporter (U4)

```
toPdf(plan: TrainingPlan, lang: Lang) -> PdfFile
toPdfSession(session: Session, lang: Lang) -> PdfFile
    // Maqueta tipo plantilla mejorada (encabezado, tareas+diagramas, objetivos
    // individuales, cargas, materiales, volumen, aspectos). Bilingüe (D6).
```

## C9 — LLMConnector (U5, opcional)

```
isEnabled() -> Boolean
complete(prompt: Prompt, config: LlmConfig) -> LlmResponse
    // Conector genérico (D5): nube (OpenAI/Anthropic) o local (Ollama).
    // API key desde configuración/entorno (RNF-3).
```

## C10 — WebUI + ChatInterface (U5)

```
// Formularios (modo parámetros) y entrevista (modo preguntas) — RF-3
submitParameters(form: PlanForm) -> PlanInput
startInterview() -> InterviewSession
answer(interview: InterviewSession, reply: UserReply) -> NextQuestion | PlanInput

// Chat de ajustes
sendChat(message: String) -> EditCommand | Answer

// Navegación/edición y preferencias
renderPlan(plan: TrainingPlan, lang: Lang) -> View
setLanguage(lang: Lang) -> void    // es/en (D6)
    // Adaptador: delega toda la lógica en PlanningService.
```
