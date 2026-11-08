"""Tests de U3 — Diagramas y Gráficas (ejemplos + propiedades PBT)."""
from __future__ import annotations

import xml.etree.ElementTree as ET

from hypothesis import given, settings
from hypothesis import strategies as st

from app.diagrams import (
    render_load_chart,
    render_organization_diagram,
    render_task_diagram,
)
from app.football_domain import get_format, suggest_tasks_for_phase
from periodization_engine import (
    LoadCurve,
    LoadPoint,
    MicroPhase,
    SessionSlot,
    SessionTypeHint,
)


def _slot(phase=MicroPhase.STIMULATING, vol=40, inten=70, day=2):
    return SessionSlot(
        day_index=day, micro_phase=phase, relative_to_match=2,
        target_load=LoadPoint(unit_index=day, volume_pct=vol, intensity_pct=inten),
        session_type=SessionTypeHint.COMPLEX,
    )


def _parse(svg: str):
    """Parsea el SVG como XML; lanza si está mal formado."""
    return ET.fromstring(svg)


def _count_players(svg: str) -> int:
    """Cuenta círculos de jugador (r=14) en el SVG."""
    return svg.count('r="14.00"')


# --------------------------- ejemplos --------------------------------------- #
def test_task_diagram_valid_svg():
    fmt = get_format("football_11").value
    ex = suggest_tasks_for_phase(_slot(), fmt)[0]
    d = render_task_diagram(ex, fmt)
    root = _parse(d.svg)
    assert root.tag.endswith("svg")
    assert d.width > 0 and d.height > 0


def test_blind_diagram_has_side_boards_and_legend():
    fmt = get_format("blind_5").value
    ex = suggest_tasks_for_phase(_slot(), fmt)[0]
    d = render_task_diagram(ex, fmt, lang="es")
    # Las vallas laterales se dibujan en amarillo y la leyenda las nombra.
    assert "#fdd835" in d.svg
    assert "Vallas laterales" in d.svg


def test_conventional_diagram_has_no_adapted_markers():
    fmt = get_format("football_11").value
    ex = suggest_tasks_for_phase(_slot(), fmt)[0]
    d = render_task_diagram(ex, fmt)
    assert "#fdd835" not in d.svg  # sin vallas


def test_player_count_matches_spec():
    fmt = get_format("football_7").value
    ex = suggest_tasks_for_phase(_slot(), fmt)[0]
    d = render_task_diagram(ex, fmt)
    expected = ex.diagram_spec.players_a + ex.diagram_spec.players_b
    assert _count_players(d.svg) == expected


def test_organization_diagram_valid():
    fmt = get_format("football_11").value
    tasks = [suggest_tasks_for_phase(_slot(p), fmt)[0]
             for p in (MicroPhase.RECOVERY, MicroPhase.STIMULATING)]
    d = render_organization_diagram(tasks, fmt)
    assert _parse(d.svg).tag.endswith("svg")


def test_load_chart_valid_and_points():
    curve = LoadCurve(points=tuple(
        LoadPoint(unit_index=i, volume_pct=40 + i, intensity_pct=70)
        for i in range(1, 6)
    ))
    c = render_load_chart(curve, lang="en")
    assert _parse(c.svg).tag.endswith("svg")
    assert "Volume" in c.svg and "Intensity" in c.svg


def test_task_diagram_deterministic():
    fmt = get_format("blind_5").value
    ex = suggest_tasks_for_phase(_slot(), fmt)[0]
    a = render_task_diagram(ex, fmt).svg
    b = render_task_diagram(ex, fmt).svg
    assert a == b


# --------------------------- propiedades (PBT) ------------------------------ #
FORMAT_IDS = ["football_11", "football_7", "futsal", "blind_5", "cp_7", "down", "amputee"]
PHASES = list(MicroPhase)


@settings(max_examples=120, deadline=None)
@given(phase=st.sampled_from(PHASES), fid=st.sampled_from(FORMAT_IDS))
def test_prop_task_svg_wellformed(phase, fid):
    fmt = get_format(fid).value
    ex = suggest_tasks_for_phase(_slot(phase), fmt)[0]
    d = render_task_diagram(ex, fmt)
    assert _parse(d.svg).tag.endswith("svg")
    assert f'width="{d.width}"' in d.svg
    assert f'height="{d.height}"' in d.svg


@settings(max_examples=120, deadline=None)
@given(phase=st.sampled_from(PHASES), fid=st.sampled_from(FORMAT_IDS))
def test_prop_player_count(phase, fid):
    fmt = get_format(fid).value
    ex = suggest_tasks_for_phase(_slot(phase), fmt)[0]
    d = render_task_diagram(ex, fmt)
    expected = ex.diagram_spec.players_a + ex.diagram_spec.players_b
    assert _count_players(d.svg) == expected


@settings(max_examples=100, deadline=None)
@given(phase=st.sampled_from(PHASES), fid=st.sampled_from(FORMAT_IDS))
def test_prop_task_deterministic(phase, fid):
    fmt = get_format(fid).value
    ex = suggest_tasks_for_phase(_slot(phase), fmt)[0]
    assert render_task_diagram(ex, fmt).svg == render_task_diagram(ex, fmt).svg


@settings(max_examples=80, deadline=None)
@given(n=st.integers(min_value=1, max_value=40))
def test_prop_load_chart_points(n):
    curve = LoadCurve(points=tuple(
        LoadPoint(unit_index=i, volume_pct=50, intensity_pct=60)
        for i in range(1, n + 1)
    ))
    c = render_load_chart(curve)
    assert _parse(c.svg).tag.endswith("svg")
