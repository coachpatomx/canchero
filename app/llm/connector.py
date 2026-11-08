"""Conector LLM genérico y opcional (D5, RF-10, RNF-3).

La clave de API se lee SIEMPRE de una variable de entorno cuyo NOMBRE se guarda
en LlmConfig; la clave literal nunca vive en código ni en disco de datos (RNF-3).
Por defecto el agente usa NullConnector y funciona 100% offline (RNF-2).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from periodization_engine.errors import Result


@dataclass(frozen=True)
class LlmConfig:
    provider: str = "none"            # "none"|"openai"|"anthropic"|"ollama"|"chain"
    model: str = ""
    api_key_env_var: str = ""         # NOMBRE de la variable de entorno, no la clave
    base_url: str = ""                # para Ollama u otros endpoints locales
    chain: str = ""                   # orden de la cadena, p. ej. "ollama,openai"

    @staticmethod
    def from_env() -> "LlmConfig":
        """Construye la config desde el entorno. Si no hay provider, queda 'none'."""
        return LlmConfig(
            provider=os.environ.get("AGENTE_LLM_PROVIDER", "none"),
            model=os.environ.get("AGENTE_LLM_MODEL", ""),
            api_key_env_var=os.environ.get("AGENTE_LLM_API_KEY_VAR", ""),
            base_url=os.environ.get("AGENTE_LLM_BASE_URL", ""),
            chain=os.environ.get("AGENTE_LLM_CHAIN", ""),
        )

    def resolve_api_key(self) -> str | None:
        """Lee la clave de la variable de entorno indicada. None si no existe."""
        if not self.api_key_env_var:
            return None
        return os.environ.get(self.api_key_env_var)


class LlmConnector(Protocol):
    def is_enabled(self) -> bool: ...
    def complete(self, prompt: str, config: LlmConfig) -> Result[str]: ...
