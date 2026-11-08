"""Exportador PDF nativo opcional (WeasyPrint) — RF-6.

PDF disponible con un clic SI WeasyPrint está instalado. Si no, degradación
limpia: is_pdf_available()==False y to_pdf_* devuelve Err (nunca lanza
ImportError), y el usuario usa la vía HTML del navegador. Import PEREZOSO para
no romper el arranque offline (RNF-2).
"""
from __future__ import annotations

import importlib.util

from periodization_engine import I18nText
from periodization_engine.errors import (
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)

from .html_export import to_html_plan, to_html_session
from .plan import SessionDoc, TrainingPlan

_UNAVAILABLE = DomainError(
    DomainErrorKind.UNKNOWN_MODEL,
    detail=(
        "WeasyPrint no instalado. Usa 'Imprimir -> Guardar como PDF' en el "
        "navegador, o instala el extra: pip install '.[pdf]'. | WeasyPrint not "
        "installed; use browser 'Print -> Save as PDF' or install the pdf extra."
    ),
)


def is_pdf_available() -> bool:
    """True si WeasyPrint se puede importar (sin importarlo todavía)."""
    return importlib.util.find_spec("weasyprint") is not None


def _html_to_pdf(html: str) -> Result[bytes]:
    if not is_pdf_available():
        return Err(_UNAVAILABLE)
    import weasyprint  # import perezoso, solo si está disponible

    pdf_bytes = weasyprint.HTML(string=html).write_pdf()
    return Ok(pdf_bytes)


def to_pdf_session(session: SessionDoc, lang: str = "es") -> Result[bytes]:
    return _html_to_pdf(to_html_session(session, lang))


def to_pdf_plan(plan: TrainingPlan, lang: str = "es") -> Result[bytes]:
    return _html_to_pdf(to_html_plan(plan, lang))
