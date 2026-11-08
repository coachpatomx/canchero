"""Exportador HTML imprimible (base, sin dependencias) — RF-6, D6.

Maqueta de la plantilla mejorada: encabezado, tareas con diagrama, materiales,
cargas/volumen, aspectos, objetivos individuales. CSS @media print para que
"Imprimir -> Guardar como PDF" del navegador produzca un PDF limpio.
"""
from __future__ import annotations

from .plan import SessionDoc, TrainingPlan


def _esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


_CSS = """
<style>
  .sheet { background:#fff; color:#111; border-radius:12px; padding:24px;
           font-family: 'Segoe UI', sans-serif; }
  .sheet ul { margin: 4px 0 4px 18px; }
  body { font-family: sans-serif; color: #111; margin: 24px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  h2 { font-size: 16px; margin: 18px 0 6px; border-bottom: 2px solid #2e7d32; }
  .meta { display: flex; flex-wrap: wrap; gap: 8px 24px; font-size: 13px; color: #333; }
  .meta b { color: #111; }
  .task { border: 1px solid #ccc; border-radius: 6px; padding: 10px; margin: 10px 0; }
  .task-head { font-weight: bold; font-size: 15px; }
  .task-meta { font-size: 12px; color: #555; margin: 2px 0 6px; }
  /* Layout de 2 columnas: info a la izquierda, diagrama a la derecha. */
  .task-cols { display: flex; gap: 18px; align-items: flex-start; }
  .task-info { flex: 1 1 55%; min-width: 0; }
  .task-diagram { flex: 0 0 42%; max-width: 440px; }
  .task-diagram svg { width: 100%; max-width: 440px; height: auto; border: 1px solid #ddd; }
  .diagram svg { max-width: 420px; height: auto; border: 1px solid #ddd; }
  .aspects { display: flex; gap: 16px; font-size: 12px; flex-wrap: wrap; margin-top: 8px; }
  .aspects div { flex: 1; min-width: 120px; }
  table { border-collapse: collapse; font-size: 12px; }
  td, th { border: 1px solid #ccc; padding: 3px 6px; }
  /* En pantallas angostas (móvil) se apila: info arriba, diagrama abajo. */
  @media (max-width: 640px) {
    .task-cols { flex-direction: column; }
    .task-diagram { flex-basis: auto; max-width: 100%; }
  }
  @media print { body { margin: 0; } .task { page-break-inside: avoid; } }
</style>
"""


def _label(es: str, en: str, lang: str) -> str:
    return es if lang == "es" else en


def _rich_blocks_html(session: SessionDoc, lang: str) -> str:
    """Render de una sesión rica generada por LLM (bloques profesionales)."""
    phase_label = {
        "calentamiento": "Calentamiento", "activacion": "Activación",
        "parte_principal": "Parte principal", "juego": "Juego / Partido condicionado",
        "vuelta_calma": "Vuelta a la calma",
    }
    # Dibujante de diagramas (import una sola vez, reutilizado por bloque).
    try:
        from app.diagrams import has_drill_data, render_drill
    except Exception:  # pragma: no cover - fallback si el módulo no está
        has_drill_data = None
        render_drill = None

    out = []
    for i, b in enumerate(session.rich_blocks, start=1):
        fase = phase_label.get(str(b.get("fase", "")), str(b.get("fase", "")))
        out.append('<div class="task">')
        out.append(
            f'<div class="task-head">{i}. {_esc(str(b.get("nombre","")))} '
            f'<span style="color:#2e7d32">({_esc(fase)})</span></div>'
        )
        meta = []
        if b.get("duracion_min"):
            meta.append(f'{b.get("duracion_min")} min')
        if b.get("dimensiones"):
            meta.append(_esc(str(b.get("dimensiones"))))
        if meta:
            out.append(f'<div class="task-meta">{" · ".join(meta)}</div>')

        # ---- Columna izquierda: información del ejercicio ----
        info = []
        info.append(f'<div>{_esc(str(b.get("descripcion","")))}</div>')
        variantes = b.get("variantes") or []
        if variantes:
            items = "".join(f"<li>{_esc(str(v))}</li>" for v in variantes)
            info.append(f'<div><b>Variantes:</b><ul>{items}</ul></div>')
        mats = b.get("materiales") or []
        if mats:
            info.append(f'<div><b>Materiales:</b> {_esc(", ".join(str(m) for m in mats))}</div>')
        asp = b.get("aspectos") or {}
        if asp:
            aspects = ['<div class="aspects">']
            for key, titulo in (("tecnico", "Técnico"), ("tactico", "Táctico"),
                                ("fisico", "Físico"), ("psicologico", "Psicológico")):
                vals = asp.get(key) or []
                aspects.append(
                    f'<div><b>{titulo}</b><br>{_esc(", ".join(str(x) for x in vals) or "-")}</div>'
                )
            aspects.append("</div>")
            info.append("".join(aspects))

        # ---- Columna derecha: diagrama dibujado desde los datos de la IA ----
        diagram_html = ""
        diagrama = b.get("diagrama")
        if render_drill and has_drill_data and has_drill_data(diagrama):
            diagram_html = render_drill(diagrama)

        # ---- Armado de las 2 columnas ----
        out.append('<div class="task-cols">')
        out.append(f'<div class="task-info">{"".join(info)}</div>')
        if diagram_html:
            out.append(f'<div class="task-diagram">{diagram_html}</div>')
        out.append("</div>")

        out.append("</div>")
    if session.adaptation_notes:
        out.append(f'<div class="task"><b>Notas de adaptación:</b> {_esc(session.adaptation_notes)}</div>')
    return "\n".join(out)


