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
    background: var(--bg-2); color:#fff; padding: 26px 36px;
    display:flex; flex-direction:row; align-items:center; justify-content:flex-start;
    gap:22px; border-bottom:1px solid var(--line);
  }
  header .logo { display:block; height:92px !important; width:auto !important; flex:0 0 auto; }
  header > div { display:flex; flex-direction:column; justify-content:center; }
  header h1 { margin: 0; font-size: 42px; font-weight: 800; letter-spacing:.5px; }
  header .muted { font-size: 17px; }
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
<style>
  .hub {{ display:flex; gap:16px; flex-wrap:wrap; margin:6px 0 10px; }}
  .hub-card {{ flex:1 1 240px; background:var(--card); border:1px solid var(--line);
               border-radius:18px; padding:22px; text-decoration:none; color:var(--ink);
               transition:.15s; display:block; }}
  .hub-card:hover {{ border-color:var(--green); transform:translateY(-2px); }}
  .hub-card .ico {{ font-size:34px; }}
  .hub-card h3 {{ margin:10px 0 6px; font-size:19px; }}
  .hub-card p {{ color:var(--muted); font-size:13px; margin:0; line-height:1.5; }}
  .hub-card .cta {{ display:inline-block; margin-top:12px; color:var(--green); font-weight:700; font-size:13px; }}
  details.classic > summary {{ cursor:pointer; color:var(--muted); font-size:13px; padding:6px 0; }}
</style>

<p style="margin:4px 0 2px">¿Qué quieres hacer hoy? &nbsp; {llm_badge}</p>
<div class="hub">
  <a class="hub-card" href="/plan/new">
    <div class="ico">🗓️</div><h3>Macrociclos</h3>
    <p>Planea la temporada hablando con el agente: periodos, cargas, competencias y fechas.</p>
    <span class="cta">Crear / abrir →</span>
  </a>
  <a class="hub-card" href="/session/new">
    <div class="ico">📋</div><h3>Sesiones</h3>
    <p>Arma entrenamientos con diagramas y ajústalos hablando: «hazla más intensa».</p>
    <span class="cta">Crear / abrir →</span>
  </a>
  <a class="hub-card" href="/roster">
    <div class="ico">👥</div><h3>Equipo</h3>
    <p>Plantel y desarrollo del deportista. (Módulos multidisciplinarios: próximamente.)</p>
    <span class="cta">Ver →</span>
  </a>
</div>
"""
    return _page("Canchero", lang, body, "Sí la mueve planificando")


def classic_plan_form(models, formats, lang: str = "es") -> str:
    """Formulario clásico de plan (desplegable dentro de la entrevista de macro)."""
    model_opts = "".join(f'<option value="{m.id}">{m.name.es}</option>' for m in models)
    fmt_opts = "".join(f'<option value="{f.id}">{f.name.es}</option>' for f in formats)
    cat_opts = "".join(f'<option value="{c}">{c or "— sin especificar —"}</option>' for c in _CATEGORIES)
    return f"""
<details class="classic" style="margin-top:14px;max-width:720px;margin-left:auto;margin-right:auto">
  <summary style="cursor:pointer;color:var(--muted);font-size:13px">O usar el formulario clásico</summary>
  <form method="get" action="/plan" style="margin-top:8px">
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
</details>
"""


def classic_session_form(history, formats, lang: str = "es") -> str:
    """Formulario clásico de sesión (desplegable dentro de la entrevista de sesión)."""
    fmt_opts = "".join(f'<option value="{f.id}">{f.name.es}</option>' for f in formats)
    cat_opts = "".join(f'<option value="{c}">{c or "— sin especificar —"}</option>' for c in _CATEGORIES)
    plan_opts = '<option value="">— sin plan (sesión suelta) —</option>' + "".join(
        f'<option value="{h.id}">{h.title_es}</option>' for h in history)
    return f"""
