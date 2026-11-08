"""Aplicación de adaptaciones a una tarea (RF-8).

Idempotente: aplicar dos veces la misma adaptación no duplica materiales ni
marcadores. No-op en formatos convencionales. Determinista.
"""
from __future__ import annotations

from dataclasses import replace

from ..exercise import DiagramSpec, Exercise


def is_adapted(fmt) -> bool:
    return bool(getattr(fmt, "is_adapted", False))


def apply_adaptations(exercise: Exercise, fmt) -> Exercise:
    """Inyecta materiales, marcadores de diagrama y comunicación de la modalidad.

    Si el formato no es adaptado, devuelve la tarea sin cambios.
    """
    if not is_adapted(fmt) or fmt.adaptation_profile is None:
        return exercise

    profile = fmt.adaptation_profile
    tag = profile.disability_domain.value
    if tag in exercise.applied_adaptations:
        return exercise  # ya aplicado -> idempotencia

    # Añadir solo los materiales que no estén ya presentes (por key).
    existing_keys = {m.key for m in exercise.materials}
    new_materials = tuple(
        m for m in profile.material_adaptations if m.key not in existing_keys
    )

    # Marcadores de diagrama sin duplicar.
    existing_markers = set(exercise.diagram_spec.adapted_markers)
    merged_markers = exercise.diagram_spec.adapted_markers + tuple(
        mk for mk in profile.diagram_markers if mk not in existing_markers
    )
    new_diagram = replace(exercise.diagram_spec, adapted_markers=merged_markers)

    return replace(
        exercise,
        materials=exercise.materials + new_materials,
        diagram_spec=new_diagram,
        applied_adaptations=exercise.applied_adaptations + (tag,),
    )