def _session_body(session: SessionDoc, lang: str) -> str:
    obj = session.objective.es if lang == "es" else session.objective.en
    load = session.load_label.es if lang == "es" else session.load_label.en
    out = [
        f"<h1>{_esc(obj)}</h1>",
    ]
    if session.objective_specific:
        out.append(f'<p class="muted">{_esc(session.objective_specific)}</p>')
    out += [
        '<div class="meta">',
        f"<span><b>{_label('Semana','Week',lang)}:</b> {session.week_index}</span>",
        f"<span><b>{_label('Mesociclo','Mesocycle',lang)}:</b> {session.meso_index+1}</span>",
        f"<span><b>{_label('Microciclo','Microcycle',lang)}:</b> {session.micro_index+1}</span>",
        f"<span><b>{_label('Carga','Load',lang)}:</b> {_esc(load)}</span>",
    ]
    if session.duration_min:
        out.append(f"<span><b>Duración:</b> {session.duration_min} min</span>")
    if session.category:
        out.append(f"<span><b>Categoría:</b> {_esc(session.category)}</span>")
    out.append(f"<span><b>{_label('Fecha','Date',lang)}:</b> {_esc(session.date or '-')}</span>")
    out.append("</div>")

    # Si hay sesión rica (LLM), se renderiza esa; si no, las tareas deterministas.
    if session.rich_blocks:
        out.append(f"<h2>{_label('Desarrollo de la sesión','Session plan',lang)}</h2>")
        out.append(_rich_blocks_html(session, lang))
        # Nota: los diagramas van DENTRO de cada bloque (render_drill). Ya no se
        # muestra el diagrama genérico al final para sesiones ricas.
        if session.individual_goals:
            out.append(f"<h2>{_label('Objetivos individuales','Individual goals',lang)}</h2>")
            out.append("<table><tr>"
                       f"<th>{_label('Jugador','Player',lang)}</th>"
                       f"<th>{_label('Objetivo','Goal',lang)}</th></tr>")
            for g in session.individual_goals:
                out.append(f"<tr><td>{_esc(str(g.get('player','')))}</td>"
                           f"<td>{_esc(str(g.get('goal','')))}</td></tr>")
            out.append("</table>")
        return "\n".join(out)

    out.append(f"<h2>{_label('Tareas','Tasks',lang)}</h2>")
    for i, ex in enumerate(session.exercises):
        name = ex.name.es if lang == "es" else ex.name.en
        desc = ex.objective.es if lang == "es" else ex.objective.en
        mats = ", ".join((m.name.es if lang == "es" else m.name.en) for m in ex.materials) or "-"
        svg = session.svgs[i] if i < len(session.svgs) else ""
        out.append('<div class="task">')
        out.append(f'<div class="task-head">{i+1}. {_esc(name)}</div>')
        out.append(
            f'<div class="task-meta">{ex.task_type.value} · {ex.didactic_strategy.value} · '
            f'{ex.duration_min} min · {ex.space.length_m:.0f}x{ex.space.width_m:.0f} · '
            f'{_label("carga","load",lang)} v{ex.load.volume_pct}/i{ex.load.intensity_pct}</div>'
        )
        out.append(f"<div>{_esc(desc)}</div>")
        out.append(f'<div><b>{_label("Materiales","Materials",lang)}:</b> {_esc(mats)}</div>')
        a = ex.aspects
        out.append('<div class="aspects">')
        out.append(f'<div><b>{_label("Técnico","Technical",lang)}</b><br>{_esc(", ".join(a.technical) or "-")}</div>')
        out.append(f'<div><b>{_label("Táctico","Tactical",lang)}</b><br>{_esc(", ".join(a.tactical) or "-")}</div>')
        out.append(f'<div><b>{_label("Físico","Physical",lang)}</b><br>{_esc(", ".join(a.physical) or "-")}</div>')
        out.append(f'<div><b>{_label("Psicológico","Psychological",lang)}</b><br>{_esc(", ".join(a.psychological) or "-")}</div>')
        out.append("</div>")
        if svg:
            out.append(f'<div class="diagram">{svg}</div>')
        out.append("</div>")

    if session.individual_goals:
        out.append(f"<h2>{_label('Objetivos individuales','Individual goals',lang)}</h2>")
        out.append("<table><tr>"
                   f"<th>{_label('Jugador','Player',lang)}</th>"
                   f"<th>{_label('Objetivo','Goal',lang)}</th></tr>")
        for g in session.individual_goals:
            out.append(f"<tr><td>{_esc(str(g.get('player','')))}</td>"
                       f"<td>{_esc(str(g.get('goal','')))}</td></tr>")
        out.append("</table>")
    return "\n".join(out)


