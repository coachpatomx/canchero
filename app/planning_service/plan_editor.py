"""Editor iterativo del macrociclo (chat tipo agente).

Convierte una instrucción en lenguaje natural ("sube el volumen de la semana 5",
"marca la semana 8 como descarga") en una ACCIÓN estructurada y la aplica sobre
el `Macrocycle` de forma segura (dataclasses.replace encadenado; todo frozen).

Dos caminos de interpretación:
1. LLM (si está activo): devuelve un JSON de acción. Preciso y flexible.
2. Reglas (fallback offline): regex simples. Garantiza que el chat FUNCIONE
   aunque no haya LLM (RNF-2), cubriendo las instrucciones más comunes.

Acciones soportadas (Fase 1):
  - set_volume      {semana|meso, valor}            fija volumen %
  - adjust_volume   {semana|meso, delta}            sube/baja volumen
  - set_intensity   {semana|meso, valor}
  - adjust_intensity{semana|meso, delta}
  - set_micro_type  {semana, tipo}                  p. ej. 'recovery' (descarga)
  - set_objective   {meso, texto}                   objetivo del mesociclo
Cada acción devuelve (macro_nuevo, mensaje_es). Nunca lanza: si algo no aplica,
devuelve el macro intacto y un mensaje explicando por qué.
"""
from __future__ import annotations

import json
import re
from dataclasses import replace

from periodization_engine import Macrocycle, Mesocycle, Microcycle, MicrocycleType

_VOL_MIN, _VOL_MAX = 10, 100
_INT_MIN, _INT_MAX = 10, 100

# Respuesta genérica amable cuando no es una orden de edición o es fuera de tema.
# Evita que el chat se "bugue" o conteste cosas raras.
_GENERIC_REPLY = (
    "Soy tu asistente de planificación. Puedo ajustar el macrociclo por ti: "
    "cambiar volumen o intensidad de una semana o mesociclo, marcar una semana "
    "como descarga, cambiar objetivos, poner el nombre del equipo, la fecha de "
    "inicio o registrar competencias. ¿Qué quieres mover? Por ejemplo: "
    "«sube el volumen de la semana 5» o «competencia el 24 de agosto vs Cruz Azul»."
)

# Sinónimos de "descarga/recuperación" -> tipo de microciclo.
_TYPE_WORDS = {
    "descarga": "recovery", "recuperacion": "recovery", "recuperación": "recovery",
    "choque": "shock", "competencia": "competition", "competitivo": "competition",
    "introductorio": "introductory", "desarrollador": "developmental",
    "precompetitivo": "precompetitive",
}


def _clamp(v, lo, hi):
    return max(lo, min(hi, int(round(v))))


def _clean_name(original_text: str, keyword: str) -> str:
    """Extrae el nombre después de la palabra clave, conservando mayúsculas
    del texto original (ej. 'ponle el nombre del equipo: CLUB AMÉRICA' -> 'CLUB AMÉRICA').

    Corta si aparece otra instrucción pegada (el macro inicia..., tengo competencia...)
    para no tragarse frases ajenas."""
    low = original_text.lower()
    idx = low.find(keyword)
    if idx == -1:
        return original_text.strip()
    rest = original_text[idx + len(keyword):]
    rest = re.sub(r"^\s*(?:\(a\))?\s*(?::|=|,|-|es|será|sera|a)?\s*", "", rest, flags=re.I)
    # Cortar antes de cualquier marcador de OTRA acción pegada en la misma frase.
    cut_markers = [
        r'\bel macro\b', r'\binicia\b', r'\bempieza\b', r'\barranca\b', r'\bcomienza\b',
        r'\btengo\b', r'\bcompetencia\b', r'\bcompetici[oó]n\b', r'\bpartido\b',
        r'\bjuego el\b', r'\bjugamos\b', r'\bsube\b', r'\bbaja\b', r'\bmarca\b',
        r'\bpon(?:le)?\b', r'\bentrenador\b', r'\bcoordinador\b', r'"',
    ]
    low_rest = rest.lower()
    cut = len(rest)
    for mk in cut_markers:
        m = re.search(mk, low_rest)
        if m and 0 < m.start() < cut:
            cut = m.start()
    return rest[:cut].strip(" .:-\"")


