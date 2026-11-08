# Diseño de Aplicación (consolidado) — Agente de Fútbol

**Etapa**: INCEPCIÓN → Application Design
**Fecha**: 2026-11-07
**Documentos relacionados**: `components.md`, `component-methods.md`, `services.md`, `component-dependency.md`, `session-output-reference.md`, y `../plans/execution-plan.md`.

---

## 1. Resumen

Agente **local** que encadena de forma **determinista** macrociclo → mesociclo → microciclo → sesión para fútbol (todas las modalidades), con **diagramas** de cancha, **seguimiento individual** por jugador/a, salida **editable** y **exportable a PDF bilingüe**. Núcleo de periodización reutilizable; diseñado para escalar a web sin rehacer el núcleo.

## 2. Decisiones de diseño (D1–D6)

| ID | Decisión | Impacto en el diseño |
|----|----------|----------------------|
| D1 | Arquitectura modular por capas ligeras | Núcleo aislado + adaptadores; sin puertos/adaptadores pesados |
| D2 | JSON en disco, repositorio tras interfaz | Portabilidad (RNF-6); migrable a SQLite |
| D3 | Diagramas en SVG | Nítido en pantalla/PDF; zonas/momentos |
| D4 | 5 modelos de periodización | Tradicional, Bloques, ATR, Periodización Táctica, Entrenamiento Estructurado |
| D5 | Conector LLM genérico | Nube o local, opcional |
| D6 | Bilingüe es/en | i18n transversal (dominio + UI + export) |
| U6 | Seguimiento individual en v1 (opción A) | Componente PlayerTracking integrado al núcleo |

## 3. Arquitectura (capas)

- **Núcleo compartido**: `PeriodizationEngine` (U1) — determinista, sin fútbol (RNF-7).
- **Dominio fútbol**: `FootballDomain` (U2) + `AdaptedFootballModule` (RF-8) + `PlayerTracking` (U6).
- **Visual**: `DiagramRenderer` (U3, SVG).
- **Orquestación**: `PlanningService` (cadena agéntica).
- **Adaptadores (borde)**: `PlanRepository` (U4), `Exporter` (U4), `LLMConnector` (U5), `WebUI+ChatInterface` (U5).

Diagrama y matriz de dependencias completos en `components.md` y `component-dependency.md`. No hay ciclos; dependencias hacia adentro.

## 4. Modelo de datos (entidades clave)

- **Macrocycle** → períodos, duración, modelo de periodización, objetivos de temporada.
- **Mesocycle** → tipo, objetivos, distribución de cargas.
- **Microcycle** → tipo (1/2 partidos), fases, % volumen/intensidad.
- **Session** → metadatos (equipo, fecha, torneo, semana, meso/micro/nº), carácter, objetivo, **carga/volumen totales**, **materiales agregados**, **objetivos individuales por jugador/a**, lista ordenada de tareas, idioma.
- **Exercise/Task** → tipo (analítico/específico/juego/global), duración, dimensiones, descripción, **materiales**, **carga**, **volumen**, **intensidad**, aspectos (téc/tác/fís/psi), ref. a diagrama, ref. a modelo de juego.
- **Player** (U6) → demarcación, objetivos **Potenciar/Mejorar/Eliminar**, fundamentos por mes, observaciones ligadas a sesiones/microciclos.
- **Diagram** → SVG (tarea u organización) + leyenda.
- **FootballFormat** → 11/7/sala/ciegos (nº jugadores, dimensiones, reglas, materiales por defecto).

Todas serializables a JSON (D2). La estructura de salida de sesión sigue la **plantilla mejorada** descrita en `session-output-reference.md`.

## 5. Trazabilidad de requisitos

| Req | Dónde se cumple |
|-----|-----------------|
| RF-1 planificación encadenada | PlanningService + PeriodizationEngine |
| RF-2 web local + chat | WebUI+ChatInterface |
| RF-3 doble modo de entrada | WebUI (parámetros + entrevista) |
| RF-4 periodización configurable | PeriodizationEngine (5 modelos + custom) |
| RF-5 diagramas y gráficas | DiagramRenderer (SVG) |
| RF-6 editable + PDF | PlanningService.editPlan + Exporter |
| RF-7 multi-formato | FootballDomain (formatos) |
| RF-8 fútbol adaptado | AdaptedFootballModule |
| RF-9 historial + biblioteca | PlanRepository |
| RF-10 motor híbrido | determinista (Engine) + LLMConnector opcional |
| RF-11 sesión suelta alineada al macro | PlanningService (regla S1.b) + WebUI/Chat (entrevista mínima) |
| RNF-1 local escalable | capas + fronteras (component-dependency §Límites) |
| RNF-2 offline | LLM opcional, no-op si desactivado |
| RNF-3 secretos | API key por configuración (LLMConnector) |
| RNF-5 coherencia/trazabilidad | PlanningService (sesión→meso→macro), PBT |
| RNF-6 portabilidad | PlanRepository JSON por carpeta |
| RNF-7 motor reutilizable | PeriodizationEngine sin dependencias de fútbol |
| U6 seguimiento individual | PlayerTracking |

## 6. Validación de completitud y consistencia

- [x] Todos los RF/RNF tienen componente responsable (tabla §5).
- [x] Cada unidad U1–U6 mapea a componentes (ver `components.md` §Trazabilidad).
- [x] Sin ciclos de dependencia; núcleo aislado (RNF-7).
- [x] Determinismo aislado del LLM (RF-10, RNF-2).
- [x] Modelo de datos cubre la plantilla de salida mejorada (objetivos individuales, cargas, materiales, volumen).
- [x] i18n (D6) contemplado transversalmente.
- [x] Fronteras definidas para escalar a web (RNF-1).

## 7. Qué se decide después (no en esta etapa)

- **Stack tecnológico** concreto (lenguaje, framework web, librería SVG/PDF) → NFR Requirements.
- **Reglas detalladas** de cada modelo de periodización y de la relación vertical de tareas → Functional Design (U1, U2).
- **Esquema JSON** exacto y validaciones → Functional Design + PBT.

---

## 8. Próximo paso

**Units Generation**: formalizar U1–U6 como unidades de trabajo con su alcance, dependencias y orden de construcción, para luego entrar a Construcción por unidad (Functional Design → NFR → Code Generation).