# --------------------------------------------------------------------------- #
# Plantilla "Fútbol Inclusivo" (estilo Club América) — uso interno/local.
# Estructura fiel a la hoja del usuario: título azul, tablas de encabezado,
# bandas azules de Meso/Objetivo, fila de objetivo/carga/capacidades/material,
# y cada bloque como fila (texto a la izquierda, "Gráfica" + diagrama a la
# derecha). Fondo con escudo como marca de agua (si existe /static/escudo-inclusivo.png).
# --------------------------------------------------------------------------- #
_AZUL = "#1f3b73"
_AMARILLO = "#eef36a"

_CSS_INCLUSIVO = """
<style>
  .sheet-incl { background:#fff; color:#111; padding:22px;
    font-family:'Segoe UI', Arial, sans-serif; position:relative; }
  .sheet-incl * { position:relative; z-index:1; }
  /* Marca de agua con el escudo (si el archivo existe). */
  .sheet-incl::before {
    content:""; position:absolute; inset:0; z-index:0;
    background-image:url('/static/escudo-inclusivo.png');
    background-repeat:no-repeat; background-position:center;
    background-size:min(70%, 620px); opacity:0.10; pointer-events:none;
  }
  .incl-title { text-align:center; color:#1f3b73; font-size:22px; font-weight:800;
    margin:0 0 14px; letter-spacing:.5px; }
  .incl-table { width:100%; border-collapse:collapse; margin:0 0 12px; font-size:13px; }
  .incl-table td, .incl-table th { border:1px solid #9bb0cf; padding:6px 8px; vertical-align:top; }
  .incl-band { background:#1f3b73; color:#fff; font-weight:700; }
  .incl-key { background:#1f3b73; color:#fff; font-weight:700; width:170px; }
  .incl-yellow { background:#eef36a; font-weight:700; width:100px; text-align:center; }
  .incl-block { width:100%; border-collapse:collapse; margin:14px 0 0; font-size:13px; }
  .incl-block td, .incl-block th { border:1px solid #9bb0cf; padding:8px 10px; vertical-align:top; }
  .incl-block .head { background:#1f3b73; color:#fff; font-weight:700; }
  .incl-block .grafica { background:#cdd8ec; font-weight:700; text-align:center; width:120px; }
  .incl-block .dur { background:#cdd8ec; font-weight:700; width:150px; }
  .incl-left { width:52%; }
  .incl-right { width:48%; text-align:center; background:#2e7d32; }
  .incl-right svg { width:100%; max-width:430px; height:auto; }
  .incl-block ul { margin:6px 0 2px 18px; padding:0; }
  .incl-var { background:#eef36a; font-weight:700; width:90px; text-align:center;
    writing-mode:vertical-rl; transform:rotate(180deg); }
  @media print { .sheet-incl { padding:0; } .incl-block, .incl-table { page-break-inside:avoid; } }
</style>
"""

