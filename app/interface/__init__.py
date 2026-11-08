"""U5 (parte interfaz) — app web local (RF-2). FastAPI opcional (grupo web)."""
from __future__ import annotations

from .webapp import create_app  # noqa: F401

__all__ = ["create_app"]
