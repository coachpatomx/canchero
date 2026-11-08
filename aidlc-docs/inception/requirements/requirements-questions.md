# Preguntas de Requisitos — Agente de Planificación de Entrenamientos de Fútbol

Responde cada pregunta escribiendo la letra elegida después de la etiqueta `[Answer]:`.
Si ninguna opción encaja, elige la última opción (**Other / Otro**) y describe tu preferencia después de `[Answer]:`.
Puedes dejar comentarios extra en cualquier respuesta. Avísame cuando termines (escribe "listo", "done" o similar).

---

## Pregunta 1 — Interfaz del agente
¿Cómo quieres interactuar con el agente en tu ordenador?

A) Chat conversacional (le escribo en lenguaje natural y me responde)

B) Línea de comandos / CLI (comandos y parámetros)

C) App web local (abro una página en el navegador con formularios y botones)

D) App de escritorio con ventana propia

X) Otro (describe después de `[Answer]:`)

[Answer]:  C (app web local) + nota: incluye chat conversacional como componente

---

## Pregunta 2 — Tipo de "gráficas" en la sesión
Cuando dices que la sesión incluya "las gráficas de lo que se vaya a practicar", ¿a qué te refieres?

A) Diagramas tácticos de cancha (pizarra del entrenador: jugadores, conos, balones, flechas de movimiento)

B) Gráficas de datos de carga (volumen, intensidad, distribución por semana/microciclo)

C) Ambas: diagramas de cancha para los ejercicios y gráficas de carga para la periodización

D) Solo texto descriptivo por ahora, las gráficas las agregamos más adelante

X) Otro (describe después de `[Answer]:`)

[Answer]: C (ambas), con diagramas de cancha prioritarios

---

## Pregunta 3 — Flujo de entrada de datos
¿Cómo prefieres darle la información al agente para que genere la planificación?

A) El agente me hace preguntas paso a paso (tipo entrevista) y yo respondo

B) Yo le paso todos los parámetros de una vez (duración, objetivos, sesiones por semana, categoría, etc.)

C) Una mezcla: un formulario/plantilla inicial y luego ajustes conversacionales

X) Otro (describe después de `[Answer]:`)

[Answer]: X, que se pueda utilizar ambos agente pregunta y pasarle los parametros

---

## Pregunta 4 — Conocimiento de periodización
¿De dónde debe salir la metodología de periodización (cómo repartir cargas, fases, principios)?

A) Que el agente traiga modelos de periodización reconocidos (ej. periodización por bloques, ATR, modelo tradicional) y me deje elegir

B) Que yo defina mis propios principios/metodología y el agente solo los organice y aplique

C) Una combinación: parte de modelos reconocidos como base, pero yo puedo sobrescribir reglas

X) Otro (describe después de `[Answer]:`)

[Answer]: C: Que se adapte a la metodología de quien lo usa + precargarle las metodologías más usadas

---

## Pregunta 5 — Formato de salida
¿Cómo quieres recibir la planificación final (macrociclo, mesociclo, sesiones)?

A) PDF imprimible (listo para llevar a la cancha)

B) Documentos Markdown (editables, legibles en cualquier editor)

C) HTML (se ve bien en pantalla, se puede imprimir)

D) Varios formatos a elegir (ej. Markdown + exportar a PDF)

X) Otro (describe después de `[Answer]:`)

[Answer]:   D (editable + export a PDF)

---

## Pregunta 6 — Alcance de los tipos de fútbol en la primera versión
Dijiste que sea agnóstico (fútbol 11, 7, sala, para ciegos, etc.). Para la **primera versión**, ¿cómo lo abordamos?

A) Soportar todos los formatos desde el inicio, con sus reglas (nº jugadores, dimensiones, duración)

B) Empezar con uno o dos formatos y diseñarlo para agregar los demás fácilmente

C) Hacerlo totalmente genérico/configurable: tú defines el formato y sus parámetros

X) Otro (describe después de `[Answer]:`)

[Answer]: A

---

## Pregunta 7 — Especificidades del fútbol para ciegos
¿Debe el agente incorporar adaptaciones propias del fútbol para ciegos (balón sonoro, guías/llamadores, orientación por sonido, zonas) como conocimiento integrado?

