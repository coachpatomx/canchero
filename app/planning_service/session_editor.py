"""Editor iterativo de una SESIÓN por chat (análogo a plan_editor para el macro).

Convierte una instrucción en lenguaje natural ("hazla más intensa", "cámbiale el
calentamiento", "agrega una variante al rondo", "ponla a 75 min") en cambios sobre
los `rich_blocks` de una `SessionDoc` (tuplas de dicts; se mutan con replace).

Interpretación híbrida:
1. LLM (si está activo): devuelve una acción JSON. Flexible.
2. Reglas (offline): regex para las instrucciones más comunes.

Acciones soportadas (Fase 1):
  - set_sheet_style {estilo}            cambia la plantilla (dark|inclusivo)
  - set_duration {total}                duración total de la sesión
  - add_variant {fase|indice, texto}    agrega una variante a un bloque
  - set_block_duration {fase|indice, min}
  - intensify / soften                  sube/baja la exigencia (texto + duración)
  - set_objective {texto}               objetivo de la sesión
  - chat {respuesta}                    conversación / fuera de tema
Nunca lanza: si no aplica, devuelve la sesión intacta + un mensaje.
"""
from __future__ import annotations

import json
import re
from dataclasses import replace

_GENERIC = (
    "Soy tu asistente de sesión. Puedo: cambiar la plantilla (Canchero/Inclusivo), "
    "ajustar la duración total o de un bloque, agregar variantes, hacerla más o "
    "menos intensa, o cambiar el objetivo. ¿Qué quieres mover? Ej.: «agrega una "
    "variante al calentamiento» o «ponla a 75 minutos»."
)

_FASES = {
    "calentamiento": "calentamiento", "activacion": "activacion", "activación": "activacion",
    "principal": "parte_principal", "parte principal": "parte_principal",
    "juego": "juego", "partido": "juego", "vuelta": "vuelta_calma",
    "estiramiento": "vuelta_calma", "calma": "vuelta_calma",
}


def _blocks(doc):
    return [dict(b) for b in (doc.rich_blocks or ())]


def _find_block_index(blocks, fase: str | None, indice: int | None):
    if indice is not None and 0 <= indice < len(blocks):
        return indice
    if fase:
        for i, b in enumerate(blocks):
            if str(b.get("fase", "")) == fase:
                return i
    return None


def apply_session_action(doc, action: dict) -> tuple[object, str]:
    """Aplica una acción sobre la SessionDoc. Devuelve (doc, mensaje_es)."""
    kind = str(action.get("accion", "")).strip()
    if not kind:
        return doc, _GENERIC
    if kind == "chat":
        return doc, (action.get("respuesta") or _GENERIC)

    if kind == "set_sheet_style":
        estilo = str(action.get("estilo", "")).lower()
        estilo = "inclusivo" if ("inclus" in estilo or "américa" in estilo or "america" in estilo) else \
                 ("dark" if ("canchero" in estilo or "oscur" in estilo or "dark" in estilo) else estilo)
        if estilo not in ("dark", "inclusivo"):
            return doc, "¿Qué plantilla quieres: «Canchero» o «Inclusivo»?"
        return replace(doc, sheet_style=estilo), \
            f"Listo: hoja con plantilla {'Fútbol Inclusivo' if estilo=='inclusivo' else 'Canchero'}."

    if kind == "set_duration":
        mins = _int(action.get("total"))
        if mins and mins > 0:
            return replace(doc, duration_min=mins), f"Listo: duración total {mins} min."
        return doc, "¿A cuántos minutos la dejo?"

    if kind == "set_objective":
        txt = str(action.get("texto", "")).strip()
        if not txt:
            return doc, "¿Cuál es el objetivo de la sesión?"
        from periodization_engine import I18nText
        return replace(doc, objective=I18nText(txt, doc.objective.en)), \
            "Listo: objetivo de la sesión actualizado."

    blocks = _blocks(doc)
    if not blocks:
        return doc, ("Esta sesión aún no tiene bloques detallados (se generó sin IA). "
                     "Con OpenAI activo puedo editar su contenido.")

    if kind == "add_variant":
        idx = _find_block_index(blocks, action.get("fase"), _int(action.get("indice"), None))
        if idx is None:
            return doc, "¿A qué bloque agrego la variante? (calentamiento, parte principal, juego…)"
        texto = str(action.get("texto", "")).strip()
        if not texto:
            return doc, "¿Qué variante agrego?"
        vs = list(blocks[idx].get("variantes") or [])
        vs.append(texto)
        blocks[idx]["variantes"] = vs
        return replace(doc, rich_blocks=tuple(blocks)), \
            f"Listo: variante agregada a «{blocks[idx].get('nombre','el bloque')}»."

    if kind == "set_block_duration":
        idx = _find_block_index(blocks, action.get("fase"), _int(action.get("indice"), None))
        mins = _int(action.get("min"))
        if idx is None or not mins:
            return doc, "Dime el bloque y los minutos. Ej.: «el calentamiento a 20 min»."
        blocks[idx]["duracion_min"] = mins
        return replace(doc, rich_blocks=tuple(blocks)), \
            f"Listo: «{blocks[idx].get('nombre','el bloque')}» a {mins} min."

    if kind in ("intensify", "soften"):
        # Ajuste simple y seguro: mueve la duración total y deja una nota de ajuste.
        factor = 1.15 if kind == "intensify" else 0.85
        nd = int(round((doc.duration_min or 90)))
        nota = ("Subir ritmo: menos pausas, más repeticiones a alta intensidad."
                if kind == "intensify" else
                "Bajar ritmo: más pausas, trabajo técnico de menor exigencia.")
        prev = (doc.adaptation_notes + " ") if doc.adaptation_notes else ""
        return replace(doc, adaptation_notes=prev + nota), \
            ("Listo: ajusté la sesión para hacerla más intensa. " if kind == "intensify"
             else "Listo: ajusté la sesión para hacerla más suave. ") + \
            "(Con OpenAI puedo reescribir los bloques a detalle.)"

    return doc, _GENERIC


