# Requisitos — Agente de Planificación de Entrenamientos de Fútbol

**Proyecto**: Agente planificador de entrenamientos (macrociclo → mesociclo → sesión)
**Tipo**: Greenfield (proyecto nuevo)
**Fecha**: 2026-11-07
**Profundidad de análisis**: Estándar

---

## 1. Visión del Producto

Un **agente** que ayuda a entrenadores de fútbol a planificar entrenamientos de forma **encadenada y coherente**: parte del **macrociclo** (objetivo de temporada), deriva de él los **mesociclos**, y de cada mesociclo deriva las **sesiones** con sus **diagramas de lo que se va a practicar**.

El diferenciador frente a lo que existe en el mercado es el **comportamiento agéntico de encadenar toda la cadena de planificación manteniendo coherencia de objetivos y cargas** (no solo generar sesiones sueltas, que es lo que hacen las herramientas actuales), más la cobertura de **fútbol adaptado**.

**Arranque**: agente **local** (vive en el ordenador del usuario). **Diseñado para escalar** a web/multiusuario después, sin rehacer el núcleo.

**Estrategia multideporte (decisión del usuario)**: **un agente por deporte**. Este proyecto construye el **Agente de Fútbol** (todas las modalidades de fútbol se tratan como configuración dentro de este agente). Otros deportes (p. ej. natación) serán **agentes independientes en el futuro**, fuera del alcance de este proyecto. El **motor de periodización** (macro→meso→sesión, fases, cargas) se construye como **pieza reutilizable compartida** (librería/paquete común) para que futuros agentes de otros deportes lo reutilicen sin duplicarlo ni mantenerlo por separado.

---

## 2. Análisis de Intención

- **Qué**: Planificador jerárquico de entrenamientos de fútbol con generación de diagramas.
- **Por qué**: La planificación de sesiones es lo más laborioso para el entrenador; encadenar macro→meso→sesión de forma coherente ahorra tiempo y mantiene consistencia metodológica.
- **Para quién**: Entrenadores de fútbol de cualquier modalidad (11, 7, sala, fútbol para ciegos y otras modalidades adaptadas). El usuario principal es entrenador de fútbol para ciegos, pero el producto es agnóstico al tipo de fútbol.

---

## 3. Contexto de Mercado (resumen de investigación)

- Existen herramientas con IA que generan **sesiones sueltas** con diagramas (ej. Gambeta, PitchLabs, CoachFlow, SessionPlan) y editores de pizarra táctica (DrawTactics).
- Existe un producto más agéntico, Matchday Lab ("copiloto consciente de la temporada"), que mantiene memoria entre sesiones/partidos — pero trabaja a nivel micro/semana y es solo fútbol convencional.
- **Hueco identificado**: nadie encadena **macrociclo → mesociclo → sesión** de arriba hacia abajo, ni cubre fútbol adaptado.
- **Validación técnica**: el competidor más avanzado (Matchday Lab) usa planificación **determinista** ("mismas entradas, mismo plan") y reserva la IA para enriquecer/explicar — alineado con el enfoque híbrido elegido (RF-10).
- **Realidad sobre diagramas**: ni los competidores con recursos ofrecen edición libre de diagramas fácilmente (Gambeta los deja "solo vista"; Matchday Lab usa biblioteca pre-hecha). Se asume para la v1 diagramas esquemáticos simples / basados en plantillas, no un editor de pizarra profesional.

---

## 4. Requisitos Funcionales

### RF-1 — Planificación jerárquica encadenada
- El agente genera un **macrociclo** a partir de parámetros de temporada (duración, objetivos, competición, categoría).
- Deriva **mesociclos** coherentes con el macrociclo (fases, distribución de cargas).
- Deriva **sesiones** (y microciclos semanales) coherentes con su mesociclo.
- Cada nivel conserva el "hilo": una sesión sabe a qué objetivo de mesociclo y macrociclo responde.

### RF-2 — Interfaz: app web local + chat
- La interfaz principal es una **app web que corre localmente** (se abre en el navegador: `localhost`).
- Incluye **formularios/botones** para pasar parámetros y navegar/editar la planificación.
- Incluye un **chat conversacional** como componente dentro de la app para pedir ajustes en lenguaje natural.

### RF-3 — Doble modo de entrada de datos (P3)
- **Modo parámetros**: el usuario rellena un formulario/plantilla con todos los datos de una vez y genera.
- **Modo entrevista**: el agente hace preguntas paso a paso y el usuario responde.
- Ambos modos deben estar disponibles y poder combinarse (ej. formulario inicial + ajustes por chat).

### RF-4 — Conocimiento de periodización configurable (P4)
- El agente trae **modelos de periodización reconocidos precargados** (ej. periodización por bloques, modelo ATR, modelo tradicional) como base.
- El usuario puede **sobrescribir reglas o definir su propia metodología**; el agente la organiza y la aplica.

