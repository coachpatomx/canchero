# Componentes — Agente de Fútbol

**Etapa**: INCEPCIÓN → Application Design
**Arquitectura (D1)**: Modular por **capas ligeras**. Un **núcleo de dominio** aislado (motor de periodización + dominio fútbol) rodeado de **adaptadores** (interfaz web/chat, conector LLM, persistencia en disco). Sin ceremonia pesada de puertos/adaptadores; separación suficiente para escalar a web (RNF-1) y para que el motor sea reutilizable por otros deportes (RNF-7).

```
┌───────────────────────────────────────────────────────────────┐
│  ADAPTADORES (borde)                                           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐  │
│  │ WebUI +       │  │ LLMConnector  │  │ PlanRepository /  │  │
│  │ ChatInterface │  │ (opcional)    │  │ Exporter (disco)  │  │
│  └───────┬───────┘  └───────┬───────┘  └─────────┬─────────┘  │
└──────────┼──────────────────┼────────────────────┼────────────┘
           │                  │                    │
┌──────────▼──────────────────▼────────────────────▼────────────┐
│  ORQUESTACIÓN                                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ PlanningService  (coordina la cadena macro→meso→sesión)   │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────┬───────────────────────┬────────────────┬───────────┘
           │                       │                │
┌──────────▼───────────┐ ┌─────────▼────────┐ ┌─────▼──────────┐
│ NÚCLEO COMPARTIDO    │ │ DOMINIO FÚTBOL   │ │ DiagramRenderer│
│ PeriodizationEngine  │ │ FootballDomain   │ │ (SVG)          │
│ (U1, sin fútbol)     │ │ (U2)             │ │ (U3)           │
└──────────────────────┘ └────────┬─────────┘ └────────────────┘
                                   │
                          ┌────────▼─────────┐
                          │ PlayerTracking   │
                          │ (U6, individual) │
                          └──────────────────┘
```

---

## Núcleo compartido

### C1 — PeriodizationEngine (U1)
**Responsabilidad**: Lógica determinista de periodización, **sin nada específico de fútbol** (RNF-7). Genera y encadena ciclos (macro → meso → micro → sesión), reparte cargas y aplica un **modelo de periodización** seleccionable.
- Modelos precargados (D4): Tradicional/lineal, Por bloques, ATR, Periodización Táctica, Entrenamiento Estructurado.
- Permite **sobrescribir reglas / definir metodología propia** (RF-4).
- Determinista: mismas entradas → mismo plan (RF-10, RNF-5). Candidato a PBT (funciones puras).
- Expone estructura de ciclos y curva de cargas (volumen/intensidad por micro/meso).
**No hace**: no conoce demarcaciones, ni diagramas, ni formatos de fútbol, ni disco, ni UI.

---

## Dominio fútbol

### C2 — FootballDomain (U2)
**Responsabilidad**: Todo lo específico de fútbol que vive **sobre** el motor.
- **Formatos** (RF-7): fútbol 11, 7, sala, para ciegos — como configuración (nº jugadores, dimensiones de cancha, duración, reglas).
- **Modelo de ejercicio/tarea**: tipo (analítico/específico/juego/global), duración, dimensiones, descripción, materiales, carga, volumen, intensidad, aspectos (técnico/táctico/físico/psicológico), referencia a diagrama.
- **Biblioteca de ejercicios** reutilizable (RF-9).
- **Vocabulario de modelo de juego** (de los manuales FMF/C1-C2): dinámicas, fases, momentos, fundamentos (FID/FGL/FCU/FCL), principios/subprincipios.
- **Catálogos de contenido bilingüe** (D6): claves de traducción es/en para nombres de tareas, aspectos, demarcaciones.

### C3 — AdaptedFootballModule (U2, submódulo activable)
**Responsabilidad**: Adaptaciones de **fútbol adaptado** (RF-8), activable al seleccionar el formato o solicitarlo.
- Fútbol para ciegos: balón sonoro, guías/llamadores, orientación por sonido, zonas, materiales específicos.
- Diseñado para añadir otras modalidades adaptadas con bajo esfuerzo.

