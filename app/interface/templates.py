"""Render HTML server-side (RF-2, D6). Sin motor de plantillas externo: strings.

Los SVG de U3 se incrustan inline. Bilingüe por parámetro lang. Estilo con una
hoja CSS compartida (paleta de cancha de fútbol) para una UI agradable.
"""
from __future__ import annotations

from app.persistence import to_html_session
from app.planning_service import Alignment


def _t(es: str, en: str, lang: str) -> str:
    return es if lang == "es" else en


# Logo de Canchero incrustado inline (no depende de la ruta /static/).
# A prueba de errores de carga.
_LOGO_SVG = (
    '<svg class="logo" xmlns="http://www.w3.org/2000/svg" width="42" height="56" '
    'viewBox="0 0 200 270" fill="none" aria-label="Canchero">'
    '<path d="M70 58 Q70 14 100 14 Q130 14 130 58" fill="none" stroke="#ff7a1a" stroke-width="12" stroke-linecap="round"/>'
    '<rect x="93" y="54" width="14" height="14" fill="#22c55e"/>'
    '<path d="M52 76 Q52 66 100 66 Q148 66 148 76 L139 190 Q138 204 124 204 L76 204 Q62 204 61 190 Z" fill="#22c55e"/>'
    '<g fill="#0e1116" opacity="0.16"><circle cx="90" cy="168" r="2.7"/><circle cx="100" cy="168" r="2.7"/>'
    '<circle cx="110" cy="168" r="2.7"/><circle cx="95" cy="184" r="2.7"/><circle cx="105" cy="184" r="2.7"/></g>'
    '<ellipse cx="82" cy="112" rx="18" ry="24" fill="#f4f4f0" stroke="#0e1116" stroke-width="3"/>'
    '<ellipse cx="118" cy="112" rx="18" ry="24" fill="#f4f4f0" stroke="#0e1116" stroke-width="3"/>'
    '<ellipse cx="90" cy="114" rx="10" ry="13" fill="#1e2430"/><ellipse cx="110" cy="114" rx="10" ry="13" fill="#1e2430"/>'
    '<circle cx="87" cy="108" r="3.4" fill="#fff"/><circle cx="107" cy="108" r="3.4" fill="#fff"/>'
    '<path d="M88 150 q12 9 24 0" stroke="#f4f4f0" stroke-width="5" fill="none" stroke-linecap="round"/>'
    '<path d="M78 204 L75 242" stroke="#22c55e" stroke-width="7.5" stroke-linecap="round"/>'
    '<path d="M92 204 L90 243" stroke="#22c55e" stroke-width="7.5" stroke-linecap="round"/>'
    '<path d="M108 204 L110 243" stroke="#22c55e" stroke-width="7.5" stroke-linecap="round"/>'
    '<path d="M122 204 L125 242" stroke="#22c55e" stroke-width="7.5" stroke-linecap="round"/>'
    '<rect x="62" y="243" width="76" height="13" rx="5" fill="#ff7a1a"/></svg>'
)


