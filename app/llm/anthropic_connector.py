"""Conector Anthropic (Claude) — RF-10, D5. Opcional, import perezoso.

Mismo contrato que OpenAI: se activa si el SDK `anthropic` está y la clave se
resuelve de entorno. Cambiar de OpenAI a Anthropic = cambiar AGENTE_LLM_PROVIDER.
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


class AnthropicConnector:
    def __init__(self, config: LlmConfig):
        self._config = config

    def is_enabled(self) -> bool:
        sdk = importlib.util.find_spec("anthropic") is not None
        return bool(sdk and self._config.resolve_api_key())

    def complete(self, prompt: str, config: LlmConfig | None = None) -> Result[str]:
        cfg = config or self._config
        if not self.is_enabled():
            return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL,
                                   detail="Anthropic no disponible | Anthropic unavailable"))
        import anthropic  # import perezoso

        client = anthropic.Anthropic(api_key=cfg.resolve_api_key())
        msg = client.messages.create(
            model=cfg.model or "claude-3-5-haiku-latest",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        # El contenido viene como lista de bloques; concatenar el texto.
        parts = [b.text for b in msg.content if getattr(b, "type", "") == "text"]
        return Ok("".join(parts))
