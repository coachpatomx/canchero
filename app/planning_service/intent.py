"""Parseo determinista de contenido/condicionantes de una petición en lenguaje
natural (RF-11), sin LLM.

Mapea palabras clave (es/en) a aspectos, estrategia didáctica y categoría de
espacio. Si el LLM está activo puede ayudar a extraer intención, pero el
resultado SIEMPRE se valida contra este catálogo del dominio.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.football_domain.game_model import DidacticStrategy, SpaceCategory


@dataclass(frozen=True)
class ParsedIntent:
    technical: tuple[str, ...] = ()
    tactical: tuple[str, ...] = ()
    physical: tuple[str, ...] = ()
    space: SpaceCategory | None = None
    strategy: DidacticStrategy | None = None
    timeframe: str = ""   # "this_week" si se detecta

    @property
    def has_content(self) -> bool:
        return bool(self.technical or self.tactical or self.physical)


# Catálogo de palabras clave -> contenido (bilingüe).
_TECHNICAL = {
    "conduccion": "driving", "conducción": "driving", "driving": "driving",
    "pase": "passing", "pass": "passing", "passing": "passing",
    "control": "ball_control", "tiro": "shooting", "shooting": "shooting",
    "regate": "dribbling", "dribbling": "dribbling",
}
_TACTICAL = {
    "presion": "pressing", "presión": "pressing", "pressing": "pressing",
    "posesion": "possession", "posesión": "possession", "possession": "possession",
    "transicion": "transition", "transición": "transition", "transition": "transition",
}
_PHYSICAL = {
    "resistencia": "endurance", "endurance": "endurance",
    "velocidad": "speed", "speed": "speed",
    "fuerza": "strength", "strength": "strength",
}
_SPACE = {
    "reducido": SpaceCategory.REDUCED, "reduced": SpaceCategory.REDUCED,
    "pequeño": SpaceCategory.SMALL, "pequeno": SpaceCategory.SMALL, "small": SpaceCategory.SMALL,
    "medio": SpaceCategory.MEDIUM, "medium": SpaceCategory.MEDIUM,
    "grande": SpaceCategory.LARGE, "large": SpaceCategory.LARGE,
    "real": SpaceCategory.REAL,
}
_TIMEFRAME = ("esta semana", "this week")


def parse_intent(text: str) -> ParsedIntent:
    t = text.lower()
    tech = tuple(dict.fromkeys(v for k, v in _TECHNICAL.items() if k in t))
    tac = tuple(dict.fromkeys(v for k, v in _TACTICAL.items() if k in t))
    phy = tuple(dict.fromkeys(v for k, v in _PHYSICAL.items() if k in t))

    space = None
    for k, v in _SPACE.items():
        if k in t:
            space = v
            break

    strategy = None
    if space in (SpaceCategory.REDUCED, SpaceCategory.SMALL):
        strategy = DidacticStrategy.POSITION_GAMES
    elif space == SpaceCategory.REAL:
        strategy = DidacticStrategy.SSP

    timeframe = "this_week" if any(tf in t for tf in _TIMEFRAME) else ""

    return ParsedIntent(technical=tech, tactical=tac, physical=phy,
                        space=space, strategy=strategy, timeframe=timeframe)
