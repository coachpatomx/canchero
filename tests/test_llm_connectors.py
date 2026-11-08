"""Tests de los conectores LLM (U5). No requieren red ni claves reales:
verifican el comportamiento de habilitación/degradación."""
from __future__ import annotations

import os

from app.llm import (
    AnthropicConnector,
    ChainConnector,
    LlmConfig,
    NullConnector,
    OllamaConnector,
    OpenAiConnector,
    build_connector,
)
from periodization_engine.errors import Err


def test_null_connector_disabled():
    c = NullConnector()
    assert c.is_enabled() is False
    assert isinstance(c.complete("hola"), Err)


def test_build_none_is_null():
    c = build_connector(LlmConfig(provider="none"))
    assert isinstance(c, NullConnector)


def test_openai_disabled_without_key(monkeypatch):
    monkeypatch.delenv("TEST_OPENAI_KEY", raising=False)
    cfg = LlmConfig(provider="openai", api_key_env_var="TEST_OPENAI_KEY")
    c = build_connector(cfg)
    assert isinstance(c, OpenAiConnector)
    # Sin clave en entorno -> deshabilitado (no intenta llamar).
    assert c.is_enabled() is False


def test_openai_config_reads_key_from_env(monkeypatch):
    monkeypatch.setenv("TEST_OPENAI_KEY", "sk-fake")
    cfg = LlmConfig(provider="openai", api_key_env_var="TEST_OPENAI_KEY")
    # La clave se resuelve del entorno, nunca del repr de la config.
    assert cfg.resolve_api_key() == "sk-fake"
    assert "sk-fake" not in repr(cfg)


def test_anthropic_disabled_without_key(monkeypatch):
    monkeypatch.delenv("TEST_ANTHROPIC_KEY", raising=False)
    c = build_connector(LlmConfig(provider="anthropic", api_key_env_var="TEST_ANTHROPIC_KEY"))
    assert isinstance(c, AnthropicConnector)
    assert c.is_enabled() is False


def test_ollama_disabled_when_server_down():
    # Apunta a un puerto donde no hay nada: is_enabled debe ser False, sin lanzar.
    c = build_connector(LlmConfig(provider="ollama", base_url="http://localhost:59999"))
    assert isinstance(c, OllamaConnector)
    assert c.is_enabled() is False


def test_chain_falls_back_to_null():
    # Cadena ollama(apagado) -> openai(sin clave) -> Null: nunca habilitado, no lanza.
    cfg = LlmConfig(provider="chain", chain="ollama,openai",
                    base_url="http://localhost:59999", api_key_env_var="NOPE_KEY")
    c = build_connector(cfg)
    assert isinstance(c, ChainConnector)
    assert c.is_enabled() is False
    assert isinstance(c.complete("hola"), Err)
    assert c.active_name() == "none"
