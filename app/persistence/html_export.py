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


def _stretch_graphic() -> str:
    """Imagen genérica (SVG) para el bloque de estiramiento / vuelta a la calma."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="420" '
        'viewBox="0 0 1000 420" style="width:100%;max-width:430px;height:auto">'
        '<rect width="1000" height="420" fill="#2e7d32"/>'
        '<rect x="40" y="40" width="920" height="340" fill="#43a047" stroke="#fff" stroke-width="3"/>'
        # cuatro figuras simples de personas estirando
        + "".join(
            f'<g transform="translate({x},210)">'
            '<circle cx="0" cy="-70" r="26" fill="#f4c20d" stroke="#1a2a52" stroke-width="4"/>'
            '<line x1="0" y1="-44" x2="0" y2="30" stroke="#1a2a52" stroke-width="10"/>'
            '<line x1="0" y1="-20" x2="-38" y2="-50" stroke="#1a2a52" stroke-width="9"/>'
            '<line x1="0" y1="-20" x2="38" y2="10" stroke="#1a2a52" stroke-width="9"/>'
            '<line x1="0" y1="30" x2="-30" y2="90" stroke="#1a2a52" stroke-width="9"/>'
            '<line x1="0" y1="30" x2="34" y2="88" stroke="#1a2a52" stroke-width="9"/>'
            '</g>'
            for x in (230, 420, 610, 800)
        )
        + '<text x="500" y="400" font-size="15" fill="#eafbe9" text-anchor="middle" '
        'font-family="sans-serif">Estiramiento / vuelta a la calma</text>'
        '</svg>'
    )


def _inclusivo_html(session: SessionDoc, lang: str = "es") -> str:
    """Hoja de sesión con la plantilla 'Fútbol Inclusivo' (estilo América)."""
    try:
        from app.diagrams import has_drill_data, render_drill
    except Exception:
        has_drill_data = render_drill = None

    obj = session.objective.es if lang == "es" else session.objective.en
    load = session.load_label.es if lang == "es" else session.load_label.en
    # Plantilla inclusiva: cancha base de FÚTBOL PARA CIEGOS (líneas oficiales:
    # vallas, dos áreas, dos porterías, tercios). Si el espacio del ejercicio es
    # reducido, el dibujante ya ajusta; si no, usa la cancha de ciegos de base.
    fmt = getattr(session, "format_id", "")
    pitch_mode = "blind" if fmt in ("", "blind_5") else "auto"

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

        # Diagrama a la derecha: cancha base + flechas tipadas (pase punteada,
        # conducción ondulada, carrera sólida) y jugadores numerados. Equilibrado.
        fase_key = str(b.get("fase", ""))
        diagrama = b.get("diagrama")
        if render_drill and has_drill_data and has_drill_data(diagrama):
            diag_html = render_drill(diagrama, clean=False, pitch=pitch_mode)
        elif fase_key == "vuelta_calma":
            # Estiramientos: imagen genérica (no necesita cancha).
            diag_html = _stretch_graphic()
        else:
            # Bloque sin diagrama: cancha base vacía para que se pueda dibujar a mano.
            diag_html = render_drill({"ancho_m": 40, "alto_m": 20}, clean=False,
                                     pitch=pitch_mode) if render_drill else "—"

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


# --------------------------------------------------------------------------- #
# MACROCICLO como MATRIZ (estilo planilla de Excel / plantilla del usuario).
# Adaptable a cualquier nº de semanas y frecuencia de competencia. RF-6.
# --------------------------------------------------------------------------- #
_PERIOD_ES = {
    "preparatory": "Preparatorio", "competitive": "Competitivo", "transition": "Transitorio",
    "resistance": "Resistencia", "strength": "Fuerza", "speed": "Velocidad", "recovery": "Recuperación",
}
_MESOTYPE_ES = {
    "base": "Base", "development": "Desarrollo", "stabilization": "Estabilización",
    "competitive": "Competitivo", "recovery": "Recuperación",
}
_MICROTYPE_ES = {
    "introductory": "Introductorio", "developmental": "Desarrollador", "shock": "Choque",
    "recovery": "Recuperación", "precompetitive": "Precompetitivo", "competition": "Competencia",
}

# Colores por periodo (banda superior de la matriz).
_PERIOD_COLOR = {
    "preparatory": "#2e7d32", "competitive": "#1565c0", "transition": "#f9a825",
    "resistance": "#2e7d32", "strength": "#6a1b9a", "speed": "#c62828", "recovery": "#00897b",
}

_CSS_MATRIX = """
<style>
  .mtx-wrap { background:#fff; color:#111; padding:16px; overflow-x:auto;
    font-family:'Segoe UI', Arial, sans-serif; position:relative;
    -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .mtx-wrap *, table.mtx td, table.mtx th {
    -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .mtx-wrap > *:not(.mtx-bg) { position:relative; z-index:1; }
  .mtx-wrap::before { content:""; position:absolute; inset:0; z-index:0;
    background:url('/static/escudo-club.png') no-repeat center;
    background-size:min(55%, 520px); opacity:0.08; pointer-events:none; }
  .mtx-title { text-align:center; color:#1f3b73; font-size:20px; font-weight:800; margin:0 0 10px; }
  table.mtx { border-collapse:collapse; width:100%; font-size:11px; }
  table.mtx td, table.mtx th { border:1px solid #9bb0cf; padding:3px 5px; text-align:center;
    vertical-align:middle; }
  .mtx-head td { background:#1f3b73; color:#fff; font-weight:700; }
  .mtx-rowlbl { background:#1f3b73; color:#fff; font-weight:700; text-align:left; width:150px;
    white-space:nowrap; }
  .mtx-sub { background:#cdd8ec; font-weight:700; }
  .mtx-obj td { font-size:10px; text-align:left; vertical-align:top; padding:5px 6px; }
  .mtx-fill { background:#2e7d32; }
  @media print {
    @page { size: landscape; }
    .mtx-wrap { padding:0; overflow:visible; }
    table.mtx { font-size:8px; }
    table.mtx td, table.mtx th { padding:1px 2px; }
  }
</style>
"""

# Capacidades y aspectos que se pintan por microciclo (filas de la matriz).
_CAP_ROWS = [
    ("Resistencia", "#2e7d32"), ("Fuerza", "#c62828"), ("Velocidad", "#f9a825"),
    ("Flexibilidad", "#1565c0"), ("Res. muscular", "#6a1b9a"), ("Potencia", "#00897b"),
    ("Agilidad", "#e67e22"),
]
_ASPECT_ROWS = [
    ("Técnica", "#f9a825"), ("Táctica", "#1565c0"), ("Tiro a gol", "#c62828"),
    ("Espacios reducidos / rondos", "#2e7d32"), ("Juegos simulados", "#f9a825"),
    ("Recreativo", "#8e44ad"), ("Partidos de preparación", "#c62828"),
]


def _vol_band(pct: int, lo: int, hi: int) -> int:
    """Normaliza el volumen del motor [lo..hi] a la escala visual 50..100% y
    devuelve la banda (100,90,...,50) más cercana. Así la rejilla se ve como la
    plantilla (volumen alto arriba al inicio, bajando hacia competencia)."""
    if hi <= lo:
        norm = 75
    else:
        norm = 50 + (pct - lo) / (hi - lo) * 50  # mapea [lo,hi] -> [50,100]
    bands = [100, 90, 80, 70, 60, 50]
    return min(bands, key=lambda b: abs(b - norm))


# Objetivo por defecto según el tipo de mesociclo (si el LLM no dio uno).
_MESO_OBJ_DEFAULT = {
    "base": "Adaptación anatómica y aeróbica: base física, resistencia y confianza.",
    "development": "Desarrollo de fuerza general y específica; estabilidad y control.",
    "stabilization": "Estabilización de cargas; consolidar adaptaciones.",
    "competitive": "Transformar fuerza en potencia y velocidad; forma competitiva.",
    "recovery": "Recuperación y descarga; mantener y cerrar el proceso.",
}


def plan_matrix_html(plan: TrainingPlan, lang: str = "es",
                     team: str = "", coordinator: str = "", coach: str = "",
                     period_label: str = "", start_date: str = "",
                     competitions: list | None = None, category: str = "",
                     days_per_week: int = 0, title_override: str = "") -> str:
    """Matriz de periodización del macrociclo (planilla tipo Excel).

    Se adapta a cualquier nº de semanas / frecuencia de partidos (no asume un
    calendario fijo). Las celdas de volumen y capacidades se pintan según las
    cargas que calculó el motor por microciclo.

    start_date: fecha ISO (YYYY-MM-DD) de la semana 1 -> muestra meses/fechas reales.
    competitions: lista de dicts {"fecha": "YYYY-MM-DD", "rival": "...", "nombre": "..."}
                  -> resalta de arriba a abajo la columna de la semana del partido.
    """
    from app.planning_service import calendar_map as cal

    macro = plan.macro
    micros = sorted(
        [m for meso in macro.mesocycles for m in meso.microcycles],
        key=lambda m: m.week_index,
    )
    n = len(micros)
    if n == 0:
        return '<div class="mtx-wrap"><p>El plan no tiene microciclos.</p></div>'

    base_title = plan.title.es if lang == "es" else plan.title.en
    # Título general: override explícito del usuario > equipo + categoría > título base.
    if title_override:
        title = title_override
    else:
        title = team or base_title
        if category:
            title = f"{title} — Categoría {category}"
    competitions = competitions or []

    # Mapear cada competencia a la semana del macro (si hay fecha de inicio).
    comp_by_week: dict[int, list] = {}
    for comp in competitions:
        d = cal.parse_iso(comp.get("fecha", ""))
        if d is None:
            continue
        wk = cal.week_of_date(start_date, d, n) if start_date else None
        if wk:
            comp_by_week.setdefault(wk, []).append(comp)

    def _comp_cell_style(week: int) -> str:
        """Si la semana tiene competencia, resalta la columna (rojo tenue)."""
        return ' style="box-shadow:inset 0 0 0 2px #c62828"' if week in comp_by_week else ""

    # --- Fila de PERIODO (colspan por nº de semanas de cada periodo)
    def _weeks_in(p):
        return [m for m in micros if p.start_week <= m.week_index <= p.end_week]

    period_cells = []
    for p in macro.periods:
        span = len(_weeks_in(p))
        if span == 0:
            continue
        col = _PERIOD_COLOR.get(p.kind.value, "#555")
        name = _PERIOD_ES.get(p.kind.value, p.kind.value)
        period_cells.append(
            f'<td colspan="{span}" style="background:{col};color:#fff;font-weight:700">{name}</td>'
        )

    # --- Fila de MESOCICLO (colspan por nº de semanas de cada meso)
    meso_cells = []
    for i, meso in enumerate(macro.mesocycles, start=1):
        span = len(meso.microcycles)
        if span == 0:
            continue
        mt = _MESOTYPE_ES.get(meso.type.value, meso.type.value)
        meso_cells.append(f'<td colspan="{span}" class="mtx-sub">Meso {i} · {mt}</td>')

    # --- Fila de MES (agrupada por meses consecutivos) si hay fecha de inicio
    month_row = ""
    if start_date:
        month_cells = []
        i = 0
        while i < n:
            mon = cal.month_label(start_date, micros[i].week_index)
            j = i
            while j + 1 < n and cal.month_label(start_date, micros[j + 1].week_index) == mon:
                j += 1
            span = j - i + 1
            month_cells.append(f'<td colspan="{span}" class="mtx-sub">{mon}</td>')
            i = j + 1
        month_row = f'<tr><td class="mtx-rowlbl">MES</td>{"".join(month_cells)}</tr>'

    # --- Filas de microciclo / fecha / semana / partidos
    micro_hdr = "".join(
        f'<td class="mtx-sub"{_comp_cell_style(m.week_index)}>M{m.week_index}</td>' for m in micros
    )
    week_hdr = "".join(f'<td>{m.week_index}</td>' for m in micros)
    date_row = ""
    if start_date:
        date_cells = "".join(
            f'<td style="font-size:9px">{cal.week_label(start_date, m.week_index)}</td>'
            for m in micros
        )
        date_row = f'<tr><td class="mtx-rowlbl">FECHA</td>{date_cells}</tr>'
    match_hdr = "".join(
        f'<td>{"●"*m.matches_this_week if m.matches_this_week else "-"}</td>' for m in micros
    )

    # --- Fila de SESIONES: numeración consecutiva de sesiones por microciclo
    # (como la plantilla: bajo cada micro van sus sesiones 1..N correlativas).
    sess_cells = []
    counter = 1
    for m in micros:
        n_sess = len(m.session_slots) if m.session_slots else 0
        if n_sess <= 0:
            # si el motor no trae slots, usar los días/semana que dio el usuario
            n_sess = days_per_week if days_per_week and days_per_week > 0 else 3
        ini = counter
        fin = counter + n_sess - 1
        counter = fin + 1
        rango = f"{ini}" if ini == fin else f"{ini}–{fin}"
        sess_cells.append(f'<td style="font-size:9px">{rango}</td>')
    sess_row = f'<tr><td class="mtx-rowlbl">SESIONES</td>{"".join(sess_cells)}</tr>'

    # --- Fila de COMPETENCIA: cruza (resalta) la columna de la semana del partido
    comp_row = ""
    if comp_by_week:
        comp_cells = []
        for m in micros:
            comps = comp_by_week.get(m.week_index)
            if comps:
                label = " / ".join(
                    (c.get("rival") or c.get("nombre") or "Partido") for c in comps
                )
                comp_cells.append(
                    f'<td style="background:#c62828;color:#fff;font-weight:700;font-size:9px">'
                    f'⚽ {_esc(label)}</td>'
                )
            else:
                comp_cells.append('<td>&nbsp;</td>')
        comp_row = f'<tr><td class="mtx-rowlbl">COMPETENCIA</td>{"".join(comp_cells)}</tr>'

    rows = []
    rows.append(f'<tr class="mtx-head"><td class="mtx-rowlbl">PERIODO</td>{"".join(period_cells)}</tr>')
    rows.append(f'<tr><td class="mtx-rowlbl">MESOCICLO</td>{"".join(meso_cells)}</tr>')
    if month_row:
        rows.append(month_row)
    rows.append(f'<tr><td class="mtx-rowlbl">MICROCICLO</td>{micro_hdr}</tr>')
    if date_row:
        rows.append(date_row)
    rows.append(f'<tr><td class="mtx-rowlbl">Semana</td>{week_hdr}</tr>')
    rows.append(sess_row)
    if comp_row:
        rows.append(comp_row)
    rows.append(f'<tr><td class="mtx-rowlbl">Partidos</td>{match_hdr}</tr>')

    # --- Rejilla de VOLUMEN (100% -> 50%); normalizada al rango real del motor
    vols = [m.target_volume_pct for m in micros]
    vlo, vhi = min(vols), max(vols)
    for band in (100, 90, 80, 70, 60, 50):
        cells = []
        for m in micros:
            on = _vol_band(m.target_volume_pct, vlo, vhi) == band
            cells.append('<td class="mtx-fill">&nbsp;</td>' if on else '<td>&nbsp;</td>')
        lbl = "Volumen" if band == 100 else "&nbsp;"
        rows.append(f'<tr><td class="mtx-rowlbl">{lbl} {band}%</td>{"".join(cells)}</tr>')

    # --- Rejilla de CAPACIDADES (se pinta según la intensidad del micro)
    def _cap_on(m, idx, total):
        # Heurística: a mayor intensidad del micro, más capacidades activas.
        active = max(1, round(m.target_intensity_pct / 100 * total))
        return idx < active

    for idx, (name, color) in enumerate(_CAP_ROWS):
        cells = []
        for m in micros:
            on = _cap_on(m, idx, len(_CAP_ROWS))
            cells.append(f'<td style="background:{color}">&nbsp;</td>' if on else '<td>&nbsp;</td>')
        rows.append(f'<tr><td class="mtx-rowlbl">{name}</td>{"".join(cells)}</tr>')

    # --- Rejilla de ASPECTOS técnico-tácticos (pintado por tipo de microciclo)
    def _aspect_on(m, idx):
        t = m.type.value
        # introductorio/desarrollador -> más técnica/espacios; competencia -> partidos/tiro
        if t in ("introductory", "developmental"):
            return idx in (0, 1, 3, 4)
        if t in ("shock", "precompetitive"):
            return idx in (1, 2, 3, 6)
        if t == "competition":
            return idx in (2, 4, 6)
        if t == "recovery":
            return idx in (5,)
        return idx in (0, 3)

    for idx, (name, color) in enumerate(_ASPECT_ROWS):
        cells = []
        for m in micros:
            on = _aspect_on(m, idx)
            cells.append(f'<td style="background:{color}">&nbsp;</td>' if on else '<td>&nbsp;</td>')
        rows.append(f'<tr><td class="mtx-rowlbl">{name}</td>{"".join(cells)}</tr>')

    # --- Encabezado (equipo/categoría · coordinador · entrenador · periodo)
    equipo_cat = _esc(team)
    if category:
        equipo_cat = (equipo_cat + " — " if equipo_cat else "") + "Categoría " + _esc(category)
    hdr = (
        '<table class="mtx" style="margin-bottom:8px">'
        f'<tr><td class="mtx-rowlbl">EQUIPO / CATEGORÍA</td><td style="text-align:left">{equipo_cat or "&nbsp;"}</td></tr>'
        f'<tr><td class="mtx-rowlbl">COORDINADOR</td><td style="text-align:left">{_esc(coordinator) or "&nbsp;"}</td></tr>'
        f'<tr><td class="mtx-rowlbl">ENTRENADOR</td><td style="text-align:left">{_esc(coach) or "&nbsp;"}</td></tr>'
        f'<tr><td class="mtx-rowlbl">PERIODO</td><td style="text-align:left">{_esc(period_label) or "&nbsp;"}</td></tr>'
        '</table>'
    )

    # --- Objetivos por mesociclo (fila de texto largo, como la plantilla)
    obj_cells = []
    for meso in macro.mesocycles:
        span = len(meso.microcycles)
        if span == 0:
            continue
        txt = (" · ".join(meso.objective_focus) if meso.objective_focus
               else _MESO_OBJ_DEFAULT.get(meso.type.value, "Objetivo del mesociclo."))
        obj_cells.append(f'<td colspan="{span}" style="text-align:left;font-size:10px">{_esc(txt)}</td>')
    obj_row = (f'<table class="mtx mtx-obj" style="margin-top:8px">'
               f'<tr><td class="mtx-rowlbl">OBJETIVO</td>{"".join(obj_cells)}</tr></table>')

    body = (
        f'<div class="mtx-title">{_esc(title)}</div>'
        f'{hdr}'
        f'<table class="mtx">{"".join(rows)}</table>'
        f'{obj_row}'
    )
    return f'<div class="mtx-wrap">{_CSS_MATRIX}{body}</div>'


def to_html_plan_matrix(plan: TrainingPlan, lang: str = "es", **meta) -> str:
    """Documento HTML completo con la matriz del macrociclo (imprimible apaisado)."""
    title = _esc(plan.title.es if lang == "es" else plan.title.en)
    body = plan_matrix_html(plan, lang, **meta)
    return (
        f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{title}</title></head><body>{body}</body></html>"
    )
