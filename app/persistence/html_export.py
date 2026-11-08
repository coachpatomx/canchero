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
  body { font-family: sans-serif; color: #111; margin: 24px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  h2 { font-size: 16px; margin: 18px 0 6px; border-bottom: 2px solid #2e7d32; }
  .meta { display: flex; flex-wrap: wrap; gap: 8px 24px; font-size: 13px; color: #333; }
  .meta b { color: #111; }
  .task { border: 1px solid #ccc; border-radius: 6px; padding: 10px; margin: 10px 0; }
  .task-head { font-weight: bold; font-size: 15px; }
  .task-meta { font-size: 12px; color: #555; margin: 2px 0 6px; }
  .diagram svg { max-width: 420px; height: auto; border: 1px solid #ddd; }
  .aspects { display: flex; gap: 16px; font-size: 12px; flex-wrap: wrap; }
  .aspects div { flex: 1; min-width: 120px; }
  table { border-collapse: collapse; font-size: 12px; }
  td, th { border: 1px solid #ccc; padding: 3px 6px; }
  @media print { body { margin: 0; } .task { page-break-inside: avoid; } }
</style>
"""


def _label(es: str, en: str, lang: str) -> str:
    return es if lang == "es" else en


def _session_body(session: SessionDoc, lang: str) -> str:
    obj = session.objective.es if lang == "es" else session.objective.en
    load = session.load_label.es if lang == "es" else session.load_label.en
    out = [
        f"<h1>{_esc(obj)}</h1>",
        '<div class="meta">',
        f"<span><b>{_label('Semana','Week',lang)}:</b> {session.week_index}</span>",
        f"<span><b>{_label('Mesociclo','Mesocycle',lang)}:</b> {session.meso_index+1}</span>",
        f"<span><b>{_label('Microciclo','Microcycle',lang)}:</b> {session.micro_index+1}</span>",
        f"<span><b>{_label('Carga','Load',lang)}:</b> {_esc(load)}</span>",
        f"<span><b>{_label('Fecha','Date',lang)}:</b> {_esc(session.date or '-')}</span>",
        "</div>",
        f"<h2>{_label('Tareas','Tasks',lang)}</h2>",
    ]
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


def to_html_session(session: SessionDoc, lang: str = "es") -> str:
    return (
        f'<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">'
        f"<title>{_esc(session.objective.es if lang=='es' else session.objective.en)}</title>"
        f"{_CSS}</head><body>{_session_body(session, lang)}</body></html>"
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