_PHASE_INCL = {
    "calentamiento": "CALENTAMIENTO", "activacion": "ACTIVACIÓN",
    "parte_principal": "PARTE PRINCIPAL", "juego": "PARTIDO CONDICIONADO",
    "vuelta_calma": "VUELTA A LA CALMA / ESTIRAMIENTO",
}


def _inclusivo_html(session: SessionDoc, lang: str = "es") -> str:
    """Hoja de sesión con la plantilla 'Fútbol Inclusivo' (estilo América)."""
    try:
        from app.diagrams import has_drill_data, render_drill
    except Exception:
        has_drill_data = render_drill = None

    obj = session.objective.es if lang == "es" else session.objective.en
    load = session.load_label.es if lang == "es" else session.load_label.en
    # ¿La modalidad es fútbol para ciegos? -> cancha oficial de ciegos.
    is_blind = (getattr(session, "format_id", "") == "blind_5")
    pitch_mode = "blind" if is_blind else "auto"

    team = _esc(session.team_name or "")
    coach = _esc(session.coach_name or "")
    sched = _esc(session.schedule or "")
    snum = _esc(session.session_number or "")
    cat = _esc(session.category or "")
    dur = f"{session.duration_min} MIN" if session.duration_min else ""

    # Reunir capacidades/aspectos y materiales a partir de los bloques.
    caps, materials = [], []
    for b in session.rich_blocks:
        asp = b.get("aspectos") or {}
        for k in ("fisico", "tecnico", "tactico"):
            for v in (asp.get(k) or []):
                if str(v) not in caps:
                    caps.append(str(v))
        for m in (b.get("materiales") or []):
            if str(m) not in materials:
                materials.append(str(m))
    caps_html = "".join(f"<li>{_esc(c)}</li>" for c in caps[:8]) or "<li>-</li>"
    mats_html = "".join(f"<li>{_esc(m)}</li>" for m in materials[:8]) or "<li>-</li>"

    out = ['<div class="incl-title">PLAN DE SESIÓN FÚTBOL INCLUSIVO</div>']

    # --- Tabla de encabezado (equipo / entrenador / fecha / nº / duración / horario)
    out.append('<table class="incl-table"><tr>'
               f'<td><b>Equipo:</b> {team or "&nbsp;"}</td>'
               f'<td colspan="3"><b>Entrenador(a):</b> {coach or "&nbsp;"}</td></tr>'
               '<tr>'
               f'<td class="incl-band">Fecha</td>'
               f'<td class="incl-band">No. Sesión</td>'
               f'<td class="incl-band">Duración</td>'
               f'<td class="incl-band">Horario</td></tr>'
               '<tr>'
               f'<td>{_esc(session.date or "&nbsp;")}</td>'
               f'<td>{snum or "&nbsp;"}</td>'
               f'<td>{dur or "&nbsp;"}</td>'
               f'<td>{sched or "&nbsp;"}</td></tr></table>')

    # --- Banda Mesociclo / Objetivo + Microciclo
    out.append('<table class="incl-table">'
               f'<tr><td class="incl-band" style="width:170px">Mesociclo: {session.meso_index+1}</td>'
               f'<td class="incl-band">Objetivo</td></tr>'
               f'<tr><td>{cat or "&nbsp;"}</td><td>{_esc(obj)}</td></tr>'
               f'<tr><td class="incl-band">Microciclo: {session.micro_index+1}</td>'
               f'<td>{_esc(session.objective_specific or "&nbsp;")}</td></tr></table>')

    # --- Fila objetivo de sesión / carga / capacidades / aspectos / material
    out.append('<table class="incl-table"><tr>'
               '<td class="incl-band">Objetivo de la sesión</td>'
               '<td class="incl-band">Carga física</td>'
               '<td class="incl-band">Capacidades por trabajar</td>'
               '<td class="incl-band">Material</td></tr>'
               '<tr>'
               f'<td>{_esc(session.objective_specific or obj)}</td>'
               f'<td>{_esc(load)}</td>'
               f'<td><ul>{caps_html}</ul></td>'
               f'<td><ul>{mats_html}</ul></td></tr></table>')

    # --- Un bloque por ejercicio (texto izquierda, gráfica derecha)
    for b in session.rich_blocks:
        fase = _PHASE_INCL.get(str(b.get("fase", "")), str(b.get("nombre", "")).upper())
        nombre = _esc(str(b.get("nombre", "")))
        dmin = b.get("duracion_min")
        dur_txt = f"{dmin} minutos" if dmin else ""

        # Texto de la columna izquierda.
        left = [f'<div><b>{nombre}</b></div>']
        left.append(f'<div>{_esc(str(b.get("descripcion","")))}</div>')
        variantes = b.get("variantes") or []
        if variantes:
            items = "".join(f"<li>{_esc(str(v))}</li>" for v in variantes)
            left.append(f'<div style="margin-top:6px"><b>Variantes:</b><ul>{items}</ul></div>')

        # Diagrama limpio (sin flechas ni números) a la derecha.
        diag_html = ""
        diagrama = b.get("diagrama")
        if render_drill and has_drill_data and has_drill_data(diagrama):
            diag_html = render_drill(diagrama, clean=True, pitch=pitch_mode)
        else:
            diag_html = '<span style="color:#cfe8cf">Gráfica</span>'

        out.append(
            '<table class="incl-block">'
            f'<tr><td class="head" colspan="2">{_esc(fase)}</td>'
            f'<td class="grafica">Gráfica</td>'
            f'<td class="dur"><b>Duración:</b> {dur_txt}</td></tr>'
            '<tr>'
            f'<td class="incl-left" colspan="2">{"".join(left)}</td>'
            f'<td class="incl-right" colspan="2">{diag_html}</td></tr>'
            '</table>'
        )

    if session.adaptation_notes:
        out.append('<table class="incl-block"><tr>'
                   f'<td><b>Notas de adaptación:</b> {_esc(session.adaptation_notes)}</td>'
                   '</tr></table>')

    # Objetivos individuales (si hay)
    if session.individual_goals:
        rows = "".join(
            f"<tr><td>{_esc(str(g.get('player','')))}</td>"
            f"<td>{_esc(str(g.get('goal','')))}</td></tr>"
            for g in session.individual_goals
        )
        out.append('<table class="incl-table" style="margin-top:12px">'
                   '<tr><td class="incl-band">Jugador</td>'
                   '<td class="incl-band">Objetivo individual</td></tr>'
                   f'{rows}</table>')

    return "\n".join(out)


