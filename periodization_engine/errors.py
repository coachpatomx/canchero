"""Errores de dominio y tipo Result para el motor de periodización.

El motor nunca lanza excepciones para el flujo de control esperado: devuelve
``Result`` (``Ok`` | ``Err``). Esto cumple RNF-5 (coherencia) y facilita que la
capa de interfaz (U5) traduzca el error a un mensaje de usuario bilingüe.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar, Union

T = TypeVar("T")


class DomainErrorKind(str, Enum):
    """Variantes de error de dominio (clave estable en inglés)."""

    INVALID_SEASON_DURATION = "invalid_season_duration"
    INCONSISTENT_DATES = "inconsistent_dates"
    UNKNOWN_MODEL = "unknown_model"
    INVALID_MODEL_RULES = "invalid_model_rules"
    UNSATISFIABLE_PLAN = "unsatisfiable_plan"


# Mensajes bilingües por variante (D6). El motor transporta ambos; U5 elige.
_MESSAGES: dict[DomainErrorKind, dict[str, str]] = {
    DomainErrorKind.INVALID_SEASON_DURATION: {
        "es": "La duración de la temporada es inválida o demasiado corta.",
        "en": "The season duration is invalid or too short.",
    },
    DomainErrorKind.INCONSISTENT_DATES: {
        "es": "Las fechas de la temporada son inconsistentes.",
        "en": "The season dates are inconsistent.",
    },
    DomainErrorKind.UNKNOWN_MODEL: {
        "es": "El modelo de periodización solicitado no existe.",
        "en": "The requested periodization model does not exist.",
    },
    DomainErrorKind.INVALID_MODEL_RULES: {
        "es": "Las reglas del modelo personalizado son inválidas.",
        "en": "The custom model rules are invalid.",
    },
    DomainErrorKind.UNSATISFIABLE_PLAN: {
        "es": "El plan no se puede satisfacer con los parámetros dados.",
        "en": "The plan cannot be satisfied with the given parameters.",
    },
}


@dataclass(frozen=True)
class DomainError:
    """Error de dominio con mensaje bilingüe y detalle opcional."""

    kind: DomainErrorKind
    detail: str = ""

    @property
    def message_es(self) -> str:
        return _MESSAGES[self.kind]["es"]

    @property
    def message_en(self) -> str:
        return _MESSAGES[self.kind]["en"]


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    @property
    def is_ok(self) -> bool:
        return True


@dataclass(frozen=True)
class Err:
    error: DomainError

    @property
    def is_ok(self) -> bool:
        return False


Result = Union[Ok[T], Err]
