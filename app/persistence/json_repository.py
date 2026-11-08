"""Repositorio JSON en disco (D2, RF-9, RNF-6).

Portabilidad por carpeta: un respaldo = copiar `data/`. Escritura atómica
(tmp + rename). Índice de historial para listar sin cargar todo.
"""
from __future__ import annotations

import json
import os

from periodization_engine.errors import (
    DomainError,
    DomainErrorKind,
    Err,
    Ok,
    Result,
)

from app.football_domain.exercise import Exercise
from app.football_domain.serialization import exercise_from_dict, exercise_to_dict

from .plan import PlanRef, TrainingPlan, plan_from_dict, plan_to_dict


def _atomic_write(path: str, data: dict) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)  # rename atómico


class JsonFileRepository:
    """Implementa PlanRepository guardando JSON en `root/plans` y `root/library`."""

    def __init__(self, root: str = "data"):
        self.root = root
        self.plans_dir = os.path.join(root, "plans")
        self.library_dir = os.path.join(root, "library")
        self.index_path = os.path.join(self.plans_dir, "_index.json")
        os.makedirs(self.plans_dir, exist_ok=True)
        os.makedirs(self.library_dir, exist_ok=True)

    # ---- índice de historial ---- #
    def _read_index(self) -> list[dict]:
        if not os.path.exists(self.index_path):
            return []
        with open(self.index_path, encoding="utf-8") as f:
            return json.load(f)

    def _write_index(self, refs: list[dict]) -> None:
        _atomic_write(self.index_path, refs)  # type: ignore[arg-type]

    def _ref_to_dict(self, ref: PlanRef) -> dict:
        return {
            "id": ref.id, "title_es": ref.title_es, "title_en": ref.title_en,
            "created_at": ref.created_at, "model_id": ref.model_id,
            "format_id": ref.format_id,
        }

    # ---- planes ---- #
    def save(self, plan: TrainingPlan) -> PlanRef:
        path = os.path.join(self.plans_dir, f"{plan.id}.json")
        _atomic_write(path, plan_to_dict(plan))
        ref = plan.to_ref()
        index = [r for r in self._read_index() if r["id"] != plan.id]
        index.append(self._ref_to_dict(ref))
        self._write_index(index)
        return ref

    def load(self, plan_id: str) -> Result[TrainingPlan]:
        path = os.path.join(self.plans_dir, f"{plan_id}.json")
        if not os.path.exists(path):
            return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL,
                                   detail=f"plan {plan_id} no encontrado"))
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return Ok(plan_from_dict(data))
        except (json.JSONDecodeError, KeyError) as e:
            return Err(DomainError(DomainErrorKind.INVALID_MODEL_RULES,
                                   detail=f"datos corruptos: {e}"))

    def list_history(self) -> list[PlanRef]:
        return [
            PlanRef(id=r["id"], title_es=r["title_es"], title_en=r["title_en"],
                    created_at=r["created_at"], model_id=r["model_id"],
                    format_id=r["format_id"])
            for r in self._read_index()
        ]

    def delete(self, plan_id: str) -> Result[None]:
        path = os.path.join(self.plans_dir, f"{plan_id}.json")
        if os.path.exists(path):
            os.remove(path)
        index = [r for r in self._read_index() if r["id"] != plan_id]
        self._write_index(index)
        return Ok(None)

    # ---- biblioteca ---- #
    def save_exercise(self, ex: Exercise) -> str:
        path = os.path.join(self.library_dir, f"{ex.id}.json")
        _atomic_write(path, exercise_to_dict(ex))
        return ex.id

    def load_exercise(self, ex_id: str) -> Result[Exercise]:
        path = os.path.join(self.library_dir, f"{ex_id}.json")
        if not os.path.exists(path):
            return Err(DomainError(DomainErrorKind.UNKNOWN_MODEL,
                                   detail=f"ejercicio {ex_id} no encontrado"))
        with open(path, encoding="utf-8") as f:
            return Ok(exercise_from_dict(json.load(f)))

    def list_exercises(self) -> list[str]:
        return sorted(
            fn[:-5] for fn in os.listdir(self.library_dir)
            if fn.endswith(".json")
        )