A) Sí, que tenga conocimiento integrado de adaptaciones para fútbol para ciegos

B) No por ahora, tratarlo como un formato más y yo aporto las adaptaciones manualmente

C) Dejarlo preparado como módulo opcional para activarlo cuando elija ese formato

X) Otro (describe después de `[Answer]:`)

[Answer]: X se integraran las adaptaciones de las modalidades de futbol adaptado mas jugadas, en un modulo a parte o simplemente que se active cuando se le diga 

---

## Pregunta 8 — Persistencia / guardado
¿El agente debe guardar y reutilizar planificaciones y ejercicios?

A) Sí, guardar un historial de planificaciones y una biblioteca de ejercicios reutilizables

B) Solo generar cada planificación en el momento, sin guardar nada

C) Guardar solo la planificación actual (archivos en el disco), sin biblioteca compartida

X) Otro (describe después de `[Answer]:`)

[Answer]: 
a
---

## Pregunta 9 — Preferencia de tecnología (lenguaje)
¿Tienes preferencia de lenguaje/tecnología para construirlo? (Afecta cómo lo desarrollamos.)

A) Python (muy usado para IA/datos, buen ecosistema de PDFs y gráficos)

B) JavaScript/TypeScript (Node) — útil si luego quieres llevarlo a web

C) Sin preferencia, elige tú lo más adecuado para un agente local escalable

X) Otro (describe después de `[Answer]:`)

[Answer]: C

---

## Pregunta 10 — Uso de IA/LLM dentro del agente
¿El agente debe usar un modelo de lenguaje (LLM) para generar contenidos (ej. redactar ejercicios, variar sesiones), o debe ser lógica determinista basada en reglas y plantillas?

A) Usar un LLM para generar/variar contenido de forma creativa

B) Lógica determinista con reglas y plantillas (resultados predecibles, sin depender de internet)

C) Híbrido: reglas para la estructura y periodización, LLM opcional para enriquecer ejercicios

X) Otro (describe después de `[Answer]:`)

[Answer]: C

---

## Pregunta: Extensión de Seguridad
¿Se deben aplicar las reglas de la extensión de **Seguridad** a este proyecto?

A) Sí — aplicar todas las reglas de SEGURIDAD como restricciones bloqueantes (recomendado para aplicaciones de nivel productivo)

B) No — omitir las reglas de SEGURIDAD (adecuado para pruebas de concepto, prototipos y proyectos experimentales)

X) Otro (describe después de `[Answer]:`)

[Answer]: 
B
---

## Pregunta: Extensión de Resiliencia
¿Se debe aplicar la línea base de **Resiliencia** a este proyecto?

**Qué es.** Aplica buenas prácticas de diseño (orientadas, no certificadoras) para sistemas resilientes, basadas en el AWS Well-Architected Framework (Pilar de Fiabilidad): tolerancia a fallos, alta disponibilidad, observabilidad y recuperación. Es un punto de partida, no una garantía de producción.

A) Sí — aplicar la línea base de resiliencia como guía de diseño (recomendado para cargas críticas de negocio)

B) No — omitir la línea base de resiliencia (adecuado para PoCs, prototipos y proyectos experimentales donde prima iterar rápido)

X) Otro (describe después de `[Answer]:`)

[Answer]: B  (ajustado por acuerdo: "local primero", se reevalúa al escalar a web/multiusuario — decisión delegada al asistente)

---

## Pregunta: Extensión de Pruebas Basadas en Propiedades (PBT)
¿Se deben aplicar las reglas de **Pruebas Basadas en Propiedades**?

A) Sí — aplicar todas las reglas de PBT como restricciones bloqueantes (recomendado para proyectos con lógica de negocio, transformaciones de datos, serialización o componentes con estado)

B) Parcial — aplicar PBT solo a funciones puras y round-trips de serialización (adecuado para proyectos con complejidad algorítmica limitada)

C) No — omitir todas las reglas de PBT (adecuado para apps CRUD simples, proyectos solo de UI o capas delgadas de integración)

X) Otro (describe después de `[Answer]:`)

[Answer]: B
