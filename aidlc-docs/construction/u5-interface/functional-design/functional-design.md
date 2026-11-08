# Functional Design — U5 Interfaz Web + Chat + LLM (+ Orquestador)

**Fase**: CONSTRUCCIÓN → Functional Design (U5)
**Unidad**: U5 — Interfaz, en `app/planning_service/` (orquestador) + `app/interface/` (web/chat/LLM)
**Fuentes directas**: `requirements.md` (RF-2, RF-3, RF-10, RF-11, RNF-1/2/3), `services.md` (regla S1.b sesión-suelta-alineada-al-macro), `component-methods.md` (C6 PlanningService, C9 LLMConnector, C10 WebUI/ChatInterface), `knowledge-base/metodologia-fmf.md` (C5 relación vertical).
**Decisiones aplicadas**: D5 (conector LLM genérico opcional), D6 (bilingüe), RF-11 (sesión suelta sin inventar macro).
**Nota**: esta unidad cierra el **hilo end-to-end usable**.

---

## 1. Propósito y fronteras

U5 es el **cerebro de coordinación + la cara visible**. Dos capas:
- **PlanningService (orquestador)**: encadena U1→U2→U3→U4 para producir planes y sesiones coherentes. Es lógica de aplicación, **sin UI**.
- **Interface**: app web local (FastAPI + HTML server-rendered), chat, modo entrevista, selector de idioma, y conector LLM opcional.

**Depende de**: U1, U2, U3, U4, y U6 (cuando exista). **Nadie depende de U5** (es la cúspide).

**Lo que U5 NO hace**:
- No reimplementa periodización (delega en U1), ni contenido (U2), ni dibujo (U3), ni disco (U4).
- El LLM es **opcional**: todo el flujo determinista funciona sin él (RNF-2).

---

## 2. PlanningService (orquestador) — el corazón

```
generate_plan(input: PlanInput) -> Result<TrainingPlan, DomainError>
    # Flujo completo: U1.build_full_tree -> por cada slot, U2.suggest_tasks ->
    # U3.render diagrama -> ensambla SessionDoc -> TrainingPlan. Determinista.

generate_session(request: SessionRequest, context: PlanContext) -> Result<SessionDoc, DomainError>
    # Genera UNA sesión. Aplica la regla S1.b (ver §3): la alinea al macro vigente,
    # o entra en modo entrevista si no hay macro (RF-11). Sin inventar macro.

edit_plan(plan: TrainingPlan, change: EditCommand) -> Result<TrainingPlan, DomainError>
    # Aplica una edición (desde formulario o chat) y regenera lo afectado (RF-6).

enrich_session(session: SessionDoc, options: LlmOptions) -> SessionDoc
    # Enriquecimiento OPCIONAL vía LLM (redacción/variantes). No-op si LLM off (RF-10).
```

**PlanInput**: parámetros de temporada (SeasonParams de U1) + modelo + formato + idioma + objetivos. Viene por formulario o se construye por entrevista.

**PlanContext**: el macro vigente (si existe) + formato + repo + idioma.

---

## 3. Regla S1.b — sesión suelta alineada al macro (RF-11)

Algoritmo determinista de `generate_session`:

1. **Parsear la petición** (contenido + condicionantes): "conducción", "espacio reducido", "esta semana". En modo determinista se mapea por **palabras clave** a aspectos/estrategia/espacio (sin LLM). Si el LLM está activo, puede ayudar a extraer la intención, pero el resultado se valida contra el catálogo de U2.
2. **¿Hay macro vigente que cubra la fecha?**
   - **Sí** → localizar el microciclo/fase correspondiente a "esta semana"; tomar su `SessionSlot` y su carga; pedir a U2 tareas coherentes con esa fase **y** con el contenido pedido; heredar objetivos del meso/macro. Resultado: sesión **alineada** con trazabilidad completa.
   - **No** → **no inventar macro**. Entrar en **modo entrevista** (RF-3): pedir los datos mínimos de temporada para construir un macro con sentido (U1), del cual derivar hasta la sesión pedida.
   - **Usuario rechaza dar datos** → generar la sesión suelta igualmente pero **marcarla** `alignment="none"` ("sin macro / alineación parcial"). Degradación explícita.
3. **Ensamblar** la sesión (tareas + diagramas + cargas) y devolverla con su `alignment` (`full` | `partial` | `none`).

---

## 4. Modo entrevista (RF-3) — máquina de preguntas

```
start_interview(goal: InterviewGoal) -> InterviewState
answer(state: InterviewState, reply: str) -> InterviewState   # avanza o termina
```
- `InterviewGoal`: `build_macro` | `single_session`.
- Secuencia de preguntas determinista (duración de temporada, días/semana, partidos/semana, formato, objetivos...). Cada respuesta valida contra el dominio.
- Al completar, produce un `PlanInput` o `SessionRequest` listo para el orquestador.
- Combinable con formulario (RF-3): se puede precargar el formulario y ajustar por chat.

---

## 5. Conector LLM (C9) — opcional, genérico (D5, RNF-3)