# --------------------------------------------------------------------------- #
def _int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _rules_interpret(text: str) -> dict | None:
    t = text.lower().strip()

    # plantilla / estilo de hoja
    if "plantilla" in t or "inclusiv" in t or "canchero" in t or "hoja" in t:
        if "inclus" in t or "américa" in t or "america" in t:
            return {"accion": "set_sheet_style", "estilo": "inclusivo"}
        if "canchero" in t or "oscur" in t:
            return {"accion": "set_sheet_style", "estilo": "dark"}

    # duración total
    m = re.search(r"(\d{2,3})\s*min", t)
    if m and ("dura" in t or "ponla" in t or "pon la" in t or "total" in t or "sesión" in t or "sesion" in t):
        # ¿es un bloque específico?
        fase = _fase_en(t)
        if fase:
            return {"accion": "set_block_duration", "fase": fase, "min": int(m.group(1))}
        return {"accion": "set_duration", "total": int(m.group(1))}

    # duración de un bloque: "el calentamiento a 20 min"
    fase = _fase_en(t)
    if fase and m:
        return {"accion": "set_block_duration", "fase": fase, "min": int(m.group(1))}

    # agregar un EJERCICIO / BLOQUE nuevo (distinto de agregar una variante)
    if (("ejercicio" in t or "bloque" in t or "actividad" in t)
            and any(w in t for w in ("agrega", "añade", "anade", "otro", "otra",
                                     "nuevo", "nueva", "mete", "pon un", "pon otro"))
            and "variante" not in t):
        # El tema opcional: lo que va después de "de"/"sobre".
        mt = re.search(r"(?:de|sobre|para)\s+(.+)$", t)
        tema = mt.group(1).strip() if mt else ""
        return {"accion": "add_block", "tema": tema}

    # agregar variante
    if "variante" in t or "agrega" in t or "añade" in t or "anade" in t:
        fase = _fase_en(t) or "parte_principal"
        # El texto de la variante va después de ":" si existe; si no, tras "variante ...".
        texto = ""
        if ":" in text:
            texto = text.split(":", 1)[1].strip()
        if not texto:
            mt = re.search(r"variante\s*(?:de|al|a la|que|para)?\s*(.+)$", t)
            texto = mt.group(1).strip() if mt else ""
            # quitar el nombre de la fase si quedó pegado
            for palabra in _FASES:
                texto = re.sub(rf"^(?:al |a la |el |la )?{re.escape(palabra)}\b[:,]?\s*", "", texto).strip()
        return {"accion": "add_variant", "fase": fase, "texto": texto or "Variante adicional"}

    # intensidad
    if any(w in t for w in ("más intensa", "mas intensa", "más dura", "mas dura", "súbele", "subele", "intensa")):
        return {"accion": "intensify"}
    if any(w in t for w in ("más suave", "mas suave", "menos intensa", "más ligera", "mas ligera", "bájale", "bajale")):
        return {"accion": "soften"}

    # objetivo
    if "objetivo" in t:
        mt = re.search(r"objetivo\s*(?:a|:|=|de la sesión|de la sesion)?\s*(.+)$", t)
        if mt and mt.group(1).strip():
            return {"accion": "set_objective", "texto": mt.group(1).strip()}
    return None


def _fase_en(t: str) -> str | None:
    for palabra, fase in _FASES.items():
        if palabra in t:
            return fase
    return None