<details class="classic" style="margin-top:14px;max-width:720px;margin-left:auto;margin-right:auto">
  <summary style="cursor:pointer;color:var(--muted);font-size:13px">O usar el formulario clásico</summary>
  <form method="get" action="/session" style="margin-top:8px">
    <label>¿Qué quieres entrenar?</label>
    <input name="text" placeholder="Ej. conducción y recepción perfilada con tiro a puerta" required>
    <div class="row">
      <div><label>Vincular a un plan</label><select name="plan_id">{plan_opts}</select></div>
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
    <label>Fundamentos técnicos</label>
    {_checkbox_group("technical_focus", _TECNICOS)}
    <input name="technical_focus_extra" placeholder="Otros (separa con comas)">
    <label>Fundamentos tácticos</label>
    {_checkbox_group("tactical_focus", _TACTICOS)}
    <input name="tactical_focus_extra" placeholder="Otros (separa con comas)">
    <label>Capacidades físicas</label>
    {_checkbox_group("physical_focus", _FISICOS)}
    <input name="physical_focus_extra" placeholder="Otras (separa con comas)">
    <label>Material disponible</label>
    <input name="materials" placeholder="balones, conos, vallas, balón sonoro...">
    <button type="submit">✨ Generar sesión</button>
  </form>
</details>
"""


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
  <p>
    <a class="btn" href="/plan/{plan.id}/chat">💬 Editar con el agente</a>
    <a class="btn" href="/plan/{plan.id}/matrix" target="_blank">📊 Ver matriz (plantilla)</a>
    <a class="btn" href="/plan/{plan.id}/excel">⬇ Exportar a Excel</a>
  </p>
  <p class="muted">La matriz abre en una pestaña nueva, lista para imprimir o guardar como PDF (apaisado). Desde ahí: Imprimir → Guardar como PDF.</p>
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
    chat_link = f'<a class="btn" href="/session/{sid}/chat">💬 Editar con el agente</a>' if sid else ""
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
    body = f'{banner}{inner}<p>{chat_link} {pdf_btn} &nbsp; <a class="back" href="/">← {_t("Inicio","Home",lang)}</a></p>'
    return _page(_t("Sesión", "Session", lang), lang, body)


# --------------------------------------------------------------------------- #
# Pantalla "estudio": chat iterativo (izquierda) + vista previa matriz (derecha).
# El entrenador escribe un ajuste en lenguaje natural y ve el cambio al instante.
# --------------------------------------------------------------------------- #
def render_plan_studio(plan, lang: str = "es", chat_history=None,
                       meta: dict | None = None, llm_on: bool = False) -> str:
    meta = meta or {}
    title = plan.title.es if lang == "es" else plan.title.en
    pid = plan.id
    history = chat_history or []
    ia_badge = ('<span style="color:#22c55e;font-size:12px">✨ IA activa (OpenAI)</span>'
                if llm_on else
                '<span style="color:#f9a825;font-size:12px">⚙️ modo reglas (sin IA) — '
                'activa OpenAI para un chat más listo</span>')

    # Burbujas del chat.
    bubbles = []
    for msg in history:
        who = msg.get("role", "user")
        text = _esc_studio(msg.get("text", ""))
        if who == "user":
            bubbles.append(
                f'<div style="align-self:flex-end;background:#22c55e;color:#06220f;'
                f'padding:9px 13px;border-radius:14px 14px 2px 14px;max-width:85%;'
                f'margin:4px 0;font-size:14px">{text}</div>'
            )
        else:
            bubbles.append(
                f'<div style="align-self:flex-start;background:#1b2330;color:#e7edf3;'
                f'padding:9px 13px;border-radius:14px 14px 14px 2px;max-width:85%;'
                f'margin:4px 0;font-size:14px">{text}</div>'
            )
    if not bubbles:
        bubbles.append(
            '<div style="align-self:flex-start;background:#1b2330;color:#9fb0c0;'
            'padding:9px 13px;border-radius:14px;max-width:90%;margin:4px 0;font-size:14px">'
            '¡Hola! Soy tu asistente. Dime cómo ajustar el macrociclo, por ejemplo:<br>'
            '• «sube el volumen de la semana 5»<br>'
            '• «pon la intensidad del mesociclo 2 en 80»<br>'
            '• «marca la semana 8 como descarga»<br>'
            '• «cambia el objetivo del mesociclo 3 a presión alta»</div>'
        )

    # La vista previa lee los metadatos (equipo, fechas, competencias) del repo,
    # así que basta con la URL base; se actualiza sola en cada cambio.
    import urllib.parse
    preview_url = f"/plan/{pid}/matrix"

    chips = (
        '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 10px">'
        + "".join(
            f'<a href="/plan/{pid}/chat/apply?instruction={urllib.parse.quote(c)}" '
            f'style="background:#1b2330;color:#9fb0c0;border:1px solid #2a3647;'
            f'border-radius:999px;padding:5px 11px;font-size:12px;text-decoration:none">{c}</a>'
            for c in ("sube el volumen de la semana 3",
                      "baja la intensidad del mesociclo 2",
                      "marca la semana 8 como descarga")
        )
        + "</div>"
    )

    body = f"""
