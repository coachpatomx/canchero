"""Entrevista estructurada para crear un macrociclo (estilo AI-DLC).

El agente guía al entrenador con una serie de preguntas (una a una en modo
GUIADO, o todas de golpe en modo EXPERTO). Cada pregunta trae opciones con una
explicación breve y una RECOMENDACIÓN. Al final arma el PlanInput + metadatos.

Diseño clave:
- Sin estado en el servidor: el progreso vive en un dict `answers` que viaja de
  ida y vuelta (se serializa a la URL/campos ocultos). Así es robusto y simple.
- No decide el idioma ni toca el motor: solo RECOGE datos y los valida.
"""
from __future__ import annotations

from dataclasses import dataclass

# Catálogo de modelos de periodización con explicación y para quién se recomienda.
MODELOS = [
    ("traditional", "Tradicional (Matveyev)",
     "Clásico: un gran periodo preparatorio y luego el competitivo. Volumen alto al "
     "inicio que baja mientras sube la intensidad.",
     "Temporadas largas con una competencia principal. Base sólida."),
    ("blocks", "Por bloques (Issurin)",
     "Concentra pocas capacidades por bloque (acumulación → transformación → "
     "realización). Cargas concentradas.",
     "Deportistas ya entrenados que necesitan picos de forma."),
    ("atr", "ATR (Acumulación–Transformación–Realización)",
     "Variante de bloques en mesociclos cortos que se repiten. Flexible para "
     "calendarios con varias competencias.",
     "Ligas con partidos frecuentes o varios objetivos en la temporada."),
    ("tactical", "Periodización Táctica (Frade)",
     "Todo gira en torno al modelo de juego; la carga se distribuye en el "
     "microciclo semanal (morfociclo).",
     "Equipos de fútbol con partido semanal y foco en el juego."),
    ("structured", "Entrenamiento Estructurado (Seirul·lo)",
     "Basado en situaciones del juego y las cualidades del jugador; muy "
     "individualizado.",
     "Cuerpos técnicos avanzados con trabajo individualizado."),
    ("football_gonzalez", "Esquema A. González (torneos cortos)",
     "Pensado para torneos cortos: prepara rápido y mantiene forma en pocas "
     "semanas.",
     "Torneos relámpago o pretemporadas muy cortas."),
]

FORMATOS = [
    ("football_11", "Fútbol 11", False),
    ("football_7", "Fútbol 7", False),
    ("futsal", "Fútbol sala", False),
    ("blind_5", "Fútbol 5 para ciegos", True),
    ("cp_7", "Fútbol 7 PC (parálisis cerebral)", True),
    ("down", "Fútbol para personas con síndrome de Down", True),
    ("amputee", "Fútbol para amputados", True),
]

CATEGORIAS = ["", "Sub-13", "Sub-15", "Sub-17", "Sub-19", "Sub-23", "Libre", "Primer equipo"]

# Orden de la entrevista (modo guiado). Cada paso tiene id, pregunta y tipo.
STEPS = [
    "team", "format", "weeks", "days", "matches", "start_date", "model", "category",
]


def _recommend_model(fmt_id: str, weeks: int, matches: int) -> str:
    """Recomendación simple de modelo según contexto."""
    if fmt_id in ("blind_5", "cp_7", "down", "amputee"):
        return "atr"  # calendarios adaptados suelen tener competencias intermitentes
    if weeks and weeks <= 8:
        return "football_gonzalez"
    if matches and matches >= 1:
        return "tactical"
    return "traditional"


def next_question(answers: dict) -> dict | None:
    """Devuelve la siguiente pregunta pendiente (o None si ya están todas).

    Retorna un dict con: id, texto, tipo ('text'|'number'|'choice'|'date'),
    opciones (para choice) y una recomendación opcional.
    """
    a = answers
    if not a.get("team"):
        return {"id": "team", "texto": "¿Para qué equipo es el plan? (nombre del equipo)",
                "tipo": "text", "placeholder": "Ej. Club América — Ciegos"}
    if not a.get("format"):
        opts = [{"value": fid, "label": name + (" ♿" if adap else "")}
                for fid, name, adap in FORMATOS]
        return {"id": "format", "texto": "¿Qué formato/modalidad de fútbol?",
                "tipo": "choice", "opciones": opts,
                "recomendacion": "Si es adaptado, la hoja usará la plantilla Fútbol Inclusivo."}
    if not a.get("weeks"):
        return {"id": "weeks", "texto": "¿Cuántas semanas dura el plan?",
                "tipo": "number", "placeholder": "20",
                "recomendacion": "Una temporada regular suele ir de 16 a 24 semanas; un torneo corto, 6 a 10."}
    if not a.get("days"):
        return {"id": "days", "texto": "¿Cuántos días de entrenamiento por semana?",
                "tipo": "number", "placeholder": "4"}
    if a.get("matches") is None or a.get("matches") == "":
        return {"id": "matches", "texto": "¿Cuántos partidos por semana? (0, 1 o 2)",
                "tipo": "number", "placeholder": "1",
                "recomendacion": "Si juegas cada quince días o cada mes, pon 0 y luego registras las fechas de competencia."}
    if not a.get("start_date"):
        return {"id": "start_date", "texto": "¿En qué fecha inicia el plan? (para calcular meses y fechas reales)",
                "tipo": "date", "placeholder": "2026-08-10"}
    if not a.get("model"):
        rec = _recommend_model(a.get("format", ""), _int(a.get("weeks")), _int(a.get("matches")))
        opts = [{"value": mid, "label": name, "desc": desc, "para": para,
                 "recomendado": (mid == rec)} for mid, name, desc, para in MODELOS]
        rec_name = next((n for i, n, _, _ in MODELOS if i == rec), rec)
        return {"id": "model", "texto": "¿Qué modelo de periodización usamos?",
                "tipo": "choice-rich", "opciones": opts,
                "recomendacion": f"Para tu caso recomiendo: {rec_name}."}
    # category es OPCIONAL: solo se pregunta si aún no se marcó como respondida.
    if "category" not in a:
        opts = [{"value": c or "__none__", "label": c or "— sin especificar —"}
                for c in CATEGORIAS]
        return {"id": "category", "texto": "¿Categoría? (opcional)",
                "tipo": "choice", "opciones": opts}
    return None  # entrevista completa


