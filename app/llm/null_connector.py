"""Conector LLM por defecto: no hace nada (offline, RNF-2).

Permite que todo el flujo determinista funcione sin red ni dependencias.
``build_connector`` ahora construye el conector real según la config, o una
cadena de respaldo, cayendo siempre a NullConnector al final.
"""
from __future__ import annotations

from periodization_engine.errors import DomainError, DomainErrorKind, Err, Result

from .connector import LlmConfig


class NullConnector:
    def is_enabled(self) -> bool:
        return False

    def complete(self, prompt: str, config: LlmConfig | None = None) -> Result[str]:
        return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL,
                               detail="LLM desactivado | LLM disabled"))


def _single_connector(config: LlmConfig):
    """Construye un conector concreto según config.provider."""
    provider = (config.provider or "none").lower()
    if provider in ("none", ""):
        return NullConnector()
    if provider == "openai":
        from .openai_connector import OpenAiConnector
        return OpenAiConnector(config)
    if provider == "anthropic":
        from .anthropic_connector import AnthropicConnector
        return AnthropicConnector(config)
    if provider == "ollama":
        from .ollama_connector import OllamaConnector
        return OllamaConnector(config)
    return NullConnector()


def build_connector(config: LlmConfig):
    """Factory principal.

    - provider "chain" -> cadena de respaldo Ollama -> OpenAI -> Null (orden por
      defecto; configurable vía AGENTE_LLM_CHAIN separado por comas).
    - provider concreto (openai/anthropic/ollama) -> ese conector.
    - "none"/desconocido -> NullConnector (offline).

    Siempre devuelve un objeto con is_enabled()/complete(); nunca lanza.
    """
    provider = (config.provider or "none").lower()
    if provider == "chain":
        from .chain_connector import ChainConnector

        order = [p.strip() for p in (config.chain or "ollama,openai").split(",") if p.strip()]
        connectors = [_single_connector(LlmConfig(
            provider=p, model=config.model,
            api_key_env_var=config.api_key_env_var, base_url=config.base_url,
        )) for p in order]
        connectors.append(NullConnector())
        return ChainConnector(connectors)
    return _single_connector(config)
