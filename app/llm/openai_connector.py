"""Conector OpenAI (RF-10, D5). Opcional, import perezoso.

Se activa SOLO si: provider=openai, el SDK `openai` está instalado, y la clave
se resuelve de la variable de entorno indicada en LlmConfig (RNF-3: la clave
nunca vive en código ni en disco). Si algo falta, is_enabled()=False y el agente
sigue en modo determinista.
"""
from __future__ import annotations

import importlib.util

from periodization_engine.errors import (
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)

from .connector import LlmConfig


class OpenAiConnector:
    def __init__(self, config: LlmConfig):
        self._config = config

    def is_enabled(self) -> bool:
        sdk = importlib.util.find_spec("openai") is not None
        return bool(sdk and self._config.resolve_api_key())

    def complete(self, prompt: str, config: LlmConfig | None = None) -> Result[str]:
        cfg = config or self._config
        if not self.is_enabled():
            return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL,
                                   detail="OpenAI no disponible (SDK o clave) | OpenAI unavailable"))
        from openai import OpenAI  # import perezoso

        client = OpenAI(api_key=cfg.resolve_api_key())
        resp = client.chat.completions.create(
            model=cfg.model or "gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return Ok(resp.choices[0].message.content or "")
