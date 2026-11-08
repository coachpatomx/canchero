"""Operaciones de seguimiento individual (U6). Puras/inmutables."""
from __future__ import annotations

from dataclasses import replace

from periodization_engine import I18nText
from periodization_engine.errors import (
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)

from .models import (
    CATEGORY_PRIORITY,
    IndividualObjective,
    Observation,
    Player,
    PlayerDossier,
    PlayerSpec,
    Roster,
)

_counter = {"n": 0}


def _next(prefix: str) -> str:
    _counter["n"] += 1
    return f"{prefix}-{_counter['n']:05d}"


def create_roster(team_name: str, specs: list[PlayerSpec]) -> Roster:
    players = tuple(
        Player(id=_next("ply"), name=s.name, position_key=s.position_key)
        for s in specs
    )
    return Roster(team_name=team_name, players=players)


def add_player(roster: Roster, spec: PlayerSpec) -> Roster:
    player = Player(id=_next("ply"), name=spec.name, position_key=spec.position_key)
    return replace(roster, players=roster.players + (player,))


def _find(roster: Roster, player_id: str) -> Player | None:
    return next((p for p in roster.players if p.id == player_id), None)


def _replace_player(roster: Roster, updated: Player) -> Roster:
    players = tuple(updated if p.id == updated.id else p for p in roster.players)
    return replace(roster, players=players)


def set_individual_objectives(
    roster: Roster, player_id: str, objectives: list[IndividualObjective]
) -> Result[Roster]:
    player = _find(roster, player_id)
    if player is None:
        return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL, detail=f"player {player_id}"))
    updated = replace(player, objectives=tuple(objectives))
    return Ok(_replace_player(roster, updated))


def update_progress(
    roster: Roster, player_id: str, objective_id: str, progress_pct: int
) -> Result[Roster]:
    if not (0 <= progress_pct <= 100):
        return Err(DomainError(DomainErrorKind.INVALID_MODEL_RULES,
                               detail="progress fuera de 0..100"))
    player = _find(roster, player_id)
    if player is None:
        return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL, detail=f"player {player_id}"))
    found = False
    new_objs = []
    for o in player.objectives:
        if o.id == objective_id:
            new_objs.append(replace(o, progress_pct=progress_pct))
            found = True
        else:
            new_objs.append(o)
    if not found:
        return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL, detail=f"objective {objective_id}"))
    return Ok(_replace_player(roster, replace(player, objectives=tuple(new_objs))))


def add_observation(
    roster: Roster, player_id: str, session_ref: str, note: I18nText, created_at: str
) -> Result[Roster]:
    player = _find(roster, player_id)
    if player is None:
        return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL, detail=f"player {player_id}"))
    obs = Observation(id=_next("obs"), session_ref=session_ref, note=note, created_at=created_at)
    updated = replace(player, observations=player.observations + (obs,))
    return Ok(_replace_player(roster, updated))


def get_player_dossier(roster: Roster, player_id: str) -> Result[PlayerDossier]:
    player = _find(roster, player_id)
    if player is None:
        return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL, detail=f"player {player_id}"))
    pot = tuple(o for o in player.objectives if o.category.value == "potentiate")
    imp = tuple(o for o in player.objectives if o.category.value == "improve")
    eli = tuple(o for o in player.objectives if o.category.value == "eliminate")
    mastered = sum(1 for o in player.objectives if o.mastered)
    return Ok(PlayerDossier(player=player, potentiate=pot, improve=imp,
                            eliminate=eli, mastered_count=mastered))


def get_session_individual_goals(roster: Roster, lang: str = "es") -> list[dict]:
    """Objetivos no dominados a imprimir en la sesión (plantilla mejorada).

    Formato ligero compatible con SessionDoc.individual_goals (U4/U5).
    Orden: eliminate -> improve -> potentiate.
    """
    rows: list[tuple[int, dict]] = []
    for p in roster.players:
        for o in p.objectives:
            if o.mastered:
                continue
            goal = o.content.es if lang == "es" else o.content.en
            rows.append((
                CATEGORY_PRIORITY[o.category],
                {"player": p.name, "position": p.position_key,
                 "category": o.category.value, "goal": goal},
            ))
    rows.sort(key=lambda r: r[0])
    return [r[1] for r in rows]
