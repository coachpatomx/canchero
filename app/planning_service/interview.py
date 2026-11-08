"""Máquina de entrevista determinista (RF-3): construye un PlanInput paso a paso
cuando no hay macro o el usuario prefiere responder preguntas."""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from periodization_engine import CompetitionType, SeasonParams, StartFitness

from .session_request import PlanInput

# Preguntas en orden (clave, es, en).
_QUESTIONS = [
    ("duration_weeks", "¿Cuántas semanas dura la temporada?", "How many weeks is the season?"),
    ("training_days_per_week", "¿Cuántos días entrenan por semana?", "Training days per week?"),
    ("matches_per_week", "¿Cuántos partidos por semana (0, 1 o 2)?", "Matches per week (0,1,2)?"),
    ("model_id", "¿Qué modelo de periodización? (traditional/blocks/atr/tactical/structured/football_gonzalez)",
     "Which periodization model?"),
    ("format_id", "¿Qué formato de fútbol? (football_11/blind_5/cp_7/down/amputee/...)",
     "Which football format?"),
]


@dataclass(frozen=True)
class InterviewState:
    answers: dict = field(default_factory=dict)
    step: int = 0

    @property
    def done(self) -> bool:
        return self.step >= len(_QUESTIONS)

    def current_question(self, lang: str = "es") -> str | None:
        if self.done:
            return None
        _, es, en = _QUESTIONS[self.step]
        return es if lang == "es" else en


def start_interview() -> InterviewState:
    return InterviewState()


def answer(state: InterviewState, reply: str) -> InterviewState:
    if state.done:
        return state
    key = _QUESTIONS[state.step][0]
    answers = dict(state.answers)
    answers[key] = reply.strip()
    return replace(state, answers=answers, step=state.step + 1)


def to_plan_input(state: InterviewState, lang: str = "es") -> PlanInput:
    """Convierte respuestas completas en un PlanInput. Asume state.done."""
    a = state.answers
    season = SeasonParams(
        start_date="2026-01-06",
        duration_weeks=int(a.get("duration_weeks", "20")),
        training_days_per_week=int(a.get("training_days_per_week", "4")),
        matches_per_week=int(a.get("matches_per_week", "1")),
        competition_type=CompetitionType.LEAGUE,
        start_fitness=StartFitness.MEDIUM,
    )
    return PlanInput(
        season=season,
        model_id=a.get("model_id", "traditional"),
        format_id=a.get("format_id", "football_11"),
        lang=lang,
    )