### RF-5 — Diagramas y gráficas (P2)
- **Prioritario**: diagramas tácticos de cancha para los ejercicios de cada sesión (jugadores, conos, balones, zonas, flechas de movimiento). Para la v1 pueden ser **esquemáticos / basados en plantillas**.
- **Secundario**: gráficas de carga (volumen, intensidad, distribución por microciclo/mesociclo) para presentar la periodización.

### RF-6 — Salida editable + exportación a PDF (P5)
- La planificación se mantiene en un **formato editable** dentro del agente (datos de macro/meso/sesión).
- El usuario **edita dentro del propio agente** (formularios o chat) y el agente **regenera** la salida.
- Se puede **exportar a PDF imprimible** para llevar a la cancha. El PDF es la "foto" final, no el lugar de edición.
- **Dos vías de PDF (decisión del usuario 2026-11-07), ambas producen PDF**: (1) **HTML imprimible** siempre disponible, sin dependencias — "Imprimir → Guardar como PDF" desde el navegador; (2) **PDF nativo opcional** con un clic si está instalado WeasyPrint. Ambas reutilizan la misma maqueta HTML. Si WeasyPrint no está, el agente usa la vía (1) sin romperse (RNF-2 offline).

### RF-7 — Soporte multi-formato de fútbol desde el inicio (P6)
- Soportar desde la v1: **fútbol 11, fútbol 7, fútbol sala y fútbol para ciegos**, con sus reglas propias (nº de jugadores, dimensiones de cancha, duración, etc.).
- Arquitectura preparada para **agregar más formatos** con bajo esfuerzo.

### RF-8 — Módulo de adaptaciones de fútbol adaptado (P7)
- Integrar las adaptaciones de las **modalidades de fútbol adaptado más practicadas**.
- **Modalidades adaptadas con contenido real en la v1** (decisión del usuario, 2026-11-07): **fútbol 7 PC** (parálisis cerebral), **fútbol para personas con síndrome de Down / discapacidad intelectual**, **fútbol 5 para ciegos** (discapacidad visual), y **fútbol para amputados**. Cubren perfiles distintos a propósito (ciegos/amputados → adaptación de material y mecánica; PC/Down → adaptación de reglas y clasificación funcional), validando la flexibilidad del submódulo.
- **Catálogo extensible**: otras modalidades (powerchair, sordos, etc.) quedan como estructura lista para añadir con bajo esfuerzo (modalidad = datos de configuración).
- **Advertencia de precisión metodológica**: las reglas de detalle de PC, Down y amputados se modelan a partir de fuentes reconocidas pero se marcan como **editables y pendientes de validación por el usuario** (experto en ciegos). El agente no afirma reglas finas con precisión no verificada; el usuario corrige vía datos.
- Debe vivir en un **módulo aparte / activable**: se aplica cuando el usuario selecciona ese formato o lo solicita.

### RF-9 — Persistencia: historial + biblioteca (P8)
- Guardar un **historial de planificaciones** (reabrir, continuar, versionar planes anteriores).
- Mantener una **biblioteca de ejercicios reutilizables** que las sesiones puedan referenciar.

### RF-11 — Petición de sesión suelta alineada al macro (entrada por lenguaje natural)
- El usuario puede pedir una sesión concreta en lenguaje natural indicando **contenido** y **condicionantes** (ej. "una sesión de conducción en espacio reducido para esta semana"). El agente genera **descripción de ejercicio(s) + diagrama**.
- **Alineación al macro**: si existe un macrociclo vigente que cubre esa fecha, la sesión se **encaja** en el microciclo/fase/carga/objetivo correspondientes y hereda la trazabilidad a meso/macro (coherencia, no sesión suelta aislada — ver RF-1, RNF-5).
- **Sin macro inventado**: el agente **no fabrica un macrociclo sin fundamento**. Si no hay macro que cubra la fecha, usa el **modo entrevista** (RF-3) para pedir los datos mínimos de temporada y construir un macro **con sentido**, del cual deriva la metodología hacia abajo hasta la sesión pedida.
- **Degradación explícita**: si el usuario rechaza dar los datos de temporada, el agente puede generar la sesión suelta pero la **marca como "sin macro / alineación parcial"**.

### RF-10 — Motor híbrido: reglas deterministas + LLM opcional (P10)
- La **estructura y la periodización** (encadenar macro→meso→sesión, repartir cargas, fases) se resuelven con **lógica determinista** (resultados predecibles, mismas entradas → mismo plan). Este es el comportamiento agéntico central.
- El **contenido de los ejercicios** (redacción, variantes, progresiones) puede **enriquecerse con un LLM opcional**.
- El agente debe **funcionar sin conexión** usando solo la lógica determinista; el LLM es un complemento activable.
- **Conectores implementados (2026-11-07)**: OpenAI, Anthropic (Claude) y Ollama (local/gratis), todos enchufables vía `AGENTE_LLM_PROVIDER`. Modo `chain` = cadena de respaldo configurable (p. ej. Ollama → OpenAI → Null): usa el primero disponible y nunca deja sin respuesta (si ninguno está, sigue determinista). Clave de API siempre por variable de entorno (RNF-3). `enrich_session` solo reescribe la redacción del objetivo de cada tarea; nunca toca estructura, cargas ni diagramas.