# --------------------------------------------------------------------------- #
# Mutación segura del macro
# --------------------------------------------------------------------------- #
def _all_micros(macro: Macrocycle):
    return [(mi, m, micro)
            for mi, m in enumerate(macro.mesocycles)
            for micro in m.microcycles]


def _rebuild(macro: Macrocycle, meso_idx: int, micro_week: int, **micro_changes) -> Macrocycle:
    """Devuelve un macro nuevo con el microciclo (por semana) modificado."""
    new_mesos = []
    for mi, meso in enumerate(macro.mesocycles):
        if mi != meso_idx:
            new_mesos.append(meso)
            continue
        new_micros = tuple(
            replace(micro, **micro_changes) if micro.week_index == micro_week else micro
            for micro in meso.microcycles
        )
        new_mesos.append(replace(meso, microcycles=new_micros))
    return replace(macro, mesocycles=tuple(new_mesos))


def _find_week(macro: Macrocycle, week: int):
    for mi, meso in enumerate(macro.mesocycles):
        for micro in meso.microcycles:
            if micro.week_index == week:
                return mi, micro
    return None, None


def apply_action(macro: Macrocycle, action: dict) -> tuple[Macrocycle, str]:
    """Aplica una acción estructurada. Devuelve (macro, mensaje_es)."""
    kind = str(action.get("accion", "")).strip()
    if not kind:
        return macro, _GENERIC_REPLY
    if kind == "chat":
        # Respuesta conversacional (saludo, duda, fuera de tema). No toca el macro.
        return macro, (action.get("respuesta") or _GENERIC_REPLY)

    # ---- acciones por SEMANA ----
    if "semana" in action and action.get("semana") is not None:
        try:
            week = int(action["semana"])
        except (TypeError, ValueError):
            return macro, "No reconocí el número de semana."
        meso_idx, micro = _find_week(macro, week)
        if micro is None:
            return macro, f"La semana {week} no existe en este macrociclo."

        if kind == "set_volume":
            v = _clamp(action.get("valor", micro.target_volume_pct), _VOL_MIN, _VOL_MAX)
            return _rebuild(macro, meso_idx, week, target_volume_pct=v), \
                f"Listo: volumen de la semana {week} fijado en {v}%."
        if kind == "adjust_volume":
            v = _clamp(micro.target_volume_pct + action.get("delta", 0), _VOL_MIN, _VOL_MAX)
            return _rebuild(macro, meso_idx, week, target_volume_pct=v), \
                f"Listo: volumen de la semana {week} ahora en {v}%."
        if kind == "set_intensity":
            v = _clamp(action.get("valor", micro.target_intensity_pct), _INT_MIN, _INT_MAX)
            return _rebuild(macro, meso_idx, week, target_intensity_pct=v), \
                f"Listo: intensidad de la semana {week} fijada en {v}%."
        if kind == "adjust_intensity":
            v = _clamp(micro.target_intensity_pct + action.get("delta", 0), _INT_MIN, _INT_MAX)
            return _rebuild(macro, meso_idx, week, target_intensity_pct=v), \
                f"Listo: intensidad de la semana {week} ahora en {v}%."
        if kind == "set_micro_type":
            tipo = str(action.get("tipo", "")).lower()
            tipo = _TYPE_WORDS.get(tipo, tipo)
            try:
                mt = MicrocycleType(tipo)
            except ValueError:
                return macro, f"No reconocí el tipo de microciclo «{action.get('tipo')}»."
            # Descarga = bajar también las cargas, por coherencia.
            extra = {}
            if mt == MicrocycleType.RECOVERY:
                extra = dict(target_volume_pct=_clamp(micro.target_volume_pct * 0.6, _VOL_MIN, _VOL_MAX),
                             target_intensity_pct=_clamp(micro.target_intensity_pct * 0.5, _INT_MIN, _INT_MAX))
            return _rebuild(macro, meso_idx, week, type=mt, **extra), \
                f"Listo: la semana {week} ahora es de tipo «{tipo}»."
        return macro, f"La acción «{kind}» no aplica a una semana."

    # ---- acciones por MESOCICLO ----
    if "meso" in action and action.get("meso") is not None:
        try:
            idx = int(action["meso"]) - 1  # el usuario cuenta desde 1
        except (TypeError, ValueError):
            return macro, "No reconocí el número de mesociclo."
        if not (0 <= idx < len(macro.mesocycles)):
            return macro, f"El mesociclo {action['meso']} no existe."
        meso = macro.mesocycles[idx]
        weeks = [mc.week_index for mc in meso.microcycles]

        if kind in ("set_volume", "adjust_volume", "set_intensity", "adjust_intensity"):
            new_micros = []
            for mc in meso.microcycles:
                if kind == "set_volume":
                    mc = replace(mc, target_volume_pct=_clamp(action.get("valor", mc.target_volume_pct), _VOL_MIN, _VOL_MAX))
                elif kind == "adjust_volume":
                    mc = replace(mc, target_volume_pct=_clamp(mc.target_volume_pct + action.get("delta", 0), _VOL_MIN, _VOL_MAX))
                elif kind == "set_intensity":
                    mc = replace(mc, target_intensity_pct=_clamp(action.get("valor", mc.target_intensity_pct), _INT_MIN, _INT_MAX))
                elif kind == "adjust_intensity":
                    mc = replace(mc, target_intensity_pct=_clamp(mc.target_intensity_pct + action.get("delta", 0), _INT_MIN, _INT_MAX))
                new_micros.append(mc)
            new_meso = replace(meso, microcycles=tuple(new_micros))
            new_macro = replace(macro, mesocycles=tuple(
                new_meso if i == idx else m for i, m in enumerate(macro.mesocycles)))
            return new_macro, f"Listo: ajusté el mesociclo {idx+1} (semanas {min(weeks)}–{max(weeks)})."
        if kind == "set_objective":
            txt = str(action.get("texto", "")).strip()
            if not txt:
                return macro, "Dime el objetivo que quieres poner."
            new_meso = replace(meso, objective_focus=(txt,))
            new_macro = replace(macro, mesocycles=tuple(
                new_meso if i == idx else m for i, m in enumerate(macro.mesocycles)))
            return new_macro, f"Listo: objetivo del mesociclo {idx+1} actualizado."
        return macro, f"La acción «{kind}» no aplica a un mesociclo."

    return macro, "Dime a qué semana o mesociclo aplicar el cambio (ej. «semana 5» o «mesociclo 2»)."


