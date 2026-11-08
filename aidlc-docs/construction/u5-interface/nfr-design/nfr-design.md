# NFR Design — U5 Interfaz Web + Chat + LLM

## 1. Estructura
`app/planning_service/`, `app/llm/`, `app/interface/` (ver Functional Design §11).

## 2. Patrones
| NFR | Decisión |
|-----|----------|
| Núcleo desacoplado (RNF-1) | `orchestrator.py` recibe el repositorio y el conector LLM por inyección; no conoce FastAPI. La web lo instancia y le pasa dependencias. |
| Offline por defecto (RNF-2) | `NullConnector.is_enabled()==False`; `enrich_session` es no-op con él. |
| Secretos (RNF-3) | `LlmConfig` guarda `api_key_env_var` (nombre de la variable), no la clave. Se lee con `os.environ.get` en el momento de la llamada; si falta, el conector queda deshabilitado. |
| Determinismo | parseo de intención por tabla de keywords; `generate_plan` encadena funciones puras de U1/U2/U3. |
| Alignment explícito | `SessionDoc`/resultado lleva `alignment: full|partial|none`; la vista lo muestra como aviso. |
| Dependencias opcionales | FastAPI (grupo web) y SDKs LLM (grupo llm) con import perezoso; core testeable sin ellos. |

## 3. Flujo de inyección
```
repo = JsonFileRepository()           # U4
llm  = build_connector(LlmConfig.from_env())  # Null si no hay config
svc  = PlanningService(repo=repo, llm=llm, render=diagrams_api)
webapp = create_app(svc)              # FastAPI fino encima
```

## 4. Test
- `tests/test_orchestrator.py`: lógica pura (sin servidor) — generate_plan/session, regla S1.b, entrevista, LLM off.
- `tests/test_webapp.py`: FastAPI TestClient (solo si fastapi instalado; skip si no).
- NullConnector permite verificar RF-10 sin red.
