"""Conector Ollama (modelos locales, gratis, offline) — RF-10, D5.

Habla con un servidor Ollama local (por defecto http://localhost:11434) vía su
API HTTP, usando solo stdlib (urllib) para no añadir dependencias. is_enabled()
hace un ping rápido; si Ollama no está corriendo, el agente sigue determinista.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from periodization_engine.errors import (
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)

from .connector import LlmConfig

_DEFAULT_URL = "http://localhost:11434"


class OllamaConnector:
    def __init__(self, config: LlmConfig):
        self._config = config
        self._base = (config.base_url or _DEFAULT_URL).rstrip("/")

    def is_enabled(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self._base}/api/tags", timeout=1.5) as r:
                return r.status == 200
        except (urllib.error.URLError, OSError, ValueError):
            return False

    def complete(self, prompt: str, config: LlmConfig | None = None) -> Result[str]:
        cfg = config or self._config
        payload = json.dumps({
            "model": cfg.model or "llama3",
            "prompt": prompt,
            "stream": False,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self._base}/api/generate", data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            return Ok(data.get("response", ""))
        except (urllib.error.URLError, OSError, ValueError) as e:
            return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL,
                                   detail=f"Ollama no disponible: {e} | Ollama unavailable"))