<div class="card" style="padding:0;overflow:hidden">
  <div style="display:flex;min-height:72vh;flex-wrap:wrap">
    <!-- Columna chat -->
    <div style="flex:1 1 360px;min-width:320px;display:flex;flex-direction:column;
                border-right:1px solid var(--line);background:#0e1116">
      <div style="padding:14px 16px;border-bottom:1px solid var(--line)">
        <b>💬 Ajusta el macrociclo hablando</b> &nbsp; {ia_badge}
        <div class="muted" style="font-size:12px">{_esc_studio(title)}</div>
      </div>
      <div style="flex:1;overflow-y:auto;padding:12px 14px;display:flex;flex-direction:column">
        {"".join(bubbles)}
      </div>
      <div style="padding:12px 14px;border-top:1px solid var(--line)">
        <details style="margin-bottom:10px">
          <summary style="cursor:pointer;color:var(--muted);font-size:12px">
            ⚙️ Datos del plan (equipo, fecha de inicio, competencias)</summary>
          <form method="get" action="/plan/{pid}/chat/apply"
                style="display:flex;flex-direction:column;gap:6px;margin:8px 0 0">
            <input name="instruction" placeholder="Ej. ponle el nombre del equipo: Club América"
                   style="margin:0">
            <button type="submit" style="margin:0;align-self:flex-start;padding:7px 14px">Aplicar</button>
          </form>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px">
            <a href="/plan/{pid}/chat/apply?instruction={_q('el macro inicia el 10 de agosto de 2026')}"
               style="background:#1b2330;color:#9fb0c0;border:1px solid #2a3647;border-radius:999px;padding:5px 11px;font-size:12px;text-decoration:none">📅 fecha de inicio…</a>
            <a href="/plan/{pid}/chat/apply?instruction={_q('tengo competencia el 20 de agosto vs Rival')}"
               style="background:#1b2330;color:#9fb0c0;border:1px solid #2a3647;border-radius:999px;padding:5px 11px;font-size:12px;text-decoration:none">⚽ agregar competencia…</a>
          </div>
        </details>
        {chips}
        <form method="get" action="/plan/{pid}/chat/apply" style="display:flex;gap:8px;margin:0">
          <input name="instruction" placeholder="Escribe tu ajuste…" autofocus
                 style="flex:1;margin:0" required>
          <button type="submit" style="margin:0">➤</button>
        </form>
      </div>
    </div>
    <!-- Columna vista previa -->
    <div style="flex:2 1 520px;min-width:360px;background:#fff">
      <div style="padding:8px 12px;background:#161b22;color:#9fb0c0;font-size:12px;
                  display:flex;justify-content:space-between;align-items:center">
        <span>Vista previa (se actualiza con cada cambio)</span>
        <a class="btn" href="{preview_url}" target="_blank"
           style="margin:0;padding:6px 12px;font-size:12px">🖨️ Abrir / Imprimir</a>
      </div>
      <iframe src="{preview_url}" style="width:100%;height:68vh;border:0;background:#fff"></iframe>
    </div>
  </div>
</div>
<p><a class="back" href="/plan/{pid}">← Volver al plan</a> &nbsp;
   <a class="back" href="/">Inicio</a></p>