def _resolve_style(session: SessionDoc, style: str) -> str:
    """El estilo explícito gana; si no, el guardado en la sesión; si no, 'dark'."""
    return style or getattr(session, "sheet_style", "") or "dark"


def session_body_html(session: SessionDoc, lang: str = "es", style: str = "") -> str:
    """Solo el contenido de la sesión (sin <html>), envuelto en un panel blanco
    con los estilos de impresión, para incrustar en la app oscura sin que se vea
    todo negro. Imprime bien.

    style: "dark" (Canchero) o "inclusivo" (plantilla tipo Club América)."""
    st = _resolve_style(session, style)
    if st == "inclusivo":
        return f'<div class="sheet-incl">{_CSS_INCLUSIVO}{_inclusivo_html(session, lang)}</div>'
    return f'<div class="sheet">{_CSS}{_session_body(session, lang)}</div>'


def to_html_session(session: SessionDoc, lang: str = "es", style: str = "") -> str:
    st = _resolve_style(session, style)
    title = _esc(session.objective.es if lang == "es" else session.objective.en)
    if st == "inclusivo":
        css = _CSS_INCLUSIVO
        body = f'<div class="sheet-incl">{_inclusivo_html(session, lang)}</div>'
    else:
        css = _CSS
        body = _session_body(session, lang)
    return (
        f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{title}</title>{css}</head><body>{body}</body></html>"
    )


def to_html_plan(plan: TrainingPlan, lang: str = "es") -> str:
    title = plan.title.es if lang == "es" else plan.title.en
    parts = [f"<h1>{_esc(title)}</h1>"]
    for s in plan.sessions:
        parts.append('<div style="page-break-after: always;">')
        parts.append(_session_body(s, lang))
        parts.append("</div>")
    body = "\n".join(parts)
    return (
        f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">'
        f"<title>{_esc(title)}</title>{_CSS}</head><body>{body}</body></html>"
    )