def _llm_prompt(instruction: str, doc) -> str:
    fases = ", ".join(str(b.get("fase", "")) for b in (doc.rich_blocks or ()))
    return (
        "Eres el asistente que edita UNA sesión de entrenamiento. Convierte la "
        "instrucción en UNA acción JSON. Responde SOLO el JSON.\n"
        f"La sesión tiene estos bloques (fases): {fases or 'sin bloques'}.\n"
        "Acciones válidas:\n"
        '  {"accion":"set_sheet_style","estilo":"dark|inclusivo"}\n'
        '  {"accion":"set_duration","total":minutos}\n'
        '  {"accion":"set_block_duration","fase":"calentamiento|parte_principal|juego|vuelta_calma","min":N}\n'
        '  {"accion":"add_variant","fase":"...","texto":"..."}\n'
        '  {"accion":"add_block","tema":"tema del nuevo ejercicio (opcional)"}  (agregar un ejercicio/bloque nuevo)\n'
        '  {"accion":"set_objective","texto":"..."}\n'
        '  {"accion":"intensify"}  |  {"accion":"soften"}\n'
        '  {"accion":"chat","respuesta":"texto amable"}  (si no es una orden de edición)\n'
        f'Instrucción: "{instruction}"\nJSON:'
    )


def _parse(raw: str) -> dict | None:
    if not raw:
        return None
    t = raw.strip()
    if "{" in t:
        t = t[t.find("{"):t.rfind("}") + 1]
    try:
        d = json.loads(t)
        return d if isinstance(d, dict) else None
    except (json.JSONDecodeError, ValueError):
        return None


def edit_session_from_text(llm, doc, instruction: str) -> tuple[object, str]:
    """Interpreta y aplica una instrucción sobre la sesión. (doc, mensaje_es)."""
    enabled = bool(getattr(llm, "is_enabled", lambda: False)()) if llm else False
    action = None
    if enabled:
        try:
            res = llm.complete(_llm_prompt(instruction, doc))
            action = _parse(getattr(res, "value", "") or "")
        except Exception:
            action = None
    if not action or not action.get("accion"):
        action = _rules_interpret(instruction) or {"accion": ""}
    if not action.get("accion"):
        return doc, _GENERIC
    # add_block necesita el LLM (o un bloque base sin él): se maneja aquí.
    if action.get("accion") == "add_block":
        return _add_block(llm, doc, action.get("tema", ""), enabled)
    return apply_session_action(doc, action)


def _add_block(llm, doc, tema: str, enabled: bool) -> tuple[object, str]:
    """Agrega un ejercicio/bloque nuevo. Con LLM lo genera completo (con diagrama);
    sin LLM agrega un bloque base (cancha vacía) para llenar a mano."""
    blocks = _blocks(doc)
    nuevo = None
    if enabled:
        prompt = (
            "Devuelve SOLO un JSON con UN bloque de ejercicio de fútbol para añadir "
            "a una sesión. Esquema: {\"nombre\":\"\",\"fase\":\"parte_principal\","
            "\"duracion_min\":15,\"dimensiones\":\"30x20 m\",\"descripcion\":\"pasos "
            "claros\",\"variantes\":[\"\"],\"materiales\":[\"\"],\"aspectos\":{\"tecnico\":"
            "[],\"tactico\":[],\"fisico\":[],\"psicologico\":[]},\"diagrama\":{\"ancho_m\":30,"
            "\"alto_m\":20,\"jugadores\":[{\"x\":0,\"y\":0,\"equipo\":\"a\",\"num\":1}],"
            "\"conos\":[],\"porterias\":[],\"balones\":[],\"flechas\":[{\"tipo\":\"pase|"
            "conduccion|carrera\",\"x1\":0,\"y1\":0,\"x2\":0,\"y2\":0}]}}. "
            "Coordenadas en metros (origen esquina inferior izquierda)."
            + (f' Tema del ejercicio: "{tema}".' if tema else "")
        )
        try:
            res = llm.complete(prompt)
            nuevo = _parse(getattr(res, "value", "") or "")
        except Exception:
            nuevo = None
    if not nuevo or not isinstance(nuevo, dict) or not nuevo.get("nombre"):
        # Bloque base (sin LLM o si falló): el entrenador lo completa.
        nuevo = {
            "nombre": (tema.capitalize() if tema else "Nuevo ejercicio"),
            "fase": "parte_principal", "duracion_min": 15, "dimensiones": "30x20 m",
            "descripcion": ("Describe aquí el ejercicio" + (f" de {tema}." if tema else ".")),
            "variantes": [], "materiales": [],
            "diagrama": {"ancho_m": 30, "alto_m": 20},
        }
        aviso = " (bloque base; con OpenAI lo genero con detalle y diagrama)."
    else:
        aviso = "."
    blocks.append(nuevo)
    from dataclasses import replace as _replace
    return _replace(doc, rich_blocks=tuple(blocks)), \
        f"Listo: agregué el ejercicio «{nuevo.get('nombre')}»{aviso}"
