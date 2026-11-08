# Unidades de Trabajo — Agente de Fútbol

**Etapa**: INCEPCIÓN → Units Generation
**Tipo**: Greenfield · **Monolito modular** (un solo usuario, agente local)
**Decisiones aplicadas**: Q1=A (monolito modular, motor como paquete reutilizable), Q2=A (orden vertical), Q3=A (U6 unidad propia), Q4=A (empezar con 2 formatos), Q5=C (ambos modos de macro).

---

## Terminología

- **Unidad de Trabajo (U#)**: agrupación lógica para desarrollo. Aquí cada unidad = **módulo lógico** del monolito.
- No hay servicios desplegables independientes (es local). El **motor de periodización (U1)** se empaqueta como **librería interna reutilizable** para futuros agentes de otros deportes (RNF-7).

---

## Estrategia de organización de código (Greenfield)

Monolito modular. El motor vive como paquete separado e independiente del resto; las demás unidades son módulos de la app.

```
/ (workspace root)
├── periodization_engine/        # U1 — paquete/librería reutilizable (SIN fútbol)
│   ├── (modelos de ciclos, fases, cargas, 5 modelos de periodización)
│   └── (API pública determinista)
├── app/                         # aplicación Agente de Fútbol
│   ├── football_domain/         # U2 — formatos, ejercicios, biblioteca, modelo de juego
│   │   └── adapted/             #      submódulo adaptaciones (fútbol para ciegos, etc.)
│   ├── player_tracking/         # U6 — roster, objetivos individuales, observaciones
│   ├── diagrams/                # U3 — render SVG tareas/organización + gráficas de carga
│   ├── persistence/             # U4 — repositorio JSON + exportador PDF
│   ├── planning_service/        # orquestador (cadena macro→meso→sesión)
│   └── interface/               # U5 — web local + chat + conector LLM
├── data/                        # datos del usuario (planes, biblioteca) en JSON — portable (RNF-6)
└── aidlc-docs/                  # documentación (NO código)
```

> Nota: nombres de carpeta orientativos; el lenguaje/estructura exacta se fija en NFR Requirements (candidato Python). La **frontera dura** es `periodization_engine/` ↔ `app/`: el motor no importa nada de `app/`.

---

## Definición de unidades

### U1 — Motor de Periodización *(paquete reutilizable)*
- **Responsabilidad**: Lógica determinista de ciclos (macro→meso→micro→sesión), fases, distribución de cargas, y los **6 modelos** (Tradicional, Bloques, ATR, Periodización Táctica, Entrenamiento Estructurado, Esquema de A. González para fútbol). Permite modelos personalizados (RF-4).
- **Entrega**: `buildMacrocycle`, `deriveMesocycles/Microcycles/SessionSlots`, `computeLoadCurve`, `listModels`, `registerCustomModel`.
- **No contiene**: nada de fútbol, disco, UI ni LLM.
- **Soporta**: ambos modos de armado del macro (Q5=C): de una vez (todo el árbol) o por partes (nivel a nivel, validando).
- **Requisitos**: RF-1, RF-4, RF-10 (parte determinista), RNF-5, RNF-7. PBT (funciones puras).
- **Dependencias**: ninguna.

### U2 — Dominio Fútbol (+ adaptado)
- **Responsabilidad**: Formatos de fútbol, modelo de ejercicio/tarea (con materiales, carga, volumen, intensidad, aspectos téc/tác/fís/psi), biblioteca de ejercicios, vocabulario de modelo de juego (dinámicas/fases/momentos/fundamentos de C1-C2), catálogos bilingües (D6). Submódulo **adaptado** activable (fútbol para ciegos: balón sonoro, guías, zonas).
- **Alcance inicial (Q4=A, ampliado 2026-11-07)**: **fútbol 11** (convencional base) + **4 modalidades adaptadas con contenido real**: fútbol 7 PC, fútbol Down/discapacidad intelectual, fútbol 5 ciegos, fútbol amputados. Fútbol 7 y sala convencionales + otras modalidades adaptadas (powerchair, sordos) se añaden después como configuración (catálogo extensible). Reglas finas de PC/Down/amputados marcadas como editables/pendientes de validación del usuario.
- **Requisitos**: RF-7, RF-8, RF-9 (biblioteca), soporte a RF-1/RF-5/RF-11.
- **Dependencias**: U1.

### U3 — Diagramas y Gráficas
- **Responsabilidad**: Render **SVG** (D3): diagrama de tarea (jugadores, conos, balones, zonas, flechas), diagrama de organización de sesión, y gráficas de carga (volumen/intensidad).
- **Requisitos**: RF-5.
- **Dependencias**: U2 (datos de tarea/formato), U1 (curva de cargas para gráficas).

### U4 — Persistencia y Exportación
- **Responsabilidad**: Repositorio en **JSON** (D2) tras interfaz (migrable a SQLite) para historial + biblioteca; portabilidad por carpeta (RNF-6). **Exportador a PDF** bilingüe con la maqueta de la plantilla mejorada (objetivos individuales, cargas, materiales, volumen, aspectos).
- **Requisitos**: RF-6, RF-9, RNF-6.
- **Dependencias**: U2, U3.

### U5 — Interfaz Web + Chat + Conector LLM *(incluye orquestación)*
- **Responsabilidad**: App web local (RF-2), formularios + chat (RF-3 doble entrada), selector de idioma (D6). **Conector LLM genérico** opcional (D5, RF-10, RNF-2, RNF-3). Aloja el **PlanningService** (orquestador) que encadena macro→meso→sesión y aplica la regla de "sesión suelta alineada al macro" (RF-11).
- **Requisitos**: RF-2, RF-3, RF-10, RF-11, RNF-1, RNF-2, RNF-3.
- **Dependencias**: U1, U2, U3, U4, U6.

### U6 — Seguimiento Individual por Deportista
- **Responsabilidad**: Roster por demarcación, **objetivos individuales** (Potenciar/Mejorar/Eliminar, Manual 1 FMF), observaciones ligadas a sesiones/microciclos, ficha/dossier por jugador. Alimenta el bloque de objetivos individuales de la sesión (plantilla mejorada).
- **Requisitos**: seguimiento individual (v1, opción A).
- **Dependencias**: U2.

---

## Trazabilidad requisitos → unidad

| Requisito | Unidad(es) |
|-----------|-----------|
| RF-1 planificación encadenada | U1 + orquestador (U5) |
| RF-2 web local + chat | U5 |
| RF-3 doble modo entrada | U5 |
| RF-4 periodización configurable | U1 |
| RF-5 diagramas y gráficas | U3 |
| RF-6 editable + PDF | U4 + orquestador (U5) |
| RF-7 multi-formato | U2 |
| RF-8 fútbol adaptado | U2 (submódulo) |
| RF-9 historial + biblioteca | U4 (persistencia) + U2 (biblioteca) |
| RF-10 motor híbrido | U1 (determinista) + U5 (LLM) |
| RF-11 sesión suelta alineada al macro | orquestador (U5) + U1 |
| RNF-1 local escalable | organización modular + fronteras |
| RNF-2 offline | U5 (LLM opcional) |
| RNF-3 secretos | U5 (conector LLM) |
| RNF-5 coherencia/trazabilidad | U1 + orquestador; PBT |
| RNF-6 portabilidad | U4 |
| RNF-7 motor reutilizable | U1 (paquete separado) |
| Seguimiento individual | U6 |

**Cobertura**: todos los RF-1…RF-11 y RNF-1…RNF-7 quedan asignados. Sin requisitos huérfanos.
