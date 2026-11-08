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


def render_home(history, models, formats, lang: str = "es") -> str:
    model_opts = "".join(f'<option value="{m.id}">{m.name.es}</option>' for m in models)
    fmt_opts = "".join(f'<option value="{f.id}">{f.name.es}</option>' for f in formats)
    rows = "".join(
        f"<li><b>{h.title_es}</b> <span class='muted'>· {h.model_id} / {h.format_id} · {h.created_at}</span></li>"
        for h in history
    ) or f"<li class='muted'>{_t('Aún no hay planes. ¡Crea el primero abajo!','No plans yet. Create your first below!',lang)}</li>"

    body = f"""
<p><a class="btn" href="/roster">👥 {_t('Gestionar equipo y objetivos','Manage team and goals',lang)}</a></p>

<div class="card">
  <h2>📋 {_t('Historial de planes','Plan history',lang)}</h2>
  <ul class="list">{rows}</ul>
</div>

<div class="card">
  <h2>🗓️ {_t('Nuevo plan de temporada','New season plan',lang)}</h2>
  <form method="get" action="/plan">
    <div class="row">
      <div><label>{_t('Semanas','Weeks',lang)}</label><input name="duration_weeks" value="20"></div>
      <div><label>{_t('Días/semana','Days/week',lang)}</label><input name="training_days_per_week" value="4"></div>
      <div><label>{_t('Partidos/semana','Matches/week',lang)}</label><input name="matches_per_week" value="1"></div>
    </div>
    <div class="row">
      <div><label>{_t('Modelo de periodización','Periodization model',lang)}</label><select name="model_id">{model_opts}</select></div>
      <div><label>{_t('Formato de fútbol','Football format',lang)}</label><select name="format_id">{fmt_opts}</select></div>
    </div>
    <button type="submit">⚡ {_t('Generar plan','Generate plan',lang)}</button>
  </form>
</div>

<div class="card">
  <h2>💬 {_t('Sesión en lenguaje natural','Natural-language session',lang)}</h2>
  <form method="get" action="/session">
    <label>{_t('Describe lo que quieres','Describe what you want',lang)}</label>
    <input name="text" placeholder="{_t('esta semana quiero una sesión de conducción en espacio reducido','this week I want a driving session in reduced space',lang)}">
    <div class="row"><div><label>{_t('Formato','Format',lang)}</label><select name="format_id">{fmt_opts}</select></div></div>
    <input type="hidden" name="plan_id" value="">
    <button type="submit">✨ {_t('Generar sesión','Generate session',lang)}</button>
  </form>
</div>
"""
    return _page("Canchero", lang, body,
                 _t("Sí la mueve planificando", "Plays it smart, planning", lang))


def render_plan(plan, lang: str = "es") -> str:
    title = plan.title.es if lang == "es" else plan.title.en
    weeks = len(plan.sessions)
    # Colores por tipo de período para la línea de tiempo.
    pcolor = {"preparatory":"#2e7d32","competitive":"#1565c0","transition":"#f9a825",
              "resistance":"#2e7d32","strength":"#6a1b9a","speed":"#c62828","recovery":"#00897b"}
    periods = "".join(
        f'<li><span class="pill" style="background:{pcolor.get(p.kind.value,"#555")}">{p.kind.value}</span> '
        f'<span class="muted">{p.stage.value} · {_t("sem","wk",lang)} {p.start_week}–{p.end_week}</span></li>'
        for p in plan.macro.periods
    )
    body = f"""
<div class="card">
  <h2>🏆 {title}</h2>
  <p class="muted">{_t('Modelo','Model',lang)}: <b>{plan.macro.model_id}</b> · {_t('Semanas','Weeks',lang)}: <b>{plan.macro.total_weeks}</b> · {_t('Sesiones','Sessions',lang)}: <b>{weeks}</b></p>
</div>
<div class="card">
  <h2>📅 {_t('Períodos','Periods',lang)}</h2>
  <ul class="list">{periods}</ul>
</div>
<p><a class="back" href="/">← {_t('Inicio','Home',lang)}</a></p>
"""
    return _page(title, lang, body)


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


def render_session(doc, alignment: Alignment, lang: str = "es", pdf_available: bool = False) -> str:
    align_msg = {
        Alignment.FULL: _t("✓ Alineada al macrociclo vigente", "✓ Aligned to the active macrocycle", lang),
        Alignment.PARTIAL: _t("Macro construido por entrevista", "Macro built via interview", lang),
        Alignment.NONE: _t("⚠ Sin macro — alineación parcial", "⚠ No macro — partial alignment", lang),
    }[alignment]
    color = {"full": "#2e7d32", "partial": "#f9a825", "none": "#c62828"}[alignment.value]
    inner = to_html_session(doc, lang)
    pdf_btn = (
        f'<a class="btn" href="/session/{doc.week_index}/pdf">⬇ {_t("Descargar PDF","Download PDF",lang)}</a>'
        if pdf_available else
        f'<span class="muted">{_t("Para PDF: Imprimir → Guardar como PDF","For PDF: Print → Save as PDF",lang)}</span>'
    )
    banner = f'<div class="banner" style="background:{color}">{align_msg}</div>'
    body = f'{banner}<div class="card">{inner}</div><p>{pdf_btn} &nbsp; <a class="back" href="/">← {_t("Inicio","Home",lang)}</a></p>'
    return _page(_t("Sesión", "Session", lang), lang, body)
