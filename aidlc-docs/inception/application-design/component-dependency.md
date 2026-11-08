# Dependencias entre Componentes — Agente de Fútbol

**Etapa**: INCEPCIÓN → Application Design
**Regla de oro**: dependencias **hacia adentro** (borde → orquestador → dominio → núcleo). El núcleo (PeriodizationEngine) no depende de nadie específico del fútbol ni del borde (RNF-7).

---

## Matriz de dependencias

Lectura: fila **depende de** columna. `●` dependencia directa.

| ↓ depende de →        | Periodiz. | Football | Adapted | Player | Diagram | Planning | Repo | Export | LLM | WebUI |
|-----------------------|:---------:|:--------:|:-------:|:------:|:-------:|:--------:|:----:|:------:|:---:|:-----:|
| **PeriodizationEngine** |    —     |          |         |        |         |          |      |        |     |       |
| **FootballDomain**      |    ●     |    —     |         |        |         |          |      |        |     |       |
| **AdaptedFootballModule** |        |    ●     |    —    |        |         |          |      |        |     |       |
| **PlayerTracking**      |          |    ●     |         |   —    |         |          |      |        |     |       |
| **DiagramRenderer**     |    ●     |    ●     |         |        |    —    |          |      |        |     |       |
| **PlanningService**     |    ●     |    ●     |    ●    |   ●    |    ●    |    —     |  ●   |   ●    |  ●  |       |
| **PlanRepository**      |          |    ●     |         |   ●    |         |          |  —   |        |     |       |
| **Exporter**            |          |    ●     |         |   ●    |    ●    |          |      |   —    |     |       |
| **LLMConnector**        |          |          |         |        |         |          |      |        |  —  |       |
| **WebUI+ChatInterface** |          |          |         |        |         |    ●     |      |        |     |   —   |

Observaciones:
- **PeriodizationEngine**: sin dependencias → es la librería reutilizable (RNF-7).
- **FootballDomain** depende solo del motor (usa su estructura de ciclos/cargas).
- **PlanningService** es el único que conoce a casi todos (orquestador).
- **WebUI** solo habla con el PlanningService (adaptador delgado).
- **LLMConnector** no depende de nada del dominio (conector genérico aislado, D5).
- No hay ciclos de dependencia.

---

## Patrones de comunicación

- **Llamada directa en proceso** (todo corre local en un proceso en la v1). El `PlanRepository` está detrás de una **interfaz** para poder sustituir JSON→SQLite (D2) sin tocar al resto.
- **Puerto opcional** para `LLMConnector`: el PlanningService lo invoca solo si está habilitado; si no, sigue sin él (RNF-2).
- **Contrato de datos** entre capas mediante entidades del dominio (Macrocycle, Mesocycle, Microcycle, Session, Exercise, Player, Diagram). Serializables a JSON (D2) — candidato a PBT de round-trip.

---

## Flujo de datos (generar plan → PDF)

```
WebUI/Chat ──PlanInput──▶ PlanningService
                              │
            ┌─────────────────┼───────────────────────────┐
            ▼                 ▼                           ▼
  PeriodizationEngine   FootballDomain(+Adapted)     PlayerTracking
   (ciclos+cargas)       (tareas por fase/formato)   (objetivos indiv.)
            │                 │                           │
            └───────┬─────────┴───────────┬───────────────┘
                    ▼                     ▼
              DiagramRenderer        (carga/volumen/materiales)
                 (SVG)                      │
                    └──────────┬────────────┘
                               ▼
                        TrainingPlan (con trazabilidad sesión→meso→macro)
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
          PlanRepository   LLMConnector   Exporter
           (JSON disco)    (opcional)     (PDF bilingüe)
```

---

## Límites de capa (para escalar a web — RNF-1)

- **Frontera 1**: WebUI/Chat ↔ PlanningService. Hoy es llamada en proceso; mañana puede ser una API HTTP sin tocar el dominio.
- **Frontera 2**: PlanningService ↔ PlanRepository. Interfaz de repositorio → JSON local hoy, SQLite o base remota después.
- **Frontera 3**: PlanningService ↔ LLMConnector. Puerto opcional → cualquier proveedor.
- El **núcleo** (PeriodizationEngine) queda detrás de todas las fronteras y se publica como paquete reutilizable para otros deportes (RNF-7).
