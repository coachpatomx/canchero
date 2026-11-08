# Referencia de Formato de Salida de Sesión

**Origen**: Plantilla real de sesión aportada por el usuario — **América U19 Femenil**, sesión de Pretemporada 1 (Torneo AP24), 18 dic 2024.
**Estatus**: Ejemplo de referencia. **Mejorable** (indicación explícita del usuario). No se clona literalmente; se usa como guía de qué datos y qué estructura debe producir el agente al generar una sesión.

> El agente debe poder generar una sesión *en el espíritu de esta plantilla* (misma información, misma lógica metodológica), con libertad para mejorar formato, claridad de diagramas y coherencia entre tareas.

---

## 1. Por qué esta plantilla es valiosa

Es el **output objetivo** del nivel más bajo de la cadena (la sesión impresa que se lleva a la cancha). Confirma, con un documento real de uso, toda la metodología de los manuales FMF cargados como base de conocimiento:

- La cadena **Torneo → Semana → Mesociclo → Microciclo → Sesión** (encabezado) ↔ RF-1 y manuales C3/C4/C5.
- La **estructura de tareas** analítico → específico → juego → global ↔ estrategias didácticas (C6) y fases de sesión (C5).
- **Diagramas de cancha por tarea** + diagrama de organización general ↔ RF-5 y momentos/zonas (C1), a generar en **SVG** (decisión D3).
- Los **4 aspectos** (técnico/táctico/físico/psicológico) ↔ estructuras del futbolista (C2/C4).

---

## 2. Campos del encabezado (metadatos de la sesión)

| Campo | Ejemplo en la plantilla | Fuente en el modelo de datos |
|-------|-------------------------|------------------------------|
| Equipo / categoría | América U19 Fem | Config del equipo |
| Fecha | Wed, Dec 18 2024 | Sesión |
| Hora / Cancha | 2:00 PM / cancha 4 | Sesión |
| Semana | Pretemporada 1 | Microciclo/periodo |
| Torneo | AP24 | Macrociclo |
| Mesociclo / Microciclo / Sesión (nº) | 1 / 1 / 1 | Cadena macro→meso→micro→sesión |
| Nº jugadoras | 20 | Roster |
| Roster por demarcación | Porteras, Centrales, Laterales, Medio centro, Interiores/Extremas, Delanteras | Dominio fútbol + U6 seguimiento individual |
| Carga | Media baja | Microciclo (tipo/%carga, C3/C4) |
| Objetivo principal | Vuelta al trabajo | Objetivo de sesión (C5) |
| Carácter | Ofensivo | Foco de la sesión |
| Tiempo activo aprox. | 71 min | Suma de duraciones de tareas |

**Nota**: el roster por demarcación en el encabezado es la bisagra con **U6 (seguimiento individual)**: las jugadoras ya están tipadas por posición, base para observaciones individuales.

---

## 3. Estructura de tareas (cuerpo de la sesión)

Cada tarea trae: **tipo**, **nombre/objetivo**, **duración**, **dimensiones**, **descripción** y **representación gráfica** (diagrama de cancha).

| Bloque en la plantilla | Ejemplo | Mapea a fase de sesión (C5) / estrategia (C6) |
|------------------------|---------|-----------------------------------------------|
| Analítico — Técnico de pases (T1) | 10 min, 10x10 | Subfase activación / tarea analítica |
| Específico — Protección del balón | 30 min, 10x10+área, 3 variantes 2c1 | Subfase principal / juego específico |
| Juego/Porteras — 8c5 protección | 15 min, doble área | Fase principal / juego condicionado |
| Global — 8c8+4 | 16 min, media sin bandas | Fase principal / juego real condicionado |
| Organización (diagrama grande) | Cancha completa, zona baja metabólico | Vista global de la sesión |

Tabla de **Dimensiones por tarea** (T1–T5) como resumen: 10x10 / 10x10 fuera del área / 10x10 fuera del área / media cancha con límites en las bandas.

---

## 4. Cuadros de cierre — los 4 aspectos (estructuras del futbolista)

Alimentan directamente el modelo de juego y el etiquetado de contenidos:

- **Técnicos**: control orientado, pase, juego de cara, protección de balón.
- **Tácticos**: espejo, posicionamiento, toma de espacios.
- **Físicos**: resistencia, arranque, cambio de ritmo, fuerza.
- **Psicológicos**: vuelta al trabajo, confianza, seguridad.

---

## 5. Implicaciones para el diseño

1. **Modelo de datos de Sesión** debe contener: metadatos (encabezado), lista ordenada de tareas (cada una con tipo, duración, dimensiones, descripción, diagrama), roster por demarcación, y los 4 bloques de aspectos.
2. **DiagramRenderer (U3)** debe producir dos clases de diagrama: (a) diagrama por tarea y (b) diagrama de organización general de cancha. SVG (D3).
3. **Exporter (U4)** debe poder volcar esta estructura a un PDF imprimible en una maqueta tipo esta hoja (RF-6), mejorable respecto al original.
4. **FootballDomain (U2)** aporta demarcaciones, dimensiones por formato y los catálogos de aspectos técnico/táctico/físico/psicológico.
5. **PlanningService** ensambla la sesión encadenando desde el microciclo (carga, objetivo) y pidiendo tareas coherentes con la fase (relación vertical, C5).
6. Mejoras candidatas sobre el original: numeración/ű coherencia vertical explícita entre tareas, leyenda de símbolos en los diagramas, trazabilidad visible del objetivo de meso/macro en la hoja.

---

## 6. Plantilla mejorada (objetivo real a soportar)

El usuario indicó que existe **otra plantilla más completa** que integra, además de lo anterior:

- **Objetivos individuales por jugador/a** (no solo roster: metas por deportista) → conecta con **U6 Seguimiento Individual** (v1, opción A). Metodología FMF Manual 1: Potenciar / Mejorar / Eliminar.
- **Cargas** (por sesión y por tarea; coherentes con el tipo de microciclo, C3/C4).
- **Materiales** (inventario por tarea: conos, balones, petos, mini-porterías, balón sonoro en fútbol para ciegos, etc.).
- **Volumen** (totales de la sesión: tiempo, series, distancias si aplica) y su relación con intensidad.
- **Etc.** (otros campos de control que el usuario pueda requerir).

**Implicación**: el modelo de datos de **Sesión** y de **Tarea** debe contemplar desde el diseño:
- `Tarea`: materiales[], carga, volumen, intensidad, dimensiones, duración, diagrama, aspectos (téc/tác/fís/psi).
- `Sesión`: objetivos individuales por jugador/a (enlazados a U6), totales de carga/volumen, lista de materiales agregada, idioma (es/en, D6).
- `Jugador/a` (U6): demarcación, objetivos Potenciar/Mejorar/Eliminar, observaciones ligadas a sesiones/microciclos.

Esta plantilla mejorada es el **objetivo de salida real**; la hoja del América U19 Fem es el punto de partida mínimo.

---

## Nota sobre el archivo de imagen

La fotografía original de la plantilla (América U19 Fem) fue aportada por el usuario en el chat como referencia visual. Se conserva aquí su análisis estructurado. Si se desea archivar el archivo de imagen junto a esta documentación, guardarlo como `session-output-reference.jpg` en esta misma carpeta.