# Hoja de estilos compartida — tema OSCURO (asfalto/pizarrón) verde+naranja.
_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --green:#22c55e; --green-600:#1f9e37; --green-900:#14532d;
    --accent:#ff7a1a; --accent-600:#e65f00;
    --bg:#0e1116; --bg-2:#12161c; --card:#161b22; --line:#242b35;
    --ink:#f4f4f0; --muted:#8a97a3;
    --blue:#3b82f6; --red:#ef4444;
    --font: 'Poppins', 'Segoe UI', system-ui, sans-serif;
  }
  * { box-sizing: border-box; }
  body { font-family: var(--font); color: var(--ink); margin: 0; background: var(--bg); }
  header {
    background: var(--bg-2); color:#fff; padding: 18px 28px;
    display:flex; flex-direction:row; align-items:center; justify-content:flex-start;
    gap:16px; border-bottom:1px solid var(--line);
  }
  header .logo { display:block; height:60px; width:auto; flex:0 0 auto; }
  header > div { display:flex; flex-direction:column; justify-content:center; }
  header h1 { margin: 0; font-size: 28px; font-weight: 800; letter-spacing:.5px; }
  header .muted { font-size: 14px; }
  .wrap { max-width: 920px; margin: 0 auto; padding: 26px; }
  .card {
    background: var(--card); border-radius: 16px; padding: 20px 22px;
    margin: 18px 0; border: 1px solid var(--line);
  }
  .card h2 { margin: 0 0 6px; font-size: 18px; font-weight:800; color: var(--ink); }
  .card h2::after { content:""; display:block; width:56px; height:3px; border-radius:2px;
                    background: var(--green); margin-top:8px; margin-bottom:6px; }
  label { display:block; font-size: 13px; color: var(--muted); margin: 12px 0 4px; }
  input, select {
    width: 100%; padding: 11px 12px; border: 1px solid var(--line); border-radius: 10px;
    font-size: 14px; background:#0e1116; color: var(--ink); font-family: var(--font);
  }
  input::placeholder { color:#5b6670; }
  input:focus, select:focus { outline: 2px solid var(--green); border-color: transparent; }
  .row { display:flex; gap:14px; flex-wrap:wrap; }
  .row > div { flex:1; min-width: 150px; }
  button, .btn {
    margin-top: 16px; background: var(--accent); color:#0e1116; border:none;
    padding: 11px 22px; border-radius: 11px; font-size: 15px; font-weight: 800;
    cursor: pointer; transition: background .15s; text-decoration:none; display:inline-block;
    font-family: var(--font);
  }
  button:hover, .btn:hover { background: var(--accent-600); }
  a.btn { color:#0e1116; }
  .list { list-style:none; padding:0; margin:0; }
  .list > li {
    background:#0e1116; border:1px solid var(--line); border-radius:10px;
    padding:12px 14px; margin:8px 0;
  }
  .pill { display:inline-block; padding:2px 10px; border-radius:999px; font-size:12px;
          font-weight:700; color:#0e1116; }
  .pill.potentiate{background:var(--green);} .pill.improve{background:var(--blue);color:#fff;}
  .pill.eliminate{background:var(--red);color:#fff;}
  .muted { color: var(--muted); font-size: 13px; }
  .back { color: var(--green); font-weight:700; text-decoration:none; }
  .banner { padding:12px 18px; border-radius:11px; color:#fff; font-weight:800; margin-bottom:14px; }
</style>
"""


def _page(title: str, lang: str, body: str, subtitle: str = "") -> str:
    sub = f'<span class="muted" style="color:#d7ead9">{subtitle}</span>' if subtitle else ""
    return f"""<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" type="image/svg+xml" href="/static/canchero.svg">
<title>{title}</title>{_CSS}</head><body>
<header>{_LOGO_SVG}<div><h1>Canchero</h1>{sub}</div></header>
<div class="wrap">{body}</div></body></html>"""


_CATEGORIES = ["", "Sub-13", "Sub-15", "Sub-17", "Sub-19", "Sub-23", "Libre", "Primer equipo"]

# Catálogos de fundamentos para selección múltiple (checkboxes) + texto libre.
_TECNICOS = ["Conducción", "Pase", "Recepción", "Recepción perfilada", "Control orientado",
             "Regate", "Tiro a puerta", "Protección del balón", "Cabeceo", "Centro"]
_TACTICOS = ["Posesión", "Presión", "Transiciones", "Toma de espacios", "Posicionamiento",
             "Repliegue", "Juego de posición", "Salida de balón", "Vigilancias", "Desmarques"]
_FISICOS = ["Resistencia", "Velocidad", "Fuerza", "Agilidad", "Potencia", "Flexibilidad",
            "Coordinación", "Cambio de ritmo", "Arranque", "Resistencia muscular"]


def _checkbox_group(name: str, options: list, columns: int = 3) -> str:
    """Grupo de casillas (selección múltiple) con layout en columnas."""
    items = "".join(
        f'<label style="display:inline-flex;align-items:center;gap:6px;'
        f'font-size:13px;color:var(--ink);margin:0;min-width:33%">'
        f'<input type="checkbox" name="{name}" value="{o}" '
        f'style="width:auto;margin:0"> {o}</label>'
        for o in options
    )
    return (f'<div style="display:flex;flex-wrap:wrap;gap:6px 4px;'
            f'background:#0e1116;border:1px solid var(--line);border-radius:10px;'
            f'padding:10px">{items}</div>')


def render_home(history, models, formats, lang: str = "es", llm_on: bool = False) -> str:
    model_opts = "".join(f'<option value="{m.id}">{m.name.es}</option>' for m in models)
    fmt_opts = "".join(f'<option value="{f.id}">{f.name.es}</option>' for f in formats)
    cat_opts = "".join(f'<option value="{c}">{c or "— sin especificar —"}</option>' for c in _CATEGORIES)
    # Selector de plan para la sesión (vincular a un plan existente).
    plan_opts = '<option value="">— sin plan (sesión suelta) —</option>' + "".join(
        f'<option value="{h.id}">{h.title_es}</option>' for h in history
    )
    rows = "".join(
        f'<li><a class="back" href="/plan/{h.id}"><b>{h.title_es}</b></a> '
        f"<span class='muted'>· {h.model_id} / {h.format_id} · {h.created_at[:10]}</span></li>"
        for h in history
    ) or "<li class='muted'>Aún no hay planes. ¡Crea el primero abajo!</li>"

    llm_badge = ('<span class="muted">✨ IA activa</span>' if llm_on else
                 '<span class="muted">IA desactivada — las sesiones usan estructura base. '
                 'Activa OpenAI/Ollama para sesiones detalladas.</span>')

    body = f"""
<p><a class="btn" href="/roster">👥 Equipo y objetivos</a> &nbsp;
   <a class="btn" href="/sessions">📚 Historial de sesiones</a> &nbsp; {llm_badge}</p>

<div class="card">
  <h2>📋 Historial de planes</h2>
  <ul class="list">{rows}</ul>
</div>

<div class="card">
  <h2>🗓️ Nuevo plan de temporada</h2>
  <form method="get" action="/plan">
    <label>Nombre del plan</label>
    <input name="title" placeholder="Ej. Temporada 2026 Ciegos" required>
    <div class="row">
      <div><label>Semanas</label><input name="duration_weeks" value="20"></div>
      <div><label>Días por semana</label><input name="training_days_per_week" value="4"></div>
      <div><label>Partidos por semana</label><input name="matches_per_week" value="1"></div>
    </div>
    <div class="row">
      <div><label>Modelo de periodización</label><select name="model_id">{model_opts}</select></div>
      <div><label>Formato de fútbol</label><select name="format_id">{fmt_opts}</select></div>
      <div><label>Categoría</label><select name="category">{cat_opts}</select></div>
    </div>
    <button type="submit">⚡ Generar plan</button>
  </form>
</div>

<div class="card">
  <h2>💬 Nueva sesión</h2>
  <p class="muted">Describe la sesión en lenguaje natural y afina con las opciones.
  Entre más contexto des (fundamento, material, categoría), mejor queda. Si hay un
  plan activo, la sesión se alinea a su microciclo de la semana.</p>
  <form method="get" action="/session">
    <label>¿Qué quieres entrenar?</label>
    <input name="text" placeholder="Ej. sesión de conducción y recepción perfilada en espacio reducido con tiro a puerta" required>
    <div class="row">
      <div><label>Vincular a un plan (para alinear cargas)</label>
        <select name="plan_id">{plan_opts}</select></div>
      <div><label>Semana del plan</label><input name="week_index" placeholder="ej. 3"></div>
    </div>
    <div class="row">
      <div><label>Formato</label><select name="format_id">{fmt_opts}</select></div>
      <div><label>Categoría</label><select name="category">{cat_opts}</select></div>
      <div><label>Duración (min)</label><input name="duration_min" value="90"></div>
    </div>
    <div class="row">
      <div><label>Estilo de hoja</label>
        <select name="sheet_style">
          <option value="dark">Canchero (oscuro)</option>
          <option value="inclusivo">Fútbol Inclusivo (plantilla América)</option>
        </select></div>
      <div><label>Nº de jugadores</label><input name="n_players" placeholder="según formato"></div>
      <div><label>Horario</label><input name="schedule" placeholder="matutino / 10:00"></div>
    </div>
    <div class="row">
      <div><label>Equipo (para la hoja inclusiva)</label><input name="team_name" placeholder="Ej. Ciegos y débiles visuales"></div>
      <div><label>Entrenador(a)</label><input name="coach_name" placeholder="nombre del entrenador"></div>
      <div><label>No. de sesión</label><input name="session_number" placeholder="ej. 64"></div>
    </div>
    <label>Fundamentos técnicos (elige los que apliquen)</label>
    {_checkbox_group("technical_focus", _TECNICOS)}
    <input name="technical_focus_extra" placeholder="Otros fundamentos técnicos (separa con comas)">

    <label>Fundamentos tácticos</label>
    {_checkbox_group("tactical_focus", _TACTICOS)}
    <input name="tactical_focus_extra" placeholder="Otros fundamentos tácticos (separa con comas)">

    <label>Capacidades físicas</label>
    {_checkbox_group("physical_focus", _FISICOS)}
    <input name="physical_focus_extra" placeholder="Otras capacidades físicas (separa con comas)">

    <label>Material disponible</label>
    <input name="materials" placeholder="balones, conos, vallas, balón sonoro, mini-porterías...">
    <button type="submit">✨ Generar sesión</button>
  </form>
</div>
"""
    return _page("Canchero", lang, body, "Sí la mueve planificando")


# Traducciones de dominio a español (el motor usa claves inglesas internas).
PERIOD_ES = {
    "preparatory": "Preparatorio", "competitive": "Competitivo", "transition": "Transitorio",
    "resistance": "Resistencia", "strength": "Fuerza", "speed": "Velocidad", "recovery": "Recuperación",
}
STAGE_ES = {
    "general": "General", "special": "Especial", "precompetitive": "Precompetitiva",
    "competitive": "Competitiva", "transition": "Transición",
}
MESOTYPE_ES = {
    "base": "Base", "development": "Desarrollo", "stabilization": "Estabilización",
    "competitive": "Competitivo", "recovery": "Recuperación",
}
MICROTYPE_ES = {
    "introductory": "Introductorio", "developmental": "Desarrollador", "shock": "Choque",
    "recovery": "Recuperación", "precompetitive": "Precompetitivo", "competition": "Competencia",
}
MODEL_ES = {
    "traditional": "Tradicional (Matveyev)", "blocks": "Por bloques (Issurin)", "atr": "ATR",
    "tactical": "Periodización Táctica (Frade)", "structured": "Entrenamiento Estructurado (Seirul·lo)",
    "football_gonzalez": "Esquema A. González (torneos cortos)",
}


def _week_bar(m) -> str:
    vol, inten = m.target_volume_pct, m.target_intensity_pct
    mt = MICROTYPE_ES.get(m.type.value, m.type.value)
    return (
        f'<li><b>Semana {m.week_index}</b> '
        f'<span class="muted">· {mt} · sesiones: {len(m.session_slots)}</span>'
        f'<div style="margin-top:6px">'
        f'<span style="display:inline-block;height:8px;width:{vol}px;max-width:100px;'
        f'background:#3b82f6;border-radius:4px;vertical-align:middle"></span>'
        f'<span class="muted" style="margin:0 10px 0 6px">vol {vol}%</span>'
        f'<span style="display:inline-block;height:8px;width:{inten}px;max-width:100px;'
        f'background:{_load_color(inten)};border-radius:4px;vertical-align:middle"></span>'
        f'<span class="muted" style="margin-left:6px">int {inten}%</span>'
        f'</div></li>'
    )


def render_plan(plan, lang: str = "es", plan_sessions: list | None = None) -> str:
    title = plan.title.es if lang == "es" else plan.title.en
    weeks = len(plan.sessions)
    pcolor = {"preparatory":"#2e7d32","competitive":"#1565c0","transition":"#f9a825",
              "resistance":"#2e7d32","strength":"#6a1b9a","speed":"#c62828","recovery":"#00897b"}

    # Cada período es un desplegable (<details>) que contiene SUS semanas dentro.
    all_micros = [m for meso in plan.macro.mesocycles for m in meso.microcycles]
    period_blocks = []
    for p in plan.macro.periods:
        micros_in = sorted(
            [m for m in all_micros if p.start_week <= m.week_index <= p.end_week],
            key=lambda m: m.week_index,
        )
        weeks_html = "".join(_week_bar(m) for m in micros_in) or \
            '<li class="muted">sin semanas</li>'
        color = pcolor.get(p.kind.value, "#555")
        period_blocks.append(
            f'<details style="margin:10px 0;border:1px solid var(--line);border-radius:12px;'
            f'background:var(--card);padding:6px 14px">'
            f'<summary style="cursor:pointer;list-style:none;padding:8px 0;font-size:15px">'
            f'<span class="pill" style="background:{color}">'
            f'{PERIOD_ES.get(p.kind.value, p.kind.value)}</span> '
            f'<b>{STAGE_ES.get(p.stage.value, p.stage.value)}</b> '
            f'<span class="muted">· sem {p.start_week}–{p.end_week} · '
            f'{len(micros_in)} semana(s)  ▸</span>'
            f'</summary>'
            f'<ul class="list" style="margin:6px 0 12px">{weeks_html}</ul>'
            f'</details>'
        )
    periods_html = "".join(period_blocks)

    body = f"""
<div class="card">
  <h2>🏆 {title}</h2>
  <p class="muted">Modelo: <b>{MODEL_ES.get(plan.macro.model_id, plan.macro.model_id)}</b> · Semanas: <b>{plan.macro.total_weeks}</b> · Sesiones: <b>{weeks}</b></p>
  <p><a class="btn" href="/plan/{plan.id}/excel">⬇ Exportar macrociclo a Excel</a></p>
</div>
<div class="card">
  <h2>📅 Períodos del macrociclo</h2>
  <p class="muted">Haz clic en un período para desplegar sus semanas y cargas.</p>
  {periods_html}
</div>
{_render_plan_sessions(plan, plan_sessions or [])}
<p><a class="back" href="/">← Inicio</a></p>
"""
    return _page(title, lang, body)


def _render_plan_sessions(plan, plan_sessions: list) -> str:
    """Sesiones guardadas de este plan, agrupadas por semana (vista de proyecto)."""
    mine = [s for s in plan_sessions if s.get("plan_id") == plan.id]
    if not mine:
        return (
            '<div class="card"><h2>📝 Sesiones de este plan</h2>'
            '<p class="muted">Aún no has generado sesiones para este plan. '
            'Vuelve al inicio y crea una; se alineará a la semana que elijas.</p></div>'
        )
    by_week: dict = {}
    for s in mine:
        by_week.setdefault(s.get("week", 0), []).append(s)
    rows = []
    for wk in sorted(by_week):
        items = "".join(
            f'<li><a class="back" href="/session/{s["id"]}/view">{s.get("title","Sesión")}</a> '
            f'<span class="muted">· {"✨ IA" if s.get("source")=="llm" else "base"}</span></li>'
            for s in by_week[wk]
        )
        rows.append(f'<li><b>Semana {wk}</b><ul class="list">{items}</ul></li>')
    return (f'<div class="card"><h2>📝 Sesiones de este plan</h2>'
            f'<ul class="list">{"".join(rows)}</ul></div>')


# Color de barra según intensidad (verde bajo -> naranja medio -> rojo alto).
def _load_color(intensity: int) -> str:
    if intensity >= 85:
        return "#ef4444"      # alta
    if intensity >= 60:
        return "#ff7a1a"      # media
    return "#22c55e"          # baja


def _render_mesocycles(plan, lang: str = "es") -> str:
    """Detalle del macro: cada mesociclo con sus microciclos (semana, tipo, cargas)."""
    mesotype = {
        "base": ("Base", "Base"), "development": ("Desarrollo", "Development"),
        "stabilization": ("Estabilización", "Stabilization"),
        "competitive": ("Competitivo", "Competitive"), "recovery": ("Recuperación", "Recovery"),
    }
    microtype = {
        "introductory": ("Introductorio", "Introductory"),
        "developmental": ("Desarrollador", "Developmental"),
        "shock": ("Choque", "Shock"), "recovery": ("Recuperación", "Recovery"),
        "precompetitive": ("Precompetitivo", "Precompetitive"),
        "competition": ("Competencia", "Competition"),
    }
    blocks = []
    for i, meso in enumerate(plan.macro.mesocycles, start=1):
        mt = mesotype.get(meso.type.value, (meso.type.value, meso.type.value))
        micro_rows = []
        for m in meso.microcycles:
            mct = microtype.get(m.type.value, (m.type.value, m.type.value))
            vol, inten = m.target_volume_pct, m.target_intensity_pct
            # mini-barras de carga
            bar = (
                f'<span style="display:inline-block;height:8px;width:{vol}px;max-width:100px;'
                f'background:#3b82f6;border-radius:4px;vertical-align:middle"></span>'
                f'<span class="muted" style="margin:0 10px 0 6px">vol {vol}%</span>'
                f'<span style="display:inline-block;height:8px;width:{inten}px;max-width:100px;'
                f'background:{_load_color(inten)};border-radius:4px;vertical-align:middle"></span>'
                f'<span class="muted" style="margin-left:6px">int {inten}%</span>'
            )
            label = mct[0] if lang == "es" else mct[1]
            micro_rows.append(
                f'<li><b>{_t("Sem","Wk",lang)} {m.week_index}</b> '
                f'<span class="muted">· {label} · {_t("sesiones","sessions",lang)}: {len(m.session_slots)}</span>'
                f'<div style="margin-top:6px">{bar}</div></li>'
            )
        name = mt[0] if lang == "es" else mt[1]
        blocks.append(
            f'<div class="card" id="meso{i}"><h2>🔁 Mesociclo {i} · {name} '
            f'<span class="muted" style="font-weight:400">(sem {meso.start_week}–{meso.end_week})</span></h2>'
            f'<ul class="list">{"".join(micro_rows)}</ul></div>'
        )
    return "".join(blocks)


def render_roster(roster, lang: str = "es") -> str:
    if roster is None or not roster.players:
        rows = f"<li class='muted'>{_t('Aún no hay jugadores. Añade uno abajo.','No players yet. Add one below.',lang)}</li>"
        player_opts = ""
    else:
        items = []
        player_opts = ""
        for p in roster.players:
            objs = "".join(
                f'<li><span class="pill {o.category.value}">{o.category.value}</span> '
                f'{(o.content.es if lang=="es" else o.content.en)} '
                f'<span class="muted">({o.progress_pct}%{" ✓" if o.mastered else ""})</span></li>'
                for o in p.objectives
            ) or f"<li class='muted'>{_t('sin objetivos','no goals',lang)}</li>"
            items.append(
                f'<li><b>{p.name}</b> <span class="muted">· {p.position_key}</span>'
                f'<ul class="list" style="margin-top:8px">{objs}</ul></li>'
            )
            player_opts += f'<option value="{p.id}">{p.name}</option>'
        rows = "".join(items)

    team = roster.team_name if roster else _t("Mi equipo", "My team", lang)
    body = f"""
<div class="card">
  <h2>👥 {_t('Equipo','Team',lang)}: {team}</h2>
  <ul class="list">{rows}</ul>
</div>
<div class="card">
  <h2>➕ {_t('Añadir jugador','Add player',lang)}</h2>
  <form method="get" action="/roster/player">
    <div class="row">
      <div><label>{_t('Nombre','Name',lang)}</label><input name="name" required></div>
      <div><label>{_t('Posición','Position',lang)}</label>
        <select name="position_key">
          <option value="gk">{_t('Portero','Goalkeeper',lang)}</option>
          <option value="cb">{_t('Central','Center-back',lang)}</option>
          <option value="fb">{_t('Lateral','Full-back',lang)}</option>
          <option value="dm">{_t('Medio','Midfielder',lang)}</option>
          <option value="wm">{_t('Interior/Extremo','Winger',lang)}</option>
          <option value="fw">{_t('Delantero','Forward',lang)}</option>
        </select>
      </div>
    </div>
    <button type="submit">{_t('Añadir','Add',lang)}</button>
  </form>
</div>
<div class="card">
  <h2>🎯 {_t('Asignar objetivo individual','Set individual goal',lang)}</h2>
  <form method="get" action="/roster/objective">
    <div class="row">
      <div><label>{_t('Jugador','Player',lang)}</label><select name="player_id">{player_opts}</select></div>
      <div><label>{_t('Categoría','Category',lang)}</label>
        <select name="category">
          <option value="potentiate">{_t('Potenciar','Potentiate',lang)}</option>
          <option value="improve">{_t('Mejorar','Improve',lang)}</option>
          <option value="eliminate">{_t('Eliminar','Eliminate',lang)}</option>
        </select>
      </div>
    </div>
    <label>{_t('Contenido','Content',lang)}</label><input name="content" required>
    <button type="submit">{_t('Guardar','Save',lang)}</button>
  </form>
</div>
<p><a class="back" href="/">← {_t('Inicio','Home',lang)}</a></p>
"""
    return _page(_t("Equipo", "Team", lang), lang, body)


def render_sessions_history(sessions: list, lang: str = "es") -> str:
    if not sessions:
        rows = "<li class='muted'>Aún no hay sesiones guardadas.</li>"
    else:
        src_label = {"llm": "✨ IA", "deterministic": "base"}
        rows = "".join(
            f'<li><a class="back" href="/session/{s["id"]}/view"><b>{s.get("title","Sesión")}</b></a> '
            f'<span class="muted">· semana {s.get("week","-")} · {src_label.get(s.get("source",""), s.get("source",""))}</span></li>'
            for s in reversed(sessions)
        )
    body = f"""
<div class="card">
  <h2>📚 Historial de sesiones</h2>
  <ul class="list">{rows}</ul>
</div>
<p><a class="back" href="/">← Inicio</a></p>
"""
    return _page("Sesiones", lang, body, "Historial")


def render_session(doc, alignment: Alignment, lang: str = "es", pdf_available: bool = False, sid: str = "") -> str:
    align_msg = {
        Alignment.FULL: _t("✓ Alineada al macrociclo vigente", "✓ Aligned to the active macrocycle", lang),
        Alignment.PARTIAL: _t("Macro construido por entrevista", "Macro built via interview", lang),
        Alignment.NONE: _t("⚠ Sin macro — alineación parcial", "⚠ No macro — partial alignment", lang),
    }[alignment]
    color = {"full": "#2e7d32", "partial": "#f9a825", "none": "#c62828"}[alignment.value]
    from app.persistence.html_export import session_body_html
    inner = session_body_html(doc, lang)
    print_link = f'<a class="btn" href="/session/{sid}/print" target="_blank">🖨️ Imprimir / PDF</a>' if sid else ""
    pdf_btn = (
        f'<a class="btn" href="/session/{sid}/pdf">⬇ Descargar PDF</a> {print_link}'
        if (pdf_available and sid) else
        f'{print_link} <span class="muted">(desde ahí: Imprimir → Guardar como PDF)</span>'
    )
    src_badge = ""
    if getattr(doc, "source", "") == "llm":
        src_badge = '<span class="muted" style="margin-left:10px">✨ generada con IA</span>'
    elif getattr(doc, "source", "") == "deterministic":
        src_badge = '<span class="muted" style="margin-left:10px">estructura base (sin IA)</span>'
    banner = f'<div class="banner" style="background:{color}">{align_msg}{src_badge}</div>'
    body = f'{banner}{inner}<p>{pdf_btn} &nbsp; <a class="back" href="/">← {_t("Inicio","Home",lang)}</a></p>'
    return _page(_t("Sesión", "Session", lang), lang, body)