# --------------------------------------------------------------------------- #
# Interpretación de la instrucción
# --------------------------------------------------------------------------- #
def _rules_interpret(text: str) -> dict | None:
    """Fallback offline por reglas. Devuelve una acción o None si no entiende."""
    t = text.lower().strip()

    # ---- título del macrociclo ----
    if ("titulo" in t or "título" in t or "nombre del macro" in t or "nombre del plan" in t):
        kw = "título" if "título" in t else ("titulo" if "titulo" in t
             else ("macro" if "nombre del macro" in t else "plan"))
        nombre = _clean_name(text, kw)
        if nombre:
            return {"accion": "set_title", "texto": nombre}

    # ---- metadatos: nombre de equipo / entrenador / coordinador ----
    m = re.search(r"(?:nombre del |nombre de |)equipo\s*(?:a|:|=|es|será|sera)?\s*(.+)", t)
    if "equipo" in t and m and m.group(1).strip():
        return {"accion": "set_team", "texto": _clean_name(text, "equipo")}
    m = re.search(r"entrenador(?:\(a\))?\s*(?:a|:|=|es|será|sera)?\s*(.+)", t)
    if "entrenador" in t and m and m.group(1).strip():
        return {"accion": "set_coach", "texto": _clean_name(text, "entrenador")}
    if "coordinador" in t:
        return {"accion": "set_coordinator", "texto": _clean_name(text, "coordinador")}

    # ---- fecha de inicio del macro ----
    if any(w in t for w in ("inicia", "empieza", "arranca", "fecha de inicio", "comienza")):
        from app.planning_service.calendar_map import parse_spanish_date
        d = parse_spanish_date(text)
        if d:
            return {"accion": "set_start_date", "fecha": d.isoformat()}

    # ---- competencia / partido ----
    if any(w in t for w in ("competencia", "competición", "competicion", "partido",
                            "juego el", "jugamos", "enfrentamos", "vs ", " vs")):
        from app.planning_service.calendar_map import parse_spanish_date
        d = parse_spanish_date(text)
        rival = ""
        mr = re.search(r"(?:vs\.?|contra|frente a)\s+(.+?)(?:\s+el\b|$)", t)
        if mr:
            rival = mr.group(1).strip()
        if d:
            return {"accion": "add_competition", "fecha": d.isoformat(), "rival": rival}

    week = None
    meso = None
    mw = re.search(r"semana\s+(\d+)", t)
    if mw:
        week = int(mw.group(1))
    mm = re.search(r"meso(?:ciclo)?\s+(\d+)", t)
    if mm:
        meso = int(mm.group(1))
    target = {"semana": week} if week is not None else ({"meso": meso} if meso is not None else {})
    if not target:
        return None

    # tipo de microciclo (descarga, etc.)
    for word, _tipo in _TYPE_WORDS.items():
        if word in t and week is not None:
            return {"accion": "set_micro_type", "tipo": word, **target}

    # Quitar "semana N" / "meso N" del texto para no confundir su número con el
    # valor objetivo (p. ej. el "a 5" de "semana 5").
    t_val = re.sub(r"semana\s+\d+", " ", t)
    t_val = re.sub(r"meso(?:ciclo)?\s+\d+", " ", t_val)

    # valor explícito "a 80", "en 70%", "ponle 90"
    mval = re.search(r"(?:a|al|en|ponle|pon|poner|dejar?|déjala?|=)\s*(\d{1,3})\s*%?", t_val)
    is_vol = "volumen" in t or "vol" in t
    is_int = "intensidad" in t or "inten" in t
    if mval and (is_vol or is_int):
        val = int(mval.group(1))
        return {"accion": "set_intensity" if is_int else "set_volume", "valor": val, **target}

    # subir / bajar
    up = any(w in t for w in ("sube", "subir", "aumenta", "incrementa", "más", "mas"))
    down = any(w in t for w in ("baja", "bajar", "reduce", "disminuye", "menos"))
    if up or down:
        delta = 10 if up else -10
        if is_int:
            return {"accion": "adjust_intensity", "delta": delta, **target}
        return {"accion": "adjust_volume", "delta": delta, **target}

    # objetivo del meso
    if meso is not None and ("objetivo" in t):
        mobj = re.search(r"objetivo\s*(?:a|:|=)?\s*(.+)$", t)
        if mobj:
            return {"accion": "set_objective", "texto": mobj.group(1).strip(), "meso": meso}
    return None


