# Code Summary — U5 Interfaz Web + Chat + LLM (+ Orquestador)

**Estado**: COMPLETA. Suite total **69 passed** (18 U1 + 13 U2 + 11 U3 + 11 U4 + 13 U5 orquestador + 3 web). **Hilo end-to-end usable logrado.**

## Código generado (en workspace root `/kiro`)
```
app/
├── planning_service/           # ORQUESTADOR (no conoce la UI, RNF-1)
│   ├── orchestrator.py         # PlanningService: generate_plan/generate_session/edit/enrich
│   ├── session_request.py      # PlanInput, SessionRequest, PlanContext, Alignment
│   ├── intent.py               # parseo determinista de contenido/condicionantes (keywords)
│   └── interview.py            # máquina de entrevista (RF-3)
├── llm/                        # conector LLM opcional (D5, RF-10, RNF-3)
│   ├── connector.py            # LlmConfig (clave por entorno) + interfaz
│   └── null_connector.py       # NullConnector (offline por defecto) + build_connector
└── interface/                  # app web local (RF-2), FastAPI opcional
    ├── webapp.py               # rutas: /, /plan, /session, /session/{id}/print
    └── templates.py            # render HTML server-side (SVG inline, bilingüe)
run_web.py                      # lanzador: python run_web.py -> http://127.0.0.1:8000
tests/test_orchestrator.py      # 11 ejemplos + 2 propiedades PBT
tests/test_webapp.py            # 3 tests de la web (skip si FastAPI ausente)
```

## Qué cumple
- **RF-1**: `generate_plan` encadena U1→U2→U3→U4 (una SessionDoc por microciclo).
- **RF-2**: app web local con formularios + entrada en lenguaje natural.
- **RF-3**: modo parámetros (formulario) + modo entrevista (máquina de preguntas).
- **RF-10**: estructura 100% determinista; LLM solo para texto, opcional; NullConnector por defecto.
- **RF-11 (regla S1.b)**: sesión alineada al macro vigente (`alignment=full`); sin macro NO se inventa (`alignment=none`); entrevista para construir macro con sentido.
- **RNF-1**: orquestador desacoplado de FastAPI (reutilizable si se escala).
- **RNF-3**: API key solo por variable de entorno; `LlmConfig` guarda el nombre de la variable, no la clave (test lo verifica).
- **D6**: render bilingüe.

## Bug de integración encontrado y corregido
El flujo web marcaba la sesión como "sin macro" aunque el plan existía, porque la web no enlazaba el `plan_id` del plan recién creado con la petición de sesión. Corregido: la web guarda el `active_plan_id` y lo usa por defecto → la sesión se alinea al macro vigente (banner verde). La lógica del orquestador ya era correcta (tests lo probaban con macro inyectado); el fallo era de la capa web. Blindado con `test_create_plan_then_aligned_session`.

## Verificación end-to-end (HTTP, tu caso de uso)
1. Crear plan de temporada (modelo González, fútbol ciegos, 17 semanas) → períodos correctos.
2. Pedir "esta semana quiero una sesión de conducción en espacio reducido" →
   sesión **alineada al macro** (banner verde), con diagrama SVG y el contenido de conducción inyectado.

## Cómo levantar la web
```
pip install '.[web]'     # FastAPI + uvicorn
python run_web.py        # http://127.0.0.1:8000
```

## Pendientes conocidos (no bloquean)
- ChatInterface de ajustes por lenguaje natural: la base (edit_session_duration, parse_intent) está; la ruta /chat completa se puede ampliar.
- Conectores LLM reales (OpenAI/Anthropic/Ollama): punto de extensión; por defecto NullConnector. La estructura nunca depende del LLM.
- Objetivos individuales en la sesión: placeholder hasta integrar U6.