def is_complete(answers: dict) -> bool:
    return next_question(answers) is None


def _int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def summary(answers: dict) -> str:
    """Resumen legible de lo capturado (para confirmar antes de generar)."""
    a = answers
    fmt = next((n for fid, n, _ in FORMATOS if fid == a.get("format")), a.get("format", ""))
    model = next((n for mid, n, _, _ in MODELOS if mid == a.get("model")), a.get("model", ""))
    partes = [
        f"Equipo: {a.get('team','')}",
        f"Formato: {fmt}",
        f"Semanas: {a.get('weeks','')} · {a.get('days','')} días/sem · {a.get('matches','')} partido(s)/sem",
        f"Inicio: {a.get('start_date','')}",
        f"Modelo: {model}",
    ]
    if a.get("category"):
        partes.append(f"Categoría: {a.get('category')}")
    return " · ".join(partes)


def express_parse(text: str, llm=None) -> dict:
    """Modo experto: extrae todos los campos de una sola frase.

    Usa el LLM si está activo (JSON con los campos); si no, reglas con regex.
    Devuelve un dict `answers` parcial o completo.
    """
    import json
    import re

    a: dict = {}
    enabled = bool(getattr(llm, "is_enabled", lambda: False)()) if llm else False
    if enabled:
        prompt = (
            "Extrae los datos de este plan de entrenamiento y responde SOLO un JSON con las "
            'claves que encuentres: {"team":"", "format":"football_11|football_7|futsal|'
            'blind_5|cp_7|down|amputee", "weeks":N, "days":N, "matches":N, '
            '"start_date":"YYYY-MM-DD", "model":"traditional|blocks|atr|tactical|structured|'
            'football_gonzalez", "category":""}. Interpreta fechas en español. '
            f'Frase: "{text}"\nJSON:'
        )
        try:
            res = llm.complete(prompt)
            raw = getattr(res, "value", "") or ""
            if "{" in raw:
                raw = raw[raw.find("{"):raw.rfind("}") + 1]
            data = json.loads(raw)
            if isinstance(data, dict):
                for k in ("team", "format", "weeks", "days", "matches", "start_date",
                          "model", "category"):
                    if data.get(k) not in (None, ""):
                        a[k] = data[k]
        except Exception:
            pass
    # Reglas (complementan o reemplazan si no hubo LLM).
    t = text.lower()
    if "weeks" not in a:
        m = re.search(r"(\d+)\s*semanas", t)
        if m:
            a["weeks"] = int(m.group(1))
    if "days" not in a:
        m = re.search(r"(\d+)\s*d[ií]as", t)
        if m:
            a["days"] = int(m.group(1))
    if "matches" not in a:
        m = re.search(r"(\d+)\s*partidos?", t)
        if m:
            a["matches"] = int(m.group(1))
    if "format" not in a:
        if "ciego" in t:
            a["format"] = "blind_5"
        elif "amputad" in t:
            a["format"] = "amputee"
        elif "down" in t:
            a["format"] = "down"
        elif "pc" in t or "cerebral" in t:
            a["format"] = "cp_7"
        elif "sala" in t or "futsal" in t:
            a["format"] = "futsal"
        elif "fútbol 7" in t or "futbol 7" in t:
            a["format"] = "football_7"
        elif "11" in t:
            a["format"] = "football_11"
    if "model" not in a:
        for mid, name, _, _ in MODELOS:
            if mid in t or name.split()[0].lower() in t:
                a["model"] = mid
                break
    if "start_date" not in a:
        from app.planning_service.calendar_map import parse_spanish_date
        d = parse_spanish_date(text)
        if d:
            a["start_date"] = d.isoformat()
    if "team" not in a:
        # Heurística: lo que va antes de la primera coma (si no parece un número/dato).
        first = text.split(",")[0].strip()
        if first and not re.search(r"\d", first) and len(first) <= 60:
            a["team"] = first
    return a


def to_plan_input_kwargs(answers: dict) -> dict:
    """Convierte las respuestas en los kwargs para crear el plan + metadatos."""
    a = answers
    return {
        "title": a.get("team", "Plan de temporada"),
        "duration_weeks": _int(a.get("weeks"), 20),
        "training_days_per_week": _int(a.get("days"), 4),
        "matches_per_week": _int(a.get("matches"), 1),
        "model_id": a.get("model", "traditional"),
        "format_id": a.get("format", "football_11"),
        "category": ("" if a.get("category") in ("__none__", None) else a.get("category", "")),
        # metadatos (no van al motor; se guardan aparte)
        "_meta": {
            "team": a.get("team", ""),
            "start_date": a.get("start_date", ""),
            "competitions": a.get("competitions", []),
            "category": ("" if a.get("category") in ("__none__", None) else a.get("category", "")),
            "coordinator": a.get("coordinator", ""),
            "coach": a.get("coach", ""),
            "days_per_week": _int(a.get("days"), 4),
        },
    }
