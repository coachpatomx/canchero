"""U3 — Diagramas y Gráficas (SVG, D3).

Convierte los datos de diagrama de U2 y la curva de carga de U1 en SVG listo
para incrustar en la web (U5) y el PDF (U4). Sin librerías de terceros (RNF-2).
"""
from __future__ import annotations

from .drill_diagram import has_drill_data, render_drill  # noqa: F401
from .load_chart import SvgChart, render_load_chart  # noqa: F401
from .organization import render_organization_diagram  # noqa: F401
from .task_diagram import SvgDiagram, render_task_diagram  # noqa: F401

__all__ = [
    "render_task_diagram", "render_organization_diagram", "render_load_chart",
    "SvgDiagram", "SvgChart", "render_drill", "has_drill_data",
]
