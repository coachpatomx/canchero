# Plan de Application Design — Agente de Fútbol

**Etapa**: INCEPCIÓN → Application Design
**Objetivo**: Identificar componentes, sus responsabilidades e interfaces, y la capa de servicios que los orquesta. (La lógica de negocio detallada vendrá después, en Functional Design por unidad.)

---

## Parte A — Preguntas de Diseño

Antes de generar los artefactos necesito aclarar algunas decisiones de diseño. Responde con la letra después de `[Answer]:`. Si ninguna encaja, usa **X) Otro** y describe. Avísame cuando termines.

### Pregunta D1 — Estilo de arquitectura general
¿Cómo prefieres organizar el agente internamente?

A) **Por capas limpias** (núcleo de dominio aislado + adaptadores para interfaz, LLM y disco) — máxima separación, ideal para escalar y testear

B) **Modular simple** (paquetes separados por módulo U1–U5, sin tanta ceremonia de puertos/adaptadores)

C) Sin preferencia — elige lo más adecuado para un agente local escalable

X) Otro (describe después de `[Answer]:`)

[Answer]: C

### Pregunta D2 — Formato de almacenamiento en disco
¿En qué formato se guardan las planificaciones y la biblioteca de ejercicios? (RNF-6: fácil de respaldar copiando una carpeta.)

A) **Archivos JSON** (legibles, fáciles de versionar, sin dependencias)

B) **Base de datos local embebida** (ej. SQLite — consultas más potentes, un solo archivo)

C) Sin preferencia — elige lo más adecuado (puede empezar en JSON y migrar a SQLite al escalar)

X) Otro (describe después de `[Answer]:`)

[Answer]: C

### Pregunta D3 — Representación de los diagramas de cancha
¿Cómo se representan internamente los diagramas de los ejercicios? (La v1 usa diagramas esquemáticos/plantillas, no un editor profesional.)

A) **SVG generado** (vectorial, se ve nítido en pantalla y PDF, editable por coordenadas)

B) **Imagen rasterizada** (PNG) generada desde una librería de dibujo

C) Sin preferencia — elige lo más adecuado para pantalla + PDF

X) Otro (describe después de `[Answer]:`)

[Answer]: C

### Pregunta D4 — Alcance de los modelos de periodización precargados (RF-4)
¿Qué modelos de periodización quieres que vengan precargados en el motor (U1) para la v1?

A) **Solo uno** bien hecho para empezar (ej. modelo tradicional / lineal) y agregar más después

B) **Dos o tres** reconocidos (ej. tradicional + periodización por bloques + ATR)

C) Que elija el asistente un set razonable para la v1

X) Otro (describe después de `[Answer]:`)

[Answer]: B Y BUSCATE OTROS DOS , VALIDA LO ULTIMO EN FUTBOL

### Pregunta D5 — Proveedor del LLM opcional (RF-10)
¿Con qué proveedor de LLM debe integrarse el conector opcional? (Recuerda: es opcional y el agente funciona offline sin él.)

A) **API en la nube** (ej. OpenAI / Anthropic) — mejor calidad, requiere API key y conexión

B) **Modelo local** (ej. Ollama corriendo en tu máquina) — sin costo recurrente, sin salir a internet

C) **Diseñar el conector genérico** para poder [text](.)enchufar cualquiera de los dos después

X) Otro (describe después de `[Answer]:`)

[Answer]: C

### Pregunta D6 — Idioma del contenido generado
¿En qué idioma debe generar el agente el contenido (sesiones, ejercicios, PDF)?

A) **Español** únicamente

B) **Español e inglés** (seleccionable)

C) Otro / varios (describe)

X) Otro (describe después de `[Answer]:`)

[Answer]: B

---

## Parte B — Artefactos a Generar (tras aprobar las respuestas)

- [x] `components.md` — definición de componentes y responsabilidades de alto nivel
- [x] `component-methods.md` — firmas de métodos (entradas/salidas), sin lógica detallada aún
- [x] `services.md` — servicios de orquestación y sus interacciones
- [x] `component-dependency.md` — matriz de dependencias, patrones de comunicación y flujo de datos
- [x] `application-design.md` — documento consolidado
- [x] Validación de completitud y consistencia del diseño
- [x] `session-output-reference.md` — referencia del formato de salida de sesión (plantilla mejorada)

**Decisiones finales**: D1=capas ligeras, D2=JSON→SQLite, D3=SVG, D4=5 modelos, D5=conector genérico, D6=bilingüe, U6=v1 (opción A).

---

## Parte C — Componentes Candidatos (borrador, se refina con tus respuestas)

Mapa preliminar alineado a las unidades U1–U5 del plan de ejecución:

- **PeriodizationEngine** (U1) — núcleo compartido: ciclos, fases, cargas, encadenamiento. Sin nada de fútbol.
- **FootballDomain** (U2) — formatos (11/7/sala/ciegos), modelo de ejercicio, biblioteca, módulo de adaptaciones de fútbol adaptado (activable).
- **DiagramRenderer** (U3) — diagramas de cancha + gráficas de carga.
- **PlanRepository / Exporter** (U4) — persistencia en disco (historial + biblioteca) y exportación a PDF.
- **PlanningService** (orquestador) — coordina el flujo macro→meso→sesión usando el motor + dominio + diagramas + persistencia.
- **WebUI + ChatInterface** (U5) — app web local, formularios, chat, doble modo de entrada.
- **LLMConnector** (U5) — enriquecimiento opcional de contenido, con gestión de API key.
