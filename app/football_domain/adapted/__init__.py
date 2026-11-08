"""Submódulo de adaptaciones de fútbol adaptado (RF-8)."""
from __future__ import annotations

from .apply import apply_adaptations, is_adapted  # noqa: F401
from .profiles import (  # noqa: F401
    AMPUTEE,
    BLIND,
    CEREBRAL_PALSY,
    DOWN,
    PROFILES,
    AdaptationProfile,
    CommunicationMode,
    DisabilityDomain,
    RuleNote,
)

__all__ = [
    "apply_adaptations", "is_adapted",
    "AdaptationProfile", "RuleNote", "DisabilityDomain", "CommunicationMode",
    "PROFILES", "BLIND", "CEREBRAL_PALSY", "DOWN", "AMPUTEE",
]