def _llm_prompt(instruction: str, macro: Macrocycle) -> str:
    n = sum(len(m.microcycles) for m in macro.mesocycles)
    return (
        "Eres el asistente de planificación de un entrenador. Convierte su "
        "instrucción en UNA acción JSON para editar el macrociclo. No expliques, "
        "responde SOLO el JSON.\n"
        f"El macrociclo tiene {len(macro.mesocycles)} mesociclos y {n} semanas (1..{n}).\n"
        "Acciones válidas (elige una):\n"
        '  {"accion":"set_volume","semana":N,"valor":0-100}\n'
        '  {"accion":"adjust_volume","semana":N,"delta":±N}\n'
        '  {"accion":"set_intensity","semana":N,"valor":0-100}\n'
        '  {"accion":"adjust_intensity","semana":N,"delta":±N}\n'
        '  {"accion":"set_micro_type","semana":N,"tipo":"recovery|shock|competition|introductory|developmental|precompetitive"}\n'
        '  {"accion":"set_volume"|"adjust_volume"|...,"meso":N,...}  (aplica a todo el mesociclo)\n'
        '  {"accion":"set_objective","meso":N,"texto":"..."}\n'
        '  {"accion":"set_team","texto":"nombre del equipo"}\n'
        '  {"accion":"set_coach","texto":"nombre del entrenador"}\n'
        '  {"accion":"set_coordinator","texto":"nombre del coordinador"}\n'
        '  {"accion":"set_start_date","fecha":"YYYY-MM-DD"}  (fecha de inicio del macro)\n'
        '  {"accion":"add_competition","fecha":"YYYY-MM-DD","rival":"rival (opcional)"}\n'
        '  {"accion":"chat","respuesta":"texto breve y amable"}  (úsalo cuando el '
        "mensaje NO sea una orden de edición: saludos, preguntas, dudas o cosas fuera "
        "de tema; responde en español como un asistente de planificación, orientando "
        "sobre lo que SÍ puedes hacer, sin inventar cambios)\n"
        "Interpreta fechas en español (ej. '20 de agosto de 2026' -> 2026-08-20).\n"
        "Si el mensaje contiene VARIAS instrucciones, devuélvelas TODAS en una "
        'lista: {"acciones":[ {..}, {..} ]}. Si es una sola, puedes devolver el '
        "objeto directo. NUNCA respondas texto fuera del JSON.\n"
        f'Mensaje del entrenador: "{instruction}"\n'
        "JSON:"
    )