```
interface LlmConnector:
    is_enabled() -> bool
    complete(prompt: str, config: LlmConfig) -> Result<str, DomainError>

Implementaciones: NullConnector (por defecto, no-op), OpenAiConnector, AnthropicConnector, OllamaConnector (local).
```
- Selección y API key **desde configuración/entorno** (RNF-3): nunca en código. `LlmConfig` lee `provider`, `model`, `api_key_env_var`, `base_url`.
- Por defecto `NullConnector`: el agente funciona 100% offline (RNF-2). El enriquecimiento es un plus.
- `enrich_session` usa el conector solo para **texto** (redactar descripción, sugerir variantes); **nunca** para la estructura/cargas (eso es determinista, RF-10).

---

## 6. App web local (RF-2) — FastAPI + HTML

```
Rutas (server-rendered, localhost):
  GET  /                      -> panel: historial + "nuevo plan" + "nueva sesión"
  GET  /plan/new              -> formulario de parámetros (modo parámetros, RF-3)
  POST /plan                  -> crea plan (PlanningService.generate_plan) y redirige
  GET  /plan/{id}             -> vista del plan (meso/micro/sesiones + curva de carga)
  GET  /session/new           -> entrada en lenguaje natural (RF-11) + formulario
  POST /session               -> genera sesión (generate_session) con su alignment
  GET  /session/{id}/print    -> HTML imprimible (U4) -> navegador guarda PDF
  GET  /session/{id}/pdf      -> PDF nativo si WeasyPrint (U4), si no 409 + aviso
  POST /chat                  -> chat de ajustes (ChatInterface) -> EditCommand|Answer
  POST /lang                  -> cambia idioma de sesión (es/en, D6)
```
- **Server-rendered** (Jinja2 o f-strings): simple, offline, sin build de frontend. Los SVG de U3 van inline.
- El selector de idioma afecta toda la vista (D6).

---

## 7. ChatInterface (C10) — ajustes en lenguaje natural

```
send_chat(message: str, context: PlanContext) -> ChatResult
    # Interpreta el mensaje: si es una edición ("haz la tarea 2 más corta"),
    # produce un EditCommand para PlanningService.edit_plan. Si es una pregunta,
    # responde (con LLM si está, o respuesta reglada si no).
```
- Modo determinista: mapea comandos frecuentes por patrón (cambiar duración, cambiar espacio, cambiar formato, regenerar diagrama).
- Modo LLM (si activo): interpreta frases más libres, pero la acción resultante se valida contra operaciones permitidas (no ejecuta nada fuera del dominio).

---

## 8. Determinismo y verificación (PBT parcial)

- `generate_plan`/`generate_session` **deterministas** sin LLM: mismas entradas → mismo plan/sesión (incluye el id del macro).
- Propiedades:
  1. **Trazabilidad end-to-end**: toda sesión generada con macro vigente tiene `alignment="full"` y referencia su microciclo/fase.
  2. **No se inventa macro**: sin macro y sin datos → `alignment="none"`; nunca aparece un macro "fantasma".
  3. **LLM off = determinista**: `enrich_session` con NullConnector devuelve la sesión sin cambios estructurales.
  4. **Herencia de carga**: las tareas de la sesión respetan la carga del slot (vía U2).
  5. **Round-trip web**: un plan generado se guarda (U4) y se reabre igual.
  6. **Secretos**: `LlmConfig` nunca contiene la clave literal; la lee de entorno.

---

## 9. Errores y degradación
`Result`/`DomainError`. Variantes: `NoMacroForDate`, `InterviewIncomplete`, `LlmDisabled`, `InvalidEditCommand`. Degradaciones: sin LLM (determinista), sin WeasyPrint (HTML print), sin macro (entrevista o alignment none).

---

## 10. Trazabilidad requisitos → diseño

| Requisito | Cubierto por |
|-----------|--------------|
| RF-1 encadenado | §2 generate_plan |
| RF-2 web local + chat | §6 rutas + §7 chat |
| RF-3 doble entrada | §4 entrevista + §6 formulario |
| RF-10 híbrido | §5 LLM opcional + §2 estructura determinista |
| RF-11 sesión alineada | §3 regla S1.b |
| RNF-1 local escalable | §1 orquestador sin UI (reutilizable en web multiusuario) |
| RNF-2 offline | §5 NullConnector por defecto |
| RNF-3 secretos | §5 API key por entorno + §8 prop 6 |
| D5 LLM enchufable | §5 interfaz LlmConnector |
| D6 bilingüe | §6 selector idioma |

---

## 11. Estructura de código prevista

```
app/
├── planning_service/
│   ├── __init__.py
│   ├── orchestrator.py     # PlanningService: generate_plan/generate_session/edit_plan/enrich_session
│   ├── session_request.py  # SessionRequest, PlanInput, PlanContext, alignment
│   ├── interview.py        # máquina de entrevista (RF-3)
│   └── intent.py           # parseo determinista de contenido/condicionantes (keywords)
├── llm/
│   ├── __init__.py
│   ├── connector.py        # interfaz LlmConnector + LlmConfig (secretos por entorno)
│   └── null_connector.py   # NullConnector (por defecto, offline)
└── interface/
    ├── __init__.py
    ├── webapp.py           # FastAPI app + rutas
    └── templates.py        # render HTML server-side (SVG inline, bilingüe)
```

> FastAPI/uvicorn se añaden como dependencia de la app (grupo `web`). El orquestador NO depende de FastAPI (RNF-1: núcleo desacoplado de la interfaz).
