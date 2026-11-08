"""Lanzador de la app web local del Agente de Fútbol (RF-2).

Uso:
    pip install '.[web]'          # instala FastAPI + uvicorn
    python run_web.py             # abre en http://127.0.0.1:8000

El LLM es opcional (RF-10): por defecto NullConnector (offline). Para activarlo,
exporta las variables de entorno AGENTE_LLM_PROVIDER / AGENTE_LLM_MODEL /
AGENTE_LLM_API_KEY_VAR (nunca la clave en código, RNF-3).
"""
from __future__ import annotations

from app.config_env import load_dotenv
from app.interface import create_app
from app.llm import LlmConfig, build_connector
from app.persistence import JsonFileRepository
from app.planning_service import PlanningService


def build():
    load_dotenv()  # carga .env si existe (tu clave de LLM, etc.)
    repo = JsonFileRepository(root="data")
    cfg = LlmConfig.from_env()
    llm = build_connector(cfg)
    # Aviso en consola de qué modo de LLM quedó activo (sin exponer la clave).
    status = "activo" if llm.is_enabled() else "desactivado (modo determinista)"
    print(f"[Agente de Fútbol] LLM: proveedor='{cfg.provider}' -> {status}")
    service = PlanningService(repo=repo, llm=llm)
    return create_app(service)


app = build()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