def _parse_action_json(raw: str) -> dict | None:
    if not raw:
        return None
    text = raw.strip()
    if "{" in text and "}" in text:
        text = text[text.find("{"):text.rfind("}") + 1]
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else None
    except (json.JSONDecodeError, ValueError):
        return None


def _parse_actions_json(raw: str) -> list[dict]:
    """Extrae una o varias acciones del JSON del LLM. Acepta:
       {"acciones":[...]}  |  [...]  |  {...}"""
    if not raw:
        return []
    text = raw.strip()
    # recortar al primer bloque { } o [ ]
    starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
    if starts:
        start = min(starts)
        end = max(text.rfind("}"), text.rfind("]"))
        if end > start:
            text = text[start:end + 1]
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return []
    if isinstance(data, dict):
        if isinstance(data.get("acciones"), list):
            return [a for a in data["acciones"] if isinstance(a, dict)]
        return [data]
    if isinstance(data, list):
        return [a for a in data if isinstance(a, dict)]
    return []


# Separadores para partir varias instrucciones dentro de un mismo mensaje
# (modo reglas, sin LLM). Comillas, saltos de línea, punto y coma, " y ", " luego ".
_SPLIT_RE = re.compile(
    r'["\n;]+|,\s+(?=sube|baja|marca|pon|ponle|aumenta|reduce|cambia|fija|el macro|'
    r'tengo|competencia|entrenador|coordinador)|\s+y\s+(?=sube|baja|marca|pon|ponle|'
    r'aumenta|reduce|cambia|fija|el macro|tengo|competencia)|\s+luego\s+|'
    r'\s+despu[eé]s\s+|\s+además\s+|\s+tambi[eé]n\s+', re.I)


def _split_instructions(text: str) -> list[str]:
    parts = [p.strip(" .,:-\"") for p in _SPLIT_RE.split(text)]
    return [p for p in parts if len(p) >= 3]


def interpret_many(llm, instruction: str, macro: Macrocycle) -> list[dict]:
    """Devuelve una LISTA de acciones (puede traer varias si el mensaje las tiene).

    Usa LLM si está activo (puede devolver varias acciones de una); si no, parte
    el texto por separadores y aplica reglas a cada trozo."""
    enabled = bool(getattr(llm, "is_enabled", lambda: False)()) if llm else False
    if enabled:
        try:
            res = llm.complete(_llm_prompt(instruction, macro))
            raw = getattr(res, "value", None)
            actions = [a for a in _parse_actions_json(raw or "") if a.get("accion")]
            if actions:
                return actions
        except Exception:
            pass  # degradación a reglas
    # Fallback por reglas. Si el mensaje trae separadores claros (comillas, saltos,
    # " y ", ";"), lo partimos PRIMERO para no tragarnos frases ajenas (bug del
    # "nombre del equipo" que se comía todo). Si no, probamos el mensaje completo.
    chunks = _split_instructions(instruction)
    if len(chunks) > 1:
        out = []
        for chunk in chunks:
            a = _rules_interpret(chunk)
            if a:
                out.append(a)
        if out:
            return out
    whole = _rules_interpret(instruction)
    return [whole] if whole else []


