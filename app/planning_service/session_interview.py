"""Entrevista estructurada para crear una SESIÓN (estilo AI-DLC).

Análoga a macro_interview, pero para una sesión concreta. Guía al entrenador:
plan al que pertenece → semana → qué entrenar (tema) → fundamentos técnico/
táctico/físico → duración → plantilla de hoja. Al final arma los kwargs de
SessionRequest + sheet_meta.

Sin estado en servidor: las respuestas viajan como JSON en la URL.
"""
from __future__ import annotations

# Catálogos (mismos que ya usa la UI de sesión).
TECNICOS = ["Conducción", "Pase", "Recepción", "Control orientado", "Regate",
            "Tiro a puerta", "Protección del balón", "Cabeceo", "Centro"]
TACTICOS = ["Posesión", "Presión", "Transiciones", "Toma de espacios",
            "Posicionamiento", "Repliegue", "Salida de balón", "Desmarques"]
FISICOS = ["Resistencia", "Velocidad", "Fuerza", "Agilidad", "Potencia",
           "Coordinación", "Cambio de ritmo", "Arranque"]

STEPS = ["plan", "week", "text", "technical", "tactical", "physical",
         "duration", "sheet_style"]


def next_question(answers: dict, plans: list | None = None) -> dict | None:
    """Siguiente pregunta pendiente (o None si ya están todas)."""
    a = answers
    plans = plans or []

    if "plan" not in a:
        opts = [{"value": "__none__", "label": "— Sesión suelta (sin plan) —"}]
        opts += [{"value": p["id"], "label": p["title"]} for p in plans]
        return {"id": "plan", "texto": "¿A qué plan pertenece la sesión?",
                "tipo": "choice", "opciones": opts,
                "recomendacion": "Si la vinculas a un plan, se alinea a la carga de esa semana."}
    if a.get("plan") not in ("__none__", None, "") and not a.get("week"):
        return {"id": "week", "texto": "¿De qué semana del plan? (número)",
                "tipo": "number", "placeholder": "3"}
    if "week" not in a and a.get("plan") in ("__none__", None, ""):
        a["week"] = ""  # sesión suelta: sin semana
    if not a.get("text"):
        return {"id": "text", "texto": "¿Qué quieres entrenar? (descríbelo en una frase)",
                "tipo": "text",
                "placeholder": "Ej. conducción y recepción perfilada con tiro a puerta"}
    if "technical" not in a:
        opts = [{"value": x, "label": x} for x in TECNICOS] + [{"value": "__skip__", "label": "— ninguno —"}]
        return {"id": "technical", "texto": "Fundamento técnico principal",
                "tipo": "choice", "opciones": opts}
    if "tactical" not in a:
        opts = [{"value": x, "label": x} for x in TACTICOS] + [{"value": "__skip__", "label": "— ninguno —"}]
        return {"id": "tactical", "texto": "Fundamento táctico principal",
                "tipo": "choice", "opciones": opts}
    if "physical" not in a:
        opts = [{"value": x, "label": x} for x in FISICOS] + [{"value": "__skip__", "label": "— ninguno —"}]
        return {"id": "physical", "texto": "Capacidad física principal",
                "tipo": "choice", "opciones": opts}
    if not a.get("duration"):
        return {"id": "duration", "texto": "¿Duración de la sesión? (minutos)",
                "tipo": "number", "placeholder": "90"}
    if "sheet_style" not in a:
        return {"id": "sheet_style", "texto": "¿Estilo de hoja?",
                "tipo": "choice",
                "opciones": [
                    {"value": "auto", "label": "Automático (según el formato)", "recomendado": True},
                    {"value": "inclusivo", "label": "Fútbol Inclusivo (plantilla América)"},
                    {"value": "dark", "label": "Canchero (oscuro)"},
                ],
                "recomendacion": "Automático usa Inclusivo si es modalidad adaptada."}
    return None


def is_complete(answers: dict, plans: list | None = None) -> bool:
    return next_question(answers, plans) is None


def summary(answers: dict) -> str:
    a = answers
    plan = "sin plan" if a.get("plan") in ("__none__", "", None) else f"plan {a.get('plan')}"
    foco = ", ".join(x for x in (a.get("technical"), a.get("tactical"), a.get("physical"))
                     if x and x != "__skip__")
    partes = [a.get("text", ""), plan]
    if a.get("week"):
        partes.append(f"semana {a.get('week')}")
    if foco:
        partes.append(f"foco: {foco}")
    partes.append(f"{a.get('duration','90')} min")
    return " · ".join(p for p in partes if p)


def _clean(v):
    return "" if v in ("__skip__", "__none__", None) else v


def to_session_kwargs(answers: dict, default_format: str = "football_11") -> dict:
    """Devuelve los datos para crear la sesión: request kwargs + plan_id + estilo."""
    a = answers
    plan_id = "" if a.get("plan") in ("__none__", "", None) else a.get("plan")
    try:
        week = int(a.get("week")) if a.get("week") else None
    except (TypeError, ValueError):
        week = None
    return {
        "plan_id": plan_id,
        "sheet_style": a.get("sheet_style", "auto"),
        "request": {
            "text": a.get("text", ""),
            "format_id": default_format,
            "week_index": week,
            "duration_min": _int(a.get("duration"), 90),
            "technical_focus": _clean(a.get("technical")) or "",
            "tactical_focus": _clean(a.get("tactical")) or "",
            "physical_focus": _clean(a.get("physical")) or "",
        },
    }


def _int(v, default):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default