"""
    return _page(f"Estudio · {title}", lang, body, "Edita conversando con el agente")


def _esc_studio(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def _q(s: str) -> str:
    import urllib.parse
    return urllib.parse.quote(s)


# --------------------------------------------------------------------------- #
# Entrevista conversacional para CREAR un macrociclo (estilo AI-DLC).
# Modo guiado (pregunta por pregunta, con opciones + explicación + recomendación)
# o experto (todo de un jalón). Sin estado en servidor: answers viaja en la URL.
# --------------------------------------------------------------------------- #
def render_macro_interview(answers: dict, question: dict | None,
                           mode: str = "guided", lang: str = "es") -> str:
    import json
    import urllib.parse
    from app.planning_service import macro_interview as mi

    answers = answers or {}
    raw_json = json.dumps(answers, ensure_ascii=False)
    enc = urllib.parse.quote(raw_json)        # para HREFs (GET por enlace)
    attr_json = _esc_studio(raw_json)         # para value="" de <input hidden> (sin URL-encode)

    # Historial: lo ya respondido como burbujas.
    bubbles = [
        '<div class="ib-bot">Vamos a armar tu macrociclo. Te hago unas preguntas '
        'y al final lo genero. Puedes cambiar al <b>modo experto</b> si prefieres '
        'escribirlo todo de un jalón.</div>'
    ]
    labels = {"team": "Equipo", "format": "Formato", "weeks": "Semanas",
              "days": "Días/sem", "matches": "Partidos/sem", "start_date": "Inicio",
              "model": "Modelo", "category": "Categoría"}
    for k in mi.STEPS:
        if k in answers and str(answers[k]) != "":
            val = answers[k]
            if k == "format":
                val = next((n for fid, n, _ in mi.FORMATOS if fid == val), val)
            if k == "model":
                val = next((n for mid, n, _, _ in mi.MODELOS if mid == val), val)
            bubbles.append(f'<div class="ib-me">{_esc_studio(labels.get(k,k))}: {_esc_studio(str(val))}</div>')

    # Bloque de la pregunta actual (o el resumen final).
    if question is None:
        panel = (
            '<div class="ib-bot"><b>¡Listo!</b> Esto es lo que capturé:<br>'
            f'{_esc_studio(mi.summary(answers))}</div>'
            f'<form method="get" action="/plan/new/create" style="margin-top:10px">'
            f'<input type="hidden" name="answers" value="{attr_json}">'
            f'<button type="submit" style="margin:0">⚡ Generar macrociclo</button></form>'
        )
    else:
        panel = _interview_question_html(question, enc, attr_json)

    mode_toggle = (
        f'<div style="margin-bottom:10px;font-size:12px">'
        f'<a href="/plan/new?mode=guided" style="color:{"#22c55e" if mode!="expert" else "#9fb0c0"};text-decoration:none">● Guiado</a> &nbsp; '
        f'<a href="/plan/new?mode=expert" style="color:{"#22c55e" if mode=="expert" else "#9fb0c0"};text-decoration:none">● Experto</a>'
        f'</div>'
    )

    expert_box = ""
    if mode == "expert":
        expert_box = (
            '<div class="ib-bot">Modo experto: escríbelo todo en una frase. Ej.: '
            '«Club América ciegos, 20 semanas, 4 días, 1 partido, inicia 10 de agosto de 2026, modelo ATR».</div>'
            f'<form method="get" action="/plan/new/express" style="display:flex;gap:8px;margin-top:8px">'
            f'<input name="text" placeholder="Describe el plan completo…" style="flex:1;margin:0" autofocus>'
            f'<button type="submit" style="margin:0">➤</button></form>'
        )

    body = f"""