---

## 5. Requisitos No Funcionales

### RNF-1 — Despliegue local primero, escalable
- Corre en el ordenador del usuario, un solo usuario, sin servidor.
- Núcleo (motor de planificación) **desacoplado de la interfaz** para permitir escalar a web/multiusuario sin reescribir la lógica.

### RNF-7 — Motor de periodización reutilizable (un agente por deporte)
- Estrategia: **un agente por deporte**. Este proyecto = **Agente de Fútbol**.
- El **motor de periodización** (ciclos macro/meso/micro/sesión, fases, distribución de cargas) se implementa como **librería/paquete compartido**, independiente de todo lo específico del fútbol.
- La **capa de dominio de fútbol** (formatos, ejercicios, diagramas de cancha, adaptaciones) se construye sobre ese motor.
- Objetivo: que un futuro agente de otro deporte (p. ej. natación) **reutilice el motor** sin duplicarlo ni mantenerlo dos veces.

### RNF-2 — Operación offline
- La funcionalidad esencial (generar y editar planificaciones con reglas/plantillas) debe operar **sin internet**. El LLM es la única parte que requiere conexión y es opcional.

### RNF-3 — Gestión de secretos
- Si se usa un LLM vía API, la **clave/API key** se maneja por configuración/variable de entorno, **nunca** escrita en el código. (Buena práctica aplicada aun con la extensión de Seguridad desactivada.)

### RNF-4 — Tecnología a criterio del asistente (P9)
- Sin preferencia de lenguaje por parte del usuario; se elegirá la tecnología más adecuada para un agente local escalable en la etapa de diseño/NFR. Candidato principal: Python (ecosistema fuerte para datos, PDF y gráficos; buena integración con LLMs), a confirmar en Construcción.

### RNF-5 — Coherencia y trazabilidad de la planificación
- Debe ser verificable que cada sesión es consistente con su mesociclo y macrociclo (objetivos y cargas encajan). Candidato a verificación mediante Pruebas Basadas en Propiedades (ver Extensiones).

### RNF-6 — Portabilidad de datos
- Las planificaciones y la biblioteca se guardan como **archivos en disco** fáciles de respaldar/copiar (un respaldo = copiar una carpeta). Sustituye necesidades de backup complejas en la fase local.

---

## 6. Configuración de Extensiones AI-DLC

| Extensión | Estado | Justificación |
|-----------|--------|---------------|
| **Seguridad** | Desactivada | Agente local de un solo usuario, no expuesto a internet entrante. Reevaluar al escalar a web/multiusuario. |
| **Resiliencia** | Desactivada | Asume despliegue en nube de producción (multi-zona, failover, RTO/RPO) — no aplica a un agente local. Reevaluar al escalar. |
| **Pruebas Basadas en Propiedades (PBT)** | Activada (Parcial) | Aplicar PBT a funciones puras y round-trips de serialización. Encaja con el motor determinista de periodización (RF-10, RNF-5) y la persistencia (RF-9). |

---

## 7. Fuera de Alcance (v1)

- **Otros deportes (natación, etc.)**: serán agentes independientes en el futuro. Este proyecto es solo el Agente de Fútbol. (El motor de periodización se diseña reutilizable para facilitarlos — RNF-7.)
- Despliegue web multiusuario / hosting en la nube (se contempla como evolución futura).
- Cuentas de usuario, login y separación de datos entre usuarios.
- Editor profesional de pizarra táctica con animaciones (la v1 usa diagramas esquemáticos / plantillas).
- Análisis de video o scouting de partidos.

---

## 8. Supuestos

- El usuario ejecuta el agente en su propio ordenador y puede instalar dependencias.
- El uso de LLM (si se activa) implica una clave de API de un proveedor y un costo por uso bajo (centavos a pocos dólares/mes para uso individual), o alternativamente un modelo local sin costo recurrente.
- Los diagramas de la v1 priorizan claridad funcional sobre fidelidad visual profesional.

---

## 9. Criterios de Éxito (v1)

1. A partir de parámetros de temporada, el agente genera un macrociclo y, encadenados, mesociclos y sesiones coherentes entre sí.
2. Cada sesión incluye al menos un diagrama esquemático de los ejercicios y referencia su objetivo de mesociclo/macrociclo.
3. El usuario puede editar la planificación (por formulario o chat) y exportar un PDF imprimible.
4. Soporta fútbol 11, 7, sala y para ciegos, con las adaptaciones de fútbol adaptado activables.
5. Funciona sin conexión para la generación y edición basada en reglas; el LLM es un complemento opcional.
6. Historial de planificaciones y biblioteca de ejercicios persistidos en disco.
