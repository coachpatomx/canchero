"""U4 — Persistencia (JSON, D2) y Exportación (HTML base + PDF opcional).

Guarda/reabre planes e historial, biblioteca de ejercicios (RF-9), y exporta a
documento imprimible (RF-6). Portabilidad por carpeta (RNF-6).
"""
from __future__ import annotations

from .excel_export import plan_to_xlsx_bytes  # noqa: F401
from .html_export import (  # noqa: F401
    session_body_html,
    to_html_plan,
    to_html_plan_matrix,
    to_html_session,
)
from .json_repository import JsonFileRepository  # noqa: F401
from .pdf_export import (  # noqa: F401
    is_pdf_available,
    to_pdf_plan,
    to_pdf_session,
)
from .plan import (  # noqa: F401
    PlanRef,
    SessionDoc,
    TrainingPlan,
    plan_from_dict,
    plan_to_dict,
)
from .repository import PlanRepository  # noqa: F401

__all__ = [
    "PlanRepository", "JsonFileRepository",
    "TrainingPlan", "SessionDoc", "PlanRef", "plan_to_dict", "plan_from_dict",
    "to_html_session", "to_html_plan", "to_html_plan_matrix", "session_body_html",
    "is_pdf_available", "to_pdf_session", "to_pdf_plan",
    "plan_to_xlsx_bytes",
]