<style>
  .ib-wrap {{ max-width:720px; margin:0 auto; }}
  .ib-chat {{ background:var(--card); border:1px solid var(--line); border-radius:16px;
              padding:16px; display:flex; flex-direction:column; min-height:440px; }}
  .ib-bot {{ align-self:flex-start; background:#1b2330; color:var(--ink); padding:10px 14px;
             border-radius:14px 14px 14px 2px; max-width:86%; margin:5px 0; font-size:14px; line-height:1.5; }}
  .ib-me {{ align-self:flex-end; background:var(--green); color:#06220f; padding:8px 13px;
            border-radius:14px 14px 2px 14px; max-width:86%; margin:4px 0; font-size:13px; }}
  .ib-opts {{ display:flex; flex-direction:column; gap:6px; margin-top:8px; }}
  .ib-opt {{ background:#0e1116; border:1px solid var(--line); border-radius:10px; padding:10px 12px;
             text-decoration:none; color:var(--ink); font-size:13px; }}
  .ib-opt:hover {{ border-color:var(--green); }}
  .ib-opt .d {{ color:var(--muted); font-size:12px; display:block; margin-top:3px; }}
  .ib-rec {{ background:#13261a; border:1px solid #1f5133; color:#8fe0a8; border-radius:10px;
             padding:8px 11px; font-size:12px; margin-top:8px; }}
  .ib-star {{ color:#f9c80e; font-weight:700; }}
</style>
<div class="ib-wrap">
  <h2 style="font-weight:800">🗓️ Macrociclos</h2>
  {_recent_plans_block()}
  <h3 style="font-weight:800;margin:18px 0 8px">Nuevo macrociclo</h3>
  {mode_toggle}
  <div class="ib-chat">
    {"".join(bubbles)}
    {expert_box if mode=="expert" else panel}
  </div>
  {_classic_plan_block()}
  <p><a class="back" href="/">← Inicio</a></p>
</div>
"""
    return _page("Macrociclos", lang, body, "Tus planes y uno nuevo")


def _recent_plans_block() -> str:
    """Lista de planes recientes (para la sección de Macrociclos)."""
    try:
        from app.persistence import JsonFileRepository  # noqa: F401
    except Exception:
        pass
    rows = _load_recent_plans_html()
    if not rows:
        return ""
    return (
        '<div class="card" style="max-width:720px;margin:0 auto">'
        '<h2>📋 Tus planes</h2><ul class="list">' + rows + '</ul></div>'
    )


# El repo real se inyecta desde webapp al arrancar; guardamos una referencia.
_REPO_REF = {"repo": None}


def set_repo_ref(repo):
    _REPO_REF["repo"] = repo


def _load_recent_plans_html() -> str:
    repo = _REPO_REF.get("repo")
    if repo is None:
        return ""
    try:
        hist = repo.list_history()
    except Exception:
        return ""
    return "".join(
        f'<li><a class="back" href="/plan/{h.id}"><b>{_esc_studio(h.title_es)}</b></a> '
        f"<span class='muted'>· {h.model_id} / {h.format_id} · {h.created_at[:10]}</span></li>"
        for h in hist
    )


def _classic_plan_block() -> str:
    """Form clásico de plan embebido en la entrevista (import perezoso de catálogos)."""
    try:
        from app.football_domain import list_formats
        from periodization_engine.models import list_models
        return classic_plan_form(list_models(), list_formats())
    except Exception:
        return ""


def _interview_question_html(q: dict, enc_answers: str, attr_answers: str) -> str:
    """Renderiza la pregunta actual con sus opciones (si las hay).

    enc_answers: JSON URL-encoded, para los HREF (enlaces GET de opciones).
    attr_answers: JSON escapado para atributo HTML, para el value de <input hidden>.
    """
    out = [f'<div class="ib-bot">{_esc_studio(q["texto"])}</div>']
    tipo = q.get("tipo")
    base = f'/plan/new/answer?step={q["id"]}&answers={enc_answers}&value='

    if tipo in ("choice", "choice-rich"):
        out.append('<div class="ib-opts">')
        for opt in q.get("opciones", []):
            import urllib.parse
            url = base + urllib.parse.quote(str(opt["value"]))
            star = ' <span class="ib-star">★ recomendado</span>' if opt.get("recomendado") else ""
            if tipo == "choice-rich":
                out.append(
                    f'<a class="ib-opt" href="{url}"><b>{_esc_studio(opt["label"])}</b>{star}'
                    f'<span class="d">{_esc_studio(opt.get("desc",""))}</span>'
                    f'<span class="d">👉 {_esc_studio(opt.get("para",""))}</span></a>'
                )
            else:
                out.append(f'<a class="ib-opt" href="{url}">{_esc_studio(opt["label"])}{star}</a>')
        out.append("</div>")
    else:
        # texto / número / fecha -> input libre
        itype = {"number": "number", "date": "date"}.get(tipo, "text")
        out.append(
            f'<form method="get" action="/plan/new/answer" style="display:flex;gap:8px;margin-top:8px">'
            f'<input type="hidden" name="step" value="{q["id"]}">'
            f'<input type="hidden" name="answers" value="{attr_answers}">'
            f'<input name="value" type="{itype}" placeholder="{_esc_studio(q.get("placeholder",""))}" '
            f'style="flex:1;margin:0" autofocus required>'
            f'<button type="submit" style="margin:0">➤</button></form>'
        )
    if q.get("recomendacion"):
        out.append(f'<div class="ib-rec">💡 {_esc_studio(q["recomendacion"])}</div>')
    return "".join(out)


# --------------------------------------------------------------------------- #
# Estudio de SESIÓN: chat iterativo (izquierda) + vista previa de la hoja (dcha).
# Análogo a render_plan_studio pero para una SessionDoc.
# --------------------------------------------------------------------------- #
def render_session_studio(doc, sid: str, lang: str = "es", chat_history=None,
                          llm_on: bool = False) -> str:
    history = chat_history or []
    title = doc.objective.es if lang == "es" else doc.objective.en
    ia_badge = ('<span style="color:#22c55e;font-size:12px">✨ IA activa (OpenAI)</span>'
                if llm_on else
                '<span style="color:#f9a825;font-size:12px">⚙️ modo reglas (sin IA)</span>')
    estilo = getattr(doc, "sheet_style", "dark")
    estilo_txt = "Fútbol Inclusivo" if estilo == "inclusivo" else "Canchero"

    bubbles = []
    for msg in history:
        who = msg.get("role", "user")
        text = _esc_studio(msg.get("text", ""))
        if who == "user":
            bubbles.append(
                f'<div style="align-self:flex-end;background:#22c55e;color:#06220f;'
                f'padding:9px 13px;border-radius:14px 14px 2px 14px;max-width:85%;'
                f'margin:4px 0;font-size:14px">{text}</div>')
        else:
            bubbles.append(
                f'<div style="align-self:flex-start;background:#1b2330;color:#e7edf3;'
                f'padding:9px 13px;border-radius:14px 14px 14px 2px;max-width:85%;'
                f'margin:4px 0;font-size:14px">{text}</div>')
    if not bubbles:
        bubbles.append(
            '<div style="align-self:flex-start;background:#1b2330;color:#9fb0c0;'
            'padding:9px 13px;border-radius:14px;max-width:92%;margin:4px 0;font-size:14px">'
            '¡Hola! Puedo ajustar esta sesión. Por ejemplo:<br>'
            '• «hazla más intensa» / «más suave»<br>'
            '• «agrega una variante al calentamiento»<br>'
            '• «pon el calentamiento a 20 min» / «ponla a 75 minutos»<br>'
            '• «cambia la plantilla a Inclusivo»</div>')

    import urllib.parse
    chips = (
        '<div style="display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 10px">'
        + "".join(
            f'<a href="/session/{sid}/chat/apply?instruction={urllib.parse.quote(c)}" '
            f'style="background:#1b2330;color:#9fb0c0;border:1px solid #2a3647;'
            f'border-radius:999px;padding:5px 11px;font-size:12px;text-decoration:none">{c}</a>'
            for c in ("hazla más intensa", "agrega una variante al calentamiento",
                      "cambia la plantilla a Inclusivo")
        ) + "</div>"
    )
    preview_url = f"/session/{sid}/preview"

    body = f"""
<div class="card" style="padding:0;overflow:hidden">
  <div style="display:flex;min-height:72vh;flex-wrap:wrap">
    <div style="flex:1 1 360px;min-width:320px;display:flex;flex-direction:column;
                border-right:1px solid var(--line);background:#0e1116">
      <div style="padding:14px 16px;border-bottom:1px solid var(--line)">
        <b>💬 Ajusta la sesión hablando</b> &nbsp; {ia_badge}
        <div class="muted" style="font-size:12px">Plantilla: {estilo_txt}</div>
      </div>
      <div style="flex:1;overflow-y:auto;padding:12px 14px;display:flex;flex-direction:column">
        {"".join(bubbles)}
      </div>
      <div style="padding:12px 14px;border-top:1px solid var(--line)">
        {chips}
        <form method="get" action="/session/{sid}/chat/apply" style="display:flex;gap:8px;margin:0">
          <input name="instruction" placeholder="Escribe tu ajuste…" autofocus
                 style="flex:1;margin:0" required>
          <button type="submit" style="margin:0">➤</button>
        </form>
      </div>
    </div>
    <div style="flex:2 1 520px;min-width:360px;background:#fff">
      <div style="padding:8px 12px;background:#161b22;color:#9fb0c0;font-size:12px;
                  display:flex;justify-content:space-between;align-items:center">
        <span>Vista previa de la hoja (se actualiza con cada cambio)</span>
        <a class="btn" href="/session/{sid}/print" target="_blank"
           style="margin:0;padding:6px 12px;font-size:12px">🖨️ Abrir / Imprimir</a>
      </div>
      <iframe src="{preview_url}" style="width:100%;height:68vh;border:0;background:#fff"></iframe>
    </div>
  </div>
</div>
<p><a class="back" href="/session/{sid}/view">← Ver sesión</a> &nbsp;
   <a class="back" href="/">Inicio</a></p>
"""
    return _page(f"Estudio de sesión", lang, body, "Edita conversando con el agente")


# --------------------------------------------------------------------------- #
# Entrevista conversacional para CREAR una SESIÓN (estilo AI-DLC).
# Reutiliza _interview_question_html; las respuestas viajan como JSON en la URL.
# --------------------------------------------------------------------------- #
def render_session_interview(answers: dict, question: dict | None,
                             plans: list | None = None, lang: str = "es") -> str:
    import json
    import urllib.parse
    from app.planning_service import session_interview as si

    answers = answers or {}
    raw_json = json.dumps(answers, ensure_ascii=False)
    enc = urllib.parse.quote(raw_json)
    attr_json = _esc_studio(raw_json)

    bubbles = [
        '<div class="ib-bot">Vamos a armar una sesión. Te hago unas preguntas y '
        'al final la genero (y luego la puedes ajustar hablando).</div>'
    ]
    labels = {"plan": "Plan", "week": "Semana", "text": "Tema",
              "technical": "Técnico", "tactical": "Táctico", "physical": "Físico",
              "duration": "Duración", "sheet_style": "Hoja"}
    for k in si.STEPS:
        if k in answers and str(answers[k]) not in ("", "__skip__", "__none__"):
            bubbles.append(
                f'<div class="ib-me">{_esc_studio(labels.get(k,k))}: '
                f'{_esc_studio(str(answers[k]))}</div>')

    if question is None:
        panel = (
            '<div class="ib-bot"><b>¡Listo!</b> ' + _esc_studio(si.summary(answers)) + '</div>'
            f'<form method="get" action="/session/new/create" style="margin-top:10px">'
            f'<input type="hidden" name="answers" value="{attr_json}">'
            f'<button type="submit" style="margin:0">⚡ Generar sesión</button></form>'
        )
    else:
        panel = _interview_question_html_sess(question, enc, attr_json)

    body = f"""
<style>
  .ib-wrap {{ max-width:720px; margin:0 auto; }}
  .ib-chat {{ background:var(--card); border:1px solid var(--line); border-radius:16px;
              padding:16px; display:flex; flex-direction:column; min-height:440px; }}
  .ib-bot {{ align-self:flex-start; background:#1b2330; color:var(--ink); padding:10px 14px;
             border-radius:14px 14px 14px 2px; max-width:86%; margin:5px 0; font-size:14px; line-height:1.5; }}
  .ib-me {{ align-self:flex-end; background:var(--green); color:#06220f; padding:8px 13px;
            border-radius:14px 14px 2px 14px; max-width:86%; margin:4px 0; font-size:13px; }}
  .ib-opts {{ display:flex; flex-direction:column; gap:6px; margin-top:8px; }}
  .ib-opt {{ background:#0e1116; border:1px solid var(--line); border-radius:10px; padding:10px 12px;
             text-decoration:none; color:var(--ink); font-size:13px; }}
  .ib-opt:hover {{ border-color:var(--green); }}
  .ib-rec {{ background:#13261a; border:1px solid #1f5133; color:#8fe0a8; border-radius:10px;
             padding:8px 11px; font-size:12px; margin-top:8px; }}
  .ib-star {{ color:#f9c80e; font-weight:700; }}
</style>
<div class="ib-wrap">
  <h2 style="font-weight:800">📋 Sesiones</h2>
  {_recent_sessions_block()}
  <h3 style="font-weight:800;margin:18px 0 8px">Nueva sesión</h3>
  <div class="ib-chat">
    {"".join(bubbles)}
    {panel}
  </div>
  {_classic_session_block(plans)}
  <p><a class="back" href="/">← Inicio</a></p>
</div>
"""
    return _page("Sesiones", lang, body, "Tus sesiones y una nueva")


def _recent_sessions_block() -> str:
    """Historial de sesiones (para la sección de Sesiones)."""
    repo = _REPO_REF.get("repo")
    if repo is None:
        return ""
    try:
        sess = repo.list_sessions()
    except Exception:
        return ""
    if not sess:
        return ('<div class="card" style="max-width:720px;margin:0 auto">'
                '<h2>📚 Tus sesiones</h2><p class="muted">Aún no hay sesiones. '
                '¡Crea la primera abajo!</p></div>')
    rows = "".join(
        f'<li><a class="back" href="/session/{s.get("id")}/view">'
        f'<b>{_esc_studio(s.get("title","Sesión"))}</b></a> '
        f'<span class="muted">· {"✨ IA" if s.get("source")=="llm" else "base"}'
        f' · sem {s.get("week","-")}</span></li>'
        for s in reversed(sess)
    )
    return ('<div class="card" style="max-width:720px;margin:0 auto">'
            f'<h2>📚 Tus sesiones</h2><ul class="list">{rows}</ul></div>')


def _classic_session_block(plans) -> str:
    """Form clásico de sesión embebido en la entrevista."""
    try:
        from app.football_domain import list_formats
        # 'plans' viene como [{"id","title"}]; classic_session_form usa .id/.title_es
        class _Ref:
            def __init__(self, d):
                self.id = d.get("id", ""); self.title_es = d.get("title", "")
        hist = [_Ref(p) for p in (plans or [])]
        return classic_session_form(hist, list_formats())
    except Exception:
        return ""


def _interview_question_html_sess(q: dict, enc_answers: str, attr_answers: str) -> str:
    """Igual que el del macro pero apuntando a /session/new/answer."""
    import urllib.parse
    out = [f'<div class="ib-bot">{_esc_studio(q["texto"])}</div>']
    tipo = q.get("tipo")
    base = f'/session/new/answer?step={q["id"]}&answers={enc_answers}&value='
    if tipo in ("choice", "choice-rich"):
        out.append('<div class="ib-opts">')
        for opt in q.get("opciones", []):
            url = base + urllib.parse.quote(str(opt["value"]))
            star = ' <span class="ib-star">★</span>' if opt.get("recomendado") else ""
            out.append(f'<a class="ib-opt" href="{url}">{_esc_studio(opt["label"])}{star}</a>')
        out.append("</div>")
    else:
        itype = {"number": "number", "date": "date"}.get(tipo, "text")
        out.append(
            f'<form method="get" action="/session/new/answer" style="display:flex;gap:8px;margin-top:8px">'
            f'<input type="hidden" name="step" value="{q["id"]}">'
            f'<input type="hidden" name="answers" value="{attr_answers}">'
            f'<input name="value" type="{itype}" placeholder="{_esc_studio(q.get("placeholder",""))}" '
            f'style="flex:1;margin:0" autofocus required>'
            f'<button type="submit" style="margin:0">➤</button></form>'
        )
    if q.get("recomendacion"):
        out.append(f'<div class="ib-rec">💡 {_esc_studio(q["recomendacion"])}</div>')
    return "".join(out)
