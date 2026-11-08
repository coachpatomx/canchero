"""Tests de la app web (U5). Se omiten si FastAPI no está instalado."""
from __future__ import annotations

import tempfile

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("httpx")  # requerido por TestClient

from fastapi.testclient import TestClient  # noqa: E402

from app.interface import create_app  # noqa: E402
from app.llm import NullConnector  # noqa: E402
from app.persistence import JsonFileRepository  # noqa: E402
from app.planning_service import PlanningService  # noqa: E402


def _client():
    svc = PlanningService(repo=JsonFileRepository(root=tempfile.mkdtemp()), llm=NullConnector())
    return TestClient(create_app(svc))


def test_home_ok():
    assert _client().get("/").status_code == 200


def test_create_plan_then_aligned_session():
    c = _client()
    # Los formularios usan GET (compatible con proxies/CDN que bloquean POST).
    r = c.get("/plan", params={
        "title": "Plan prueba", "duration_weeks": "17", "training_days_per_week": "4",
        "matches_per_week": "1", "model_id": "football_gonzalez",
        "format_id": "blind_5",
    })
    assert r.status_code == 200
    assert "resistance" in r.text  # períodos del modelo González

    # Sesión en lenguaje natural: debe alinearse al plan recién creado.
    r2 = c.get("/session", params={
        "text": "esta semana quiero una sesion de conduccion en espacio reducido",
        "format_id": "blind_5", "plan_id": "",
    })
    assert r2.status_code == 200
    assert "Alineada al macrociclo vigente" in r2.text


def test_session_without_plan_is_marked_no_macro():
    c = _client()
    # Sin crear plan: la sesión queda marcada 'sin macro'.
    r = c.get("/session", params={
        "text": "sesion de pase", "format_id": "football_11", "plan_id": "",
    })
    assert r.status_code == 200
    assert "Sin macro" in r.text


def test_view_saved_plan_from_history():
    c = _client()
    c.get("/plan", params={
        "title": "Mi plan", "duration_weeks": "12", "training_days_per_week": "4",
        "matches_per_week": "1", "model_id": "traditional", "format_id": "football_11",
    })
    home = c.get("/").text
    assert "Mi plan" in home  # aparece en el historial con su nombre
    # el historial enlaza a /plan/{id}; extraer un id y abrirlo
    import re
    m = re.search(r'/plan/([0-9a-f]+)"', home)
    assert m, "no se encontró enlace de plan en el historial"
    r = c.get(f"/plan/{m.group(1)}")
    assert r.status_code == 200
    assert "Mi plan" in r.text
