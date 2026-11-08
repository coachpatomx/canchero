# Plan de Units Generation — Agente de Fútbol

**Etapa**: INCEPCIÓN → Units Generation (Parte 1: Planificación)
**Objetivo**: Formalizar las unidades de trabajo (U1–U6) con alcance, dependencias, orden de construcción y estrategia de organización de código, antes de entrar a Construcción por unidad.

> Contexto: proyecto **greenfield**, **un solo usuario** (no hay equipos ni historias de usuario formales), **agente local** monolítico con módulos lógicos. Las unidades ya salieron del Application Design (components.md). Este plan solo necesita cerrar algunas decisiones de decomposición y luego genera los artefactos.

---

## Parte A — Preguntas de decomposición

Responde con la letra después de `[Answer]:`. Si ninguna encaja, usa **X) Otro** y describe. Avísame cuando termines.

### Pregunta Q1 — Modelo de despliegue / organización de código
Dado que es un agente local (monolito con módulos), ¿cómo prefieres organizar el código?

A) **Monolito modular** — un solo proyecto/app, con el motor de periodización (U1) como **paquete/librería interna separada y reutilizable** (para que otro deporte lo reuse después, RNF-7), y U2–U6 como módulos dentro de la app.

B) **Todo en un solo módulo** sin separar el motor (más simple ahora, pero rompe RNF-7 y dificulta reutilizar el motor).

C) Sin preferencia — elige lo más adecuado para "local ahora, escalable después".

X) Otro (describe después de `[Answer]:`)

[Answer]: A (recomendación del asistente, aprobada por el usuario con "DALE")

### Pregunta Q2 — Orden de construcción de las unidades
¿Prefieres construir en un orden que entregue algo **usable punta a punta cuanto antes**, o construir **capa por capa** completa?

A) **Vertical / valor pronto**: U1 (motor) → U2 (fútbol) → un hilo mínimo de U3+U4+U5 para ver una sesión generada con diagrama y PDF end-to-end, y luego completar U6 y refinar. Ves resultados tangibles antes.

B) **Horizontal / por capas**: terminar U1 completo, luego U2 completo, luego U3, U4, U5, U6 en orden. Más ordenado, resultados visibles más tarde.

C) Sin preferencia — elige el orden que mejor respete dependencias y dé valor pronto.

X) Otro (describe después de `[Answer]:`)

[Answer]: A (recomendación del asistente, aprobada por el usuario con "DALE")

### Pregunta Q3 — Encaje del seguimiento individual (U6)
U6 (seguimiento individual) ya es parte de la v1. ¿Cómo lo tratamos como unidad?

A) **Unidad propia (U6)** separada, que se integra con la capa de fútbol (U2) y el orquestador. Más clara su evolución futura (fichas, histórico por jugador).

B) **Submódulo dentro de U2** (capa de fútbol), sin unidad propia. Menos piezas, pero mezcla responsabilidades.

C) Sin preferencia — elige lo más coherente con el diseño ya hecho.

X) Otro (describe después de `[Answer]:`)

[Answer]: A (recomendación del asistente, aprobada por el usuario con "DALE")

### Pregunta Q4 — Alcance mínimo de formatos para la primera versión construible
RF-7 pide 11/7/sala/ciegos. Para **empezar a construir** (no para la v1 final), ¿arrancamos con un subconjunto y añadimos el resto, o los cuatro de una vez?

A) **Arrancar con 1–2 formatos** (p. ej. fútbol 11 + fútbol para ciegos, que es tu caso real) para validar la cadena completa, y añadir fútbol 7 y sala después con bajo esfuerzo (la arquitectura ya lo soporta).

B) **Los cuatro formatos desde el primer código** de U2.

C) Sin preferencia — elige lo más eficiente para validar rápido sin retrabajo.

X) Otro (describe después de `[Answer]:`)

[Answer]: A (recomendación del asistente, aprobada por el usuario con "DALE")

### Pregunta Q5 — Modo de armado del macro (flujo de usuario)
Cuando el agente te ayuda a armar el macro, ¿qué flujo prefieres priorizar en la construcción?

A) **De una sola vez**: das todos los datos de temporada y genera el macro completo (meso incluidos).

B) **Por partes validando**: propone períodos → validas → mesociclos → validas → etc.

C) **Ambos disponibles** desde el inicio (el motor es el mismo; cambia solo cómo lo pide la interfaz).

X) Otro (describe después de `[Answer]:`)

[Answer]: C (recomendación del asistente, aprobada por el usuario con "DALE")

---

## Resumen de decisiones (aprobadas 2026-11-07)
- **Q1 = A**: Monolito modular; motor de periodización (U1) como paquete/librería interna reutilizable (RNF-7).
- **Q2 = A**: Orden vertical (valor pronto) — hilo end-to-end mínimo antes de completar todo.
- **Q3 = A**: U6 (seguimiento individual) como unidad propia.
- **Q4 = A**: Empezar con fútbol 11 + fútbol para ciegos; añadir 7 y sala después.
- **Q5 = C**: Ambos modos de armado del macro (de una vez y por partes validando) disponibles.

---

## Parte B — Artefactos a generar (tras aprobar respuestas)

- [x] `unit-of-work.md` — definición de unidades U1–U6, responsabilidades, alcance, y **estrategia de organización de código** (greenfield).
- [x] `unit-of-work-dependency.md` — matriz de dependencias entre unidades y orden de construcción.
- [x] `unit-of-work-story-map.md` — mapeo de requisitos funcionales (RF) a unidades (sustituye al mapa de historias, ya que se omitieron User Stories).
- [x] Validar límites de unidades y dependencias (sin ciclos).
- [x] Asegurar que todos los RF/RNF están asignados a una unidad.

---

## Parte C — Unidades candidatas (borrador, se formaliza con tus respuestas)

| Unidad | Nombre | Alcance | Depende de |
|--------|--------|---------|-----------|
| U1 | Motor de Periodización | Ciclos macro/meso/micro/sesión, fases, cargas, 5 modelos, determinista | — |
| U2 | Dominio Fútbol (+ adaptado) | Formatos, ejercicios, biblioteca, modelo de juego, adaptaciones | U1 |
| U3 | Diagramas y Gráficas | SVG de tareas/organización, gráficas de carga | U2 (y U1 para cargas) |
| U4 | Persistencia y Exportación | JSON en disco (historial+biblioteca), PDF bilingüe | U2, U3 |
| U5 | Interfaz Web + Chat + LLM | App local, formularios, chat, doble entrada, conector LLM, orquestación | U1–U4 |
| U6 | Seguimiento Individual | Roster, objetivos individuales, observaciones | U2 |
