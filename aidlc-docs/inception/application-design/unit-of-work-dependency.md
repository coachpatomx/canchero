# Dependencias y Orden de Construcción — Unidades de Trabajo

**Etapa**: INCEPCIÓN → Units Generation
**Orden**: vertical / valor pronto (Q2=A).

---

## Matriz de dependencias entre unidades

Lectura: fila **depende de** columna. `●` = dependencia directa.

| ↓ depende de → | U1 | U2 | U3 | U4 | U5 | U6 |
|----------------|:--:|:--:|:--:|:--:|:--:|:--:|
| **U1 Motor**            | — |   |   |   |   |   |
| **U2 Dominio Fútbol**   | ● | — |   |   |   |   |
| **U3 Diagramas**        | ● | ● | — |   |   |   |
| **U4 Persist./Export**  |   | ● | ● | — |   |   |
| **U5 Interfaz+Orq.**    | ● | ● | ● | ● | — | ● |
| **U6 Seguim. Individual** |  | ● |   |   |   | — |

- **U1** no depende de nadie → paquete reutilizable (RNF-7).
- **U5** (interfaz + orquestador) es la que conoce a todas (coordina la cadena).
- **Sin ciclos**. Grafo acíclico dirigido.

```
U1 ──▶ U2 ──▶ U3 ──▶ U4 ──▶ U5
        │              ▲       ▲
        └──▶ U6 ────────┘       │
        └──────────────────────┘
(U1 también alimenta U3 directamente para gráficas de carga,
 y al orquestador en U5 para la cadena macro→meso→sesión)
```

---

## Orden de construcción (vertical — Q2=A)

El objetivo es llegar pronto a un **hilo end-to-end mínimo**: generar una sesión con diagrama y exportarla, antes de completar cada unidad al 100%.

### Fase 1 — Núcleo determinista
1. **U1 Motor de Periodización** (completo o casi): ciclos + al menos 1 modelo funcionando (p. ej. Tradicional), luego el resto de los 5. Base de todo. Candidato PBT desde el inicio.

### Fase 2 — Dominio mínimo
2. **U2 Dominio Fútbol** con **fútbol 11 + fútbol para ciegos** (Q4=A): modelo de ejercicio, formatos, un set inicial de biblioteca, vocabulario de modelo de juego.

### Fase 3 — Hilo end-to-end mínimo (valor tangible pronto)
3. **U3 Diagramas** (diagrama de tarea SVG primero; gráfica de carga después).
4. **U4 Persistencia + Export** (guardar/leer JSON; PDF de sesión).
5. **U5 Interfaz + Orquestador** (mínimo): un flujo que, dado un macro, genere una sesión con diagrama y la exporte. Aquí se ve la cadena funcionando.

> Al terminar la Fase 3 ya existe un agente usable punta a punta: armar macro → bajar a sesión → diagrama → PDF.

### Fase 4 — Completar y refinar
6. **U6 Seguimiento Individual** integrado a la sesión (objetivos individuales en la hoja).
7. Completar: los 5 modelos de periodización, formatos 7 y sala, chat de ajustes (RF-3), conector LLM (RF-10), regla de sesión-suelta-alineada-al-macro (RF-11), gráficas de carga, i18n es/en completo (D6).

### Fase 5 — Build and Test global
8. Construcción, pruebas (incl. PBT parcial del motor y round-trips de serialización JSON) y verificación de coherencia macro→meso→sesión (RNF-5).

---

## Construcción por unidad en CONSTRUCCIÓN

Cada unidad pasará por su ciclo (según execution-plan): Functional Design → NFR Requirements → NFR Design → Code Generation. **Build and Test** es global al final. **Infrastructure Design** se omite (agente local).

| Orden | Unidad | Entra a Construcción |
|-------|--------|----------------------|
| 1 | U1 | Functional Design (ciclos, modelos, cargas) |
| 2 | U2 | Functional Design (ejercicio, formatos, biblioteca) |
| 3 | U3 | Functional Design (SVG) |
| 4 | U4 | Functional Design (esquema JSON, PDF) |
| 5 | U6 | Functional Design (ficha, objetivos individuales) |
| 6 | U5 | Functional Design (orquestación, UI, chat, LLM) |

> Nota: U6 puede diseñarse antes o en paralelo a U5, pues solo depende de U2. Se construye su integración final dentro del hilo de U5.
