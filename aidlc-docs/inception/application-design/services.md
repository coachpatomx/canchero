# Servicios de Orquestación — Agente de Fútbol

**Etapa**: INCEPCIÓN → Application Design

El sistema tiene **un servicio orquestador principal** (PlanningService) que coordina el núcleo, el dominio y los adaptadores. Alrededor hay responsabilidades de borde (UI, persistencia, export, LLM) que no orquestan lógica de dominio.

---

## S1 — PlanningService (orquestador principal)

**Rol**: Implementa el comportamiento agéntico central (RF-1): encadenar macro→meso→micro→sesión manteniendo coherencia de objetivos y cargas, e integrar diagramas, seguimiento individual y persistencia.

**Colabora con**:
- `PeriodizationEngine` (C1) — estructura de ciclos y cargas (determinista).
- `FootballDomain` (C2) + `AdaptedFootballModule` (C3) — tareas, formatos, adaptaciones.
- `PlayerTracking` (C4) — objetivos individuales a integrar en la sesión.
- `DiagramRenderer` (C5) — diagramas SVG y gráficas de carga.
- `PlanRepository` (C7) / `Exporter` (C8) — persistencia y PDF.
- `LLMConnector` (C9) — enriquecimiento opcional.

### Flujo principal — Generar plan completo (macro→sesión)

```
1. Recibe PlanInput (de formulario o de entrevista — RF-3).
2. PeriodizationEngine.buildMacrocycle(seasonParams, model)      [determinista]
3. deriveMesocycles → deriveMicrocycles → deriveSessionSlots
4. Para cada SessionSlot:
   a. FootballDomain.suggestTasksForPhase(slot, format)          [relación vertical C5]
   b. AdaptedFootballModule.applyAdaptations(...) si formato adaptado
   c. PlayerTracking.getSessionIndividualGoals(session)          [U6, objetivos individuales]
   d. DiagramRenderer.renderTaskDiagram / renderOrganizationDiagram
   e. Calcular carga/volumen/materiales de la sesión
   f. (opcional) LLMConnector.complete(...) para enriquecer redacción  [RF-10]
5. Ensambla TrainingPlan con trazabilidad sesión→meso→macro       [RNF-5]
6. PlanRepository.save(plan)
7. (a demanda) Exporter.toPdf(plan, lang)                         [D6 bilingüe]
```

**Garantías**:
- La **estructura** (pasos 2-3 y distribución de cargas) es **determinista**: mismas entradas → mismo plan (RF-10, RNF-5). Apto para PBT.
- El agente **funciona sin LLM** (paso 4f es no-op si está desactivado) (RNF-2).

### Flujo de edición

```
editPlan(plan, EditCommand):
  - El comando llega de formulario o de chat (WebUI/ChatInterface).
  - Se recalcula solo lo afectado (sesión/microciclo/meso) preservando coherencia.
  - Se re-renderizan diagramas afectados y se persiste.
```

---

## Responsabilidades de borde (no orquestan dominio)

### B1 — Entrada (WebUI + ChatInterface, C10)
Traduce interacción de usuario en `PlanInput` / `EditCommand`. Dos modos (RF-3): parámetros (formulario) y entrevista (preguntas paso a paso), combinables. Selector de idioma (D6).

### B2 — Persistencia (PlanRepository, C7)
Lee/escribe planes y biblioteca en **JSON** (D2) tras interfaz de repositorio (migrable a SQLite). Portabilidad por carpeta (RNF-6).

### B3 — Exportación (Exporter, C8)
Renderiza el plan/sesión a **PDF** bilingüe con la maqueta de la plantilla mejorada (objetivos individuales, cargas, materiales, volumen, aspectos) (RF-6).

### B4 — Enriquecimiento (LLMConnector, C9)
Servicio **opcional** y enchufable (D5). Nunca en el camino crítico de la generación determinista (RNF-2).

---

---

## S1.b — Regla de alineación: petición de sesión suelta

**Caso de uso** (decidido con el usuario): *"Para esta semana quiero una sesión para trabajar conducción en espacio reducido"*.

**Regla de diseño**:
1. El agente **nunca inventa un macrociclo "al aire"** solo para alinear una sesión. Un macro sin fundamento no genera valor y rompería la coherencia que es el diferenciador del producto (RF-1, RNF-5).
2. Si **existe macro vigente** que cubre "esta semana": el agente ubica el microciclo/fase/carga/objetivo correspondientes y **encaja** la petición (contenido=conducción, condicionante=espacio reducido) dentro de esos límites. La sesión hereda la trazabilidad a meso/macro.
3. Si **no existe macro** (o no cubre esa fecha): el agente **no adivina**. Entra en **modo entrevista** (RF-3) y pide los datos mínimos para construir un macro **con sentido** (duración de temporada, categoría, competición, objetivo). Con eso genera el macro → deriva meso/micro → y recién entonces baja a la sesión pedida, ya alineada.
4. Alternativa degradada explícita: si el usuario insiste en una **sesión suelta sin macro**, el agente la genera igual pero **marca la sesión como "no alineada / sin macro"** (alineación parcial), para que quede claro que no hay hilo hacia arriba.

```
handleSessionRequest(request):
  macro = findCoveringMacro(request.date)
  if macro exists:
      slot = locateSlot(macro, request.date)         # fase + carga objetivo
      return generateSession(slot, context(request)) # encaja conducción/esp. reducido
  else:
      ask minimal season params (modo entrevista)    # construir macro con sentido
      macro = buildMacrocycle(...); derive meso/micro
      slot = locateSlot(macro, request.date)
      return generateSession(slot, context(request))
      # (si el usuario rechaza dar params → sesión suelta marcada "sin macro")
```

Impacto en componentes: afecta a `PlanningService` (orquestación del caso) y a `WebUI/ChatInterface` (disparar entrevista mínima). No cambia el núcleo.

---

## Principios de interacción entre servicios

1. **El núcleo no conoce el borde**: `PeriodizationEngine` no sabe de fútbol, disco, UI ni LLM (RNF-7). `FootballDomain` no sabe de UI ni disco.
2. **Dependencias hacia adentro**: los adaptadores (UI, repo, export, LLM) dependen del orquestador y del dominio, no al revés.
3. **Determinismo aislado**: la generación estructural vive en el motor y es pura/testeable; lo no determinista (LLM) queda en un adaptador opcional.
4. **i18n transversal (D6)**: el contenido del dominio lleva claves de traducción es/en; la UI y el Exporter resuelven el idioma seleccionado.
