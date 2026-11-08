"""Perfiles de adaptación de fútbol adaptado (RF-8).

4 modalidades con contenido real en v1 (decisión del usuario): ciegos (fútbol 5),
parálisis cerebral (fútbol 7), Down/discapacidad intelectual, amputados.

FUENTES OFICIALES verificadas 2026-11-07 (reglas reformuladas para cumplir
licencias; cada perfil cita su federación en `governing_body`/`source_url`):
- Ciegos: IBSA — Blind Football Laws of the Game (ciclo 2025-2029).
- PC: IFCPF — International Federation of CP Football (paralímpico desde 1984).
- Down/ID: Virtus — Int. Sports Federation for Persons with Intellectual Disability.
- Amputados: WAFF — World Amputee Football Federation.

Reglas marcadas `validated=True` cuando provienen de la fuente oficial citada.
Donde persista duda de aplicación local, se deja `validated=False` con nota.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from periodization_engine import I18nText

from ..exercise import Material


class DisabilityDomain(str, Enum):
    VISUAL = "visual"
    CEREBRAL_PALSY = "cerebral_palsy"
    INTELLECTUAL = "intellectual"
    AMPUTEE = "amputee"


class CommunicationMode(str, Enum):
    SONOROUS = "sonorous"
    VERBAL = "verbal"
    VISUAL = "visual"
    SIGN = "sign"


@dataclass(frozen=True)
class RuleNote:
    text: I18nText
    validated: bool = False


@dataclass(frozen=True)
class AdaptationProfile:
    disability_domain: DisabilityDomain
    classification: tuple[str, ...]
    material_adaptations: tuple[Material, ...]
    rule_adaptations: tuple[RuleNote, ...]
    communication_modes: tuple[CommunicationMode, ...]
    coaching_notes: I18nText
    governing_body: str = ""        # federación oficial
    source_url: str = ""            # reglamento de referencia
    diagram_markers: tuple[str, ...] = ()


# --------------------------------------------------------------------------- #
# VISUAL (ciegos) — IBSA Blind Football Laws of the Game 2025-2029
# --------------------------------------------------------------------------- #
BLIND = AdaptationProfile(
    disability_domain=DisabilityDomain.VISUAL,
    classification=("B1",),  # jugadores de campo B1; portero puede ser B2/B3 o vidente
    material_adaptations=(
        Material("sonorous_ball", I18nText("Balón sonoro", "Sonorous ball"), 1, adapted=True),
        Material("eyeshade", I18nText("Antifaz", "Eyeshade"), 8, adapted=True),
        Material("side_boards", I18nText("Vallas laterales", "Side boards"), 2, adapted=True),
        Material("guide", I18nText("Guía / llamador", "Guide / caller"), 1, adapted=True),
    ),
    rule_adaptations=(
        RuleNote(I18nText("5 por equipo: 4 jugadores de campo B1 + 1 portero (vidente o B2/B3)",
                          "5 per team: 4 B1 outfield players + 1 goalkeeper (sighted or B2/B3)"),
                 validated=True),
        RuleNote(I18nText("Jugadores de campo con antifaz obligatorio; el portero no sale de su área",
                          "Outfield players wear mandatory eyeshades; goalkeeper stays in the area"),
                 validated=True),
        RuleNote(I18nText("Decir 'voy' al ir a disputar el balón (seguridad)",
                          "Say 'voy' when going to challenge for the ball (safety)"),
                 validated=True),
        RuleNote(I18nText("Vallas laterales: el balón no sale por las bandas",
                          "Side boards: ball does not go out on the sides"),
                 validated=True),
        RuleNote(I18nText("Orientación por sonido del balón y de las llamadas del guía/entrenador",
                          "Orientation via ball sound and guide/coach calls"),
                 validated=True),
    ),
    communication_modes=(CommunicationMode.SONOROUS, CommunicationMode.VERBAL),
    coaching_notes=I18nText(
        "Priorizar orientación espacial por sonido; consignas verbales claras y constantes.",
        "Prioritize sound-based spatial orientation; clear, constant verbal cues.",
    ),
    governing_body="IBSA",
    source_url="https://ibsasport.org/sports/football/",
    diagram_markers=("side_boards", "guide", "zones"),
)

# --------------------------------------------------------------------------- #
# PARÁLISIS CEREBRAL (fútbol 7) — IFCPF
# --------------------------------------------------------------------------- #
CEREBRAL_PALSY = AdaptationProfile(
    disability_domain=DisabilityDomain.CEREBRAL_PALSY,
    classification=("FT1", "FT2", "FT3"),
    material_adaptations=(),
    rule_adaptations=(
        RuleNote(I18nText("7 por equipo; composición: al menos un FT1 y como máximo un FT3 en campo",
                          "7 per team; on-field: at least one FT1 and at most one FT3"),
                 validated=True),
        RuleNote(I18nText("Sin fuera de juego", "No offside"), validated=True),
        RuleNote(I18nText("Saque de banda permitido con una mano (rodar el balón)",
                          "Throw-in allowed with one hand (rolling the ball)"), validated=True),
        RuleNote(I18nText("Dos tiempos de 30 minutos", "Two 30-minute halves"), validated=True),
        RuleNote(I18nText("Campo y portería reducidos respecto al fútbol 11",
                          "Reduced field and goal vs 11-a-side"), validated=True),
    ),
    communication_modes=(CommunicationMode.VERBAL, CommunicationMode.VISUAL),
    coaching_notes=I18nText(
        "Adaptar ritmo y complejidad a la clasificación funcional (FT1–FT3). Verificar composición de equipo.",
        "Adapt pace and complexity to functional class (FT1–FT3). Check team composition rule.",
    ),
    governing_body="IFCPF",
    source_url="https://www.ifcpf.com/what-is-cp-football",
)

# --------------------------------------------------------------------------- #
# DISCAPACIDAD INTELECTUAL / DOWN — Virtus
# --------------------------------------------------------------------------- #
DOWN = AdaptationProfile(
    disability_domain=DisabilityDomain.INTELLECTUAL,
    # Clases Virtus: II1 (discapacidad intelectual), II2 (DI + impedimento
    # adicional significativo — aquí entra síndrome de Down), II3 (autismo sin DI).
    classification=("II1", "II2", "II3"),
    material_adaptations=(),
    rule_adaptations=(
        RuleNote(I18nText("Elegibilidad Virtus: CI ≤ 75 y limitaciones adaptativas antes de los 22 años",
                          "Virtus eligibility: IQ ≤ 75 and adaptive limitations before age 22"),
                 validated=True),
        RuleNote(I18nText("Síndrome de Down se clasifica como II2 (discapacidad intelectual + impedimento adicional)",
                          "Down syndrome classifies as II2 (intellectual disability + additional impairment)"),
                 validated=True),
        RuleNote(I18nText("Se juega sobre reglas FIFA con adaptaciones de ritmo/consignas según el evento",
                          "Played on FIFA rules with pace/cue adaptations per event"),
                 validated=False),
    ),
    communication_modes=(CommunicationMode.VERBAL, CommunicationMode.VISUAL),
    coaching_notes=I18nText(
        "Instrucciones simples y progresivas; repetición y refuerzo positivo. Formato/nº de jugadores según evento.",
        "Simple, progressive instructions; repetition and positive reinforcement. Format/number per event.",
    ),
    governing_body="Virtus",
    source_url="https://virtus.sport/virtus-eligibility-procedures-guidance",
)

# --------------------------------------------------------------------------- #
# AMPUTADOS — WAFF
# --------------------------------------------------------------------------- #
AMPUTEE = AdaptationProfile(
    disability_domain=DisabilityDomain.AMPUTEE,
    classification=("outfield", "goalkeeper"),
    material_adaptations=(
        Material("forearm_crutches", I18nText("Muletas de antebrazo (aluminio)",
                                              "Aluminium forearm crutches"), 12, adapted=True),
    ),
    rule_adaptations=(
        RuleNote(I18nText("7 por equipo: 6 jugadores de campo + 1 portero",
                          "7 per team: 6 outfield players + 1 goalkeeper"), validated=True),
        RuleNote(I18nText("Jugadores de campo: amputación de una pierna; juegan con muletas de antebrazo y sin prótesis",
                          "Outfield: single-leg amputees; play on forearm crutches without prosthesis"),
                 validated=True),
        RuleNote(I18nText("Portero: amputación de un brazo", "Goalkeeper: single-arm amputee"),
                 validated=True),
        RuleNote(I18nText("La muleta no puede usarse para jugar el balón intencionalmente",
                          "The crutch may not be used to intentionally play the ball"), validated=True),
    ),
    communication_modes=(CommunicationMode.VERBAL,),
    coaching_notes=I18nText(
        "Cuidar equilibrio y apoyos; gestionar fatiga por uso de muletas. En competición doméstica puede variar (prótesis/amputados de brazo en campo).",
        "Mind balance and supports; manage crutch-use fatigue. Domestic play may vary (prosthesis / arm-amputees outfield).",
    ),
    governing_body="WAFF",
    source_url="https://amputeefootball.org/",
)


PROFILES: dict[str, AdaptationProfile] = {
    "blind_5": BLIND,
    "cp_7": CEREBRAL_PALSY,
    "down": DOWN,
    "amputee": AMPUTEE,
}