### C4 — PlayerTracking (U6, seguimiento individual) — **v1**
**Responsabilidad**: Ficha y seguimiento por jugador/a, integrado a la planificación (decisión: Opción A, v1).
- **Roster por demarcación** (como en la plantilla real de sesión).
- **Objetivos individuales** por deportista con metodología FMF Manual 1: **Potenciar / Mejorar / Eliminar**; fundamentos por mes; estructuras del futbolista.
- **Observaciones** ligadas a sesiones y microciclos (trazabilidad del seguimiento).
- Alimenta el bloque de objetivos individuales de la sesión (plantilla mejorada).
**Depende de**: C2 (demarcaciones, dominio).

---

## Generación visual

### C5 — DiagramRenderer (U3)
**Responsabilidad**: Generar **diagramas en SVG** (D3) (RF-5).
- **Diagrama de tarea**: cancha esquemática con jugadores, conos, balones, zonas, flechas de movimiento (basado en plantillas/coordenadas para la v1).
- **Diagrama de organización** general de la sesión (cancha completa con zonas).
- **Gráficas de carga**: volumen/intensidad por microciclo/mesociclo (secundario).
- Soporta las zonas/momentos del modelo de juego (C1).
**Depende de**: C2 (datos de tarea/formato), C1 (curva de cargas para gráficas).

---

## Orquestación

### C6 — PlanningService
**Responsabilidad**: Coordina el **flujo agéntico macro→meso→sesión** (RF-1). Es el cerebro que encadena todo manteniendo coherencia de objetivos y cargas.
- Pide al motor (C1) la estructura de ciclos y cargas.
- Pide al dominio (C2) tareas coherentes con la fase de sesión (relación vertical, C5) y el formato.
- Integra objetivos individuales (C4) en la sesión.
- Solicita diagramas (C5), persiste/exporta (vía C7/C8), y puede enriquecer contenido con el LLM (C9).
- Mantiene la **trazabilidad**: cada sesión referencia su objetivo de meso/macro (RNF-5).
**Depende de**: C1, C2, C4, C5, y los adaptadores C7/C8/C9.

---

## Adaptadores (borde)

### C7 — PlanRepository (U4)
**Responsabilidad**: Persistencia en disco (RF-9, RNF-6).
- Guarda/lee **historial de planificaciones** y **biblioteca de ejercicios**.
- **Formato JSON** (D2) tras una **interfaz de repositorio** para poder migrar a SQLite al escalar.
- Portabilidad: respaldo = copiar una carpeta (RNF-6).

### C8 — Exporter (U4)
**Responsabilidad**: Exportar la planificación/sesión a **PDF imprimible** (RF-6).
- Maqueta tipo la plantilla real (mejorada): encabezado, tareas con diagramas, objetivos individuales, cargas, materiales, volumen, aspectos.
- Bilingüe (D6).

### C9 — LLMConnector (U5, opcional)
**Responsabilidad**: Enriquecer contenido de ejercicios (redacción, variantes, progresiones) (RF-10).
- **Conector genérico** (D5): enchufable a nube (OpenAI/Anthropic) o local (Ollama).
- **Opcional**: el agente funciona sin él (RNF-2). API key por configuración (RNF-3).

### C10 — WebUI + ChatInterface (U5)
**Responsabilidad**: Interfaz de usuario, app web local (RF-2).
- **Formularios/botones** para parámetros y navegación/edición.
- **Chat** conversacional embebido para ajustes en lenguaje natural.
- **Doble modo de entrada** (RF-3): parámetros (formulario completo) y entrevista (preguntas paso a paso), combinables.
- Selector de **idioma** (es/en, D6).
- Es un adaptador: habla con el PlanningService, no contiene lógica de dominio.

---

## Trazabilidad componente ↔ requisitos ↔ unidad

| Componente | Requisitos | Unidad |
|-----------|-----------|--------|
| PeriodizationEngine | RF-1, RF-4, RF-10, RNF-5, RNF-7 | U1 |
| FootballDomain | RF-1, RF-7, RF-9 | U2 |
| AdaptedFootballModule | RF-8 | U2 |
| PlayerTracking | (nuevo) seguimiento individual | U6 |
| DiagramRenderer | RF-5 | U3 |
| PlanningService | RF-1, RF-3, RNF-5 | orquestador |
| PlanRepository | RF-9, RNF-6 | U4 |
| Exporter | RF-6 | U4 |
| LLMConnector | RF-10, RNF-2, RNF-3 | U5 |
| WebUI + ChatInterface | RF-2, RF-3 | U5 |