def interpret_instruction(llm, instruction: str, macro: Macrocycle) -> dict:
    """Compat: devuelve una sola acción (la primera interpretada)."""
    acts = interpret_many(llm, instruction, macro)
    return acts[0] if acts else {"accion": ""}


_META_ACTIONS = {"set_team", "set_coach", "set_coordinator", "set_start_date",
                 "add_competition", "set_title"}


def _apply_meta_action(meta: dict, action: dict) -> tuple[dict, str]:
    """Aplica una acción de metadatos sobre una copia de `meta`. (meta, mensaje)."""
    kind = action["accion"]
    meta = dict(meta)
    if kind == "set_title":
        meta["title_override"] = action.get("texto", "").strip()
        return meta, f"Listo: título del macrociclo → «{meta['title_override']}»."
    if kind == "set_team":
        meta["team"] = action.get("texto", "").strip()
        return meta, f"Listo: nombre del equipo → «{meta['team']}»."
    if kind == "set_coach":
        meta["coach"] = action.get("texto", "").strip()
        return meta, f"Listo: entrenador → «{meta['coach']}»."
    if kind == "set_coordinator":
        meta["coordinator"] = action.get("texto", "").strip()
        return meta, f"Listo: coordinador → «{meta['coordinator']}»."
    if kind == "set_start_date":
        meta["start_date"] = action.get("fecha", "")
        from app.planning_service.calendar_map import parse_iso
        d = parse_iso(meta["start_date"])
        pretty = d.strftime("%d/%m/%Y") if d else meta["start_date"]
        return meta, (f"Listo: el macrociclo inicia el {pretty}. "
                      "Ahora la matriz muestra meses y fechas reales.")
    if kind == "add_competition":
        comps = list(meta.get("competitions", []))
        comp = {"fecha": action.get("fecha", ""), "rival": action.get("rival", "")}
        comps.append(comp)
        meta["competitions"] = comps
        from app.planning_service.calendar_map import parse_iso
        d = parse_iso(comp["fecha"])
        pretty = d.strftime("%d/%m/%Y") if d else comp["fecha"]
        extra = f" vs {comp['rival']}" if comp["rival"] else ""
        hint = "" if meta.get("start_date") else (
            " Nota: dime primero la fecha de inicio del macro para ubicarla en la matriz "
            "(ej. «el macro inicia el 10 de agosto de 2026»).")
        return meta, f"Listo: competencia registrada el {pretty}{extra}.{hint}"
    return meta, "Acción de metadatos no reconocida."


def edit_macro_from_text(llm, macro: Macrocycle, instruction: str,
                         meta: dict | None = None) -> tuple[Macrocycle, dict, str]:
    """Interpreta y aplica una o VARIAS instrucciones de un mismo mensaje.

    Devuelve (macro_nuevo, meta_nuevo, mensaje_es). Aplica cada acción en orden
    (las de metadatos tocan meta; las de carga/objetivo tocan el macro) y
    acumula los mensajes de confirmación.
    """
    meta = dict(meta or {})
    actions = [a for a in interpret_many(llm, instruction, macro) if a.get("accion")]
    if not actions:
        return macro, meta, _GENERIC_REPLY
    messages = []
    for action in actions:
        if action.get("accion") in _META_ACTIONS:
            meta, msg = _apply_meta_action(meta, action)
        else:
            macro, msg = apply_action(macro, action)  # incluye 'chat'
        messages.append(msg)
    # Un solo mensaje si fue una acción; lista con viñetas si fueron varias.
    if len(messages) == 1:
        return macro, meta, messages[0]
    return macro, meta, "Hice " + str(len(messages)) + " cambios:\n• " + "\n• ".join(messages)
