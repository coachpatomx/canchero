# Build and Test — Resumen (Agente de Fútbol)

**Fase**: CONSTRUCCIÓN → Build and Test (global, cierre de construcción)
**Fecha**: 2026-11-07
**Resultado de la suite**: **80 passed** (0 fallos) con Python 3.14 / pytest 9 / Hypothesis.

---

## 1. Estado de las unidades

| Unidad | Paquete | Tests | Estado |
|--------|---------|-------|--------|
| U1 Motor de Periodización | `periodization_engine/` | 18 (10 ej + 8 PBT) | ✅ |
| U2 Dominio Fútbol (+ adaptado) | `app/football_domain/` | 13 (9 ej + 4 PBT) | ✅ |
| U3 Diagramas y Gráficas (SVG) | `app/diagrams/` | 11 (7 ej + 4 PBT) | ✅ |
| U4 Persistencia + Exportación | `app/persistence/` | 11 (9 ej + 2 PBT) | ✅ |
| U5 Interfaz + Orquestador + LLM | `app/planning_service/`, `app/llm/`, `app/interface/` | 16 (13 orq + 3 web) | ✅ |
| U6 Seguimiento Individual | `app/player_tracking/` | 11 (8 ej + 3 PBT) | ✅ |
| **Total** | | **80** | ✅ |

## 2. Requisitos cubiertos (v1)

- RF-1 planificación encadenada · RF-2 web local + chat · RF-3 doble entrada (formulario + entrevista) · RF-4 periodización configurable (6 modelos + custom) · RF-5 diagramas SVG + gráficas · RF-6 editable + export (HTML siempre + PDF opcional) · RF-7 multi-formato · RF-8 fútbol adaptado (ciegos, PC, Down, amputados) · RF-9 historial + biblioteca · RF-10 motor híbrido (determinista + LLM opcional) · RF-11 sesión suelta alineada al macro (sin inventar).
- RNF-1 local escalable · RNF-2 offline · RNF-3 secretos por entorno · RNF-5 coherencia/trazabilidad (PBT) · RNF-6 portabilidad (round-trip) · RNF-7 motor reutilizable.

## 3. Verificación integral (tests de integración incluidos)

- **U1→U2**: `test_football_domain.test_integration_u1_u2_full_session` — el árbol del motor alimenta las tareas de fútbol, con herencia de carga.
- **U1→U4**: `test_persistence` — plan completo guardado y reabierto idéntico (round-trip).
- **U5 end-to-end (HTTP)**: `test_webapp` — crear plan + pedir sesión en lenguaje natural → sesión alineada al macro con diagrama.
- **U1→U6 vía orquestador**: smoke test — sesión de fútbol para ciegos con objetivos individuales en el HTML imprimible.

## 4. Extensiones AI-DLC

- **PBT (Activada Parcial)**: 21 propiedades con Hypothesis en los 6 paquetes (determinismo, rangos de carga, round-trips de serialización, SVG bien formado, trazabilidad, no-inventar-macro, inmutabilidad). ✅
- **Seguridad / Resiliencia**: Desactivadas por decisión (agente local). N/A en esta etapa; reevaluar al escalar a web multiusuario.

## 5. Hallazgos durante Build

- **Bug de integración (U5 web)**: la sesión quedaba "sin macro" porque la web no enlazaba el plan activo con la petición. Corregido (active_plan_id) y blindado con test. El orquestador ya era correcto.
- **Reparto de semanas (U1)**: fallo inicial con duraciones cortas (más períodos que semanas); corregido con método de Hamilton. Cubierto por PBT.

## 6. Limitaciones conocidas (no bloquean v1)

- Conectores LLM reales (OpenAI/Anthropic/Ollama) son puntos de extensión; por defecto NullConnector (offline). La estructura nunca depende del LLM.
- PDF nativo requiere instalar WeasyPrint (extra `pdf`); sin él, se usa "Imprimir → Guardar como PDF" del navegador.
- Reglas finas de PC/Down/amputados marcadas `validated=false` — pendientes de validación del usuario (experto). El agente no las presenta como verificadas.
- Diagramas esquemáticos (no editor de pizarra), según alcance v1 de RF-5.
- UI de edición de roster/objetivos y ruta /chat completa: API lista, pantallas ampliables.
