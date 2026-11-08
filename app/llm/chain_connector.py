"""Conector de cadena de respaldo (fallback) — RF-10.

Intenta una lista ordenada de conectores y usa el primero habilitado. Permite
"mezclar" proveedores con prioridad, p. ej. Ollama (gratis/local) -> OpenAI
(si hay clave) -> Null (determinista, siempre funciona). El agente nunca se
queda sin respuesta: si ninguno está, is_enabled()=False y el flujo sigue
determinista.
"""
from __future__ import annotations

from periodization_engine.errors import DomainError, DomainErrorKind, Err, Result

from .connector import LlmConfig


class ChainConnector:
    def __init__(self, connectors: list):
        self._connectors = connectors

    def _active(self):
        for c in self._connectors:
            try:
                if c.is_enabled():
                    return c
            except Exception:
                continue
        return None

    def is_enabled(self) -> bool:
        return self._active() is not None

    def active_name(self) -> str:
        c = self._active()
        return type(c).__name__ if c else "none"

    def complete(self, prompt: str, config: LlmConfig | None = None) -> Result[str]:
        c = self._active()
        if c is None:
            return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL,
                                   detail="ningún LLM disponible | no LLM available"))
        return c.complete(prompt, config)
