"""Serialización de Exercise y FootballFormat a/desde dict JSON-nativo (RNF-6).

Para que U4 persista en disco. Round-trip: from_dict(to_dict(x)) == x.
"""
from __future__ import annotations

from dataclasses import asdict

from periodization_engine import I18nText

from .adapted.profiles import (
    AdaptationProfile,
    CommunicationMode,
    DisabilityDomain,
    RuleNote,
)
from .exercise import (
    AspectTags,
    Constraint,
    DiagramSpec,
    Exercise,
    LoadSpec,
    Material,
    PlayerSetup,
    SpaceSpec,
)
from .formats import FootballFormat, Position
from .game_model import (
    DidacticStrategy,
    Fundamental,
    GameModelRef,
    GamePhase,
    SpaceCategory,
    TaskType,
)


def _enums_to_values(obj):
    if isinstance(obj, dict):
        return {k: _enums_to_values(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_enums_to_values(v) for v in obj]
    if hasattr(obj, "value") and not isinstance(obj, (str, int, float, bool)):
        return obj.value
    return obj


# --------------------------------------------------------------------------- #
# Exercise
# --------------------------------------------------------------------------- #
def exercise_to_dict(ex: Exercise) -> dict:
    return _enums_to_values(asdict(ex))


def _i18n(d: dict) -> I18nText:
    return I18nText(es=d["es"], en=d["en"])


def _material(d: dict) -> Material:
    return Material(key=d["key"], name=_i18n(d["name"]),
                    quantity=d["quantity"], adapted=d["adapted"])


def exercise_from_dict(d: dict) -> Exercise:
    return Exercise(
        id=d["id"],
        name=_i18n(d["name"]),
        task_type=TaskType(d["task_type"]),
        didactic_strategy=DidacticStrategy(d["didactic_strategy"]),
        objective=_i18n(d["objective"]),
        duration_min=d["duration_min"],
        space=SpaceSpec(d["space"]["length_m"], d["space"]["width_m"],
                        SpaceCategory(d["space"]["category"])),
        n_players=PlayerSetup(**d["n_players"]),
        load=LoadSpec(**d["load"]),
        aspects=AspectTags(
            technical=tuple(d["aspects"]["technical"]),
            tactical=tuple(d["aspects"]["tactical"]),
            physical=tuple(d["aspects"]["physical"]),
            psychological=tuple(d["aspects"]["psychological"]),
        ),
        diagram_spec=DiagramSpec(
            players_a=d["diagram_spec"]["players_a"],
            players_b=d["diagram_spec"]["players_b"],
            cones=d["diagram_spec"]["cones"],
            balls=d["diagram_spec"]["balls"],
            zones=tuple(d["diagram_spec"]["zones"]),
            arrows=tuple(d["diagram_spec"]["arrows"]),
            adapted_markers=tuple(d["diagram_spec"]["adapted_markers"]),
        ),
        materials=tuple(_material(m) for m in d["materials"]),
        game_model_refs=tuple(
            GameModelRef(GamePhase(r["phase"]), r["moment"], Fundamental(r["fundamental"]))
            for r in d["game_model_refs"]
        ),
        constraints=tuple(
            Constraint(_i18n(c["description"]), c["gradient"]) for c in d["constraints"]
        ),
        lang_available=tuple(d["lang_available"]),
        applied_adaptations=tuple(d["applied_adaptations"]),
    )


# --------------------------------------------------------------------------- #
# FootballFormat
# --------------------------------------------------------------------------- #
def format_to_dict(fmt: FootballFormat) -> dict:
    return _enums_to_values(asdict(fmt))


def _rule(d: dict) -> RuleNote:
    return RuleNote(text=_i18n(d["text"]), validated=d["validated"])


def _profile(d: dict | None) -> AdaptationProfile | None:
    if d is None:
        return None
    return AdaptationProfile(
        disability_domain=DisabilityDomain(d["disability_domain"]),
        classification=tuple(d["classification"]),
        material_adaptations=tuple(_material(m) for m in d["material_adaptations"]),
        rule_adaptations=tuple(_rule(r) for r in d["rule_adaptations"]),
        communication_modes=tuple(CommunicationMode(c) for c in d["communication_modes"]),
        coaching_notes=_i18n(d["coaching_notes"]),
        governing_body=d.get("governing_body", ""),
        source_url=d.get("source_url", ""),
        diagram_markers=tuple(d["diagram_markers"]),
    )


def format_from_dict(d: dict) -> FootballFormat:
    return FootballFormat(
        id=d["id"],
        name=_i18n(d["name"]),
        players_on_field=d["players_on_field"],
        field_length_m=d["field_length_m"],
        field_width_m=d["field_width_m"],
        match_duration_min=d["match_duration_min"],
        is_adapted=d["is_adapted"],
        adaptation_profile=_profile(d["adaptation_profile"]),
        rules_notes=tuple(_rule(r) for r in d["rules_notes"]),
        positions=tuple(Position(p["key"], _i18n(p["name"])) for p in d["positions"]),
    )
