"""Mapeo de calendario real para el macrociclo.

Dada una fecha de inicio (ISO, YYYY-MM-DD) y el número de semana (1-based), calcula
la fecha de inicio de esa semana. Y a la inversa: dada una fecha, en qué semana del
macro cae. Sirve para:
  - mostrar fechas/mes reales en la matriz,
  - ubicar una competencia ("tengo partido el 20 de agosto") en su semana.

Sin dependencias externas: usa datetime del stdlib.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

_MESES_ES = ["", "ene", "feb", "mar", "abr", "may", "jun",
             "jul", "ago", "sep", "oct", "nov", "dic"]
_MESES_LARGO = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
}


def parse_iso(s: str) -> date | None:
    """Parsea 'YYYY-MM-DD'. None si no es válida."""
    if not s:
        return None
    try:
        return datetime.strptime(s.strip()[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def week_start(start_iso: str, week_index: int) -> date | None:
    """Fecha de inicio (lunes alineado) de la semana `week_index` (1-based)."""
    d0 = parse_iso(start_iso)
    if d0 is None:
        return None
    # Alinear al lunes de la semana de inicio.
    monday0 = d0 - timedelta(days=d0.weekday())
    return monday0 + timedelta(weeks=week_index - 1)


def week_label(start_iso: str, week_index: int) -> str:
    """Etiqueta corta 'dd mmm' de la semana (p. ej. '18 ago'). '' si no hay fecha."""
    d = week_start(start_iso, week_index)
    if d is None:
        return ""
    return f"{d.day:02d} {_MESES_ES[d.month]}"


def month_label(start_iso: str, week_index: int) -> str:
    """Nombre de mes de la semana (p. ej. 'AGOSTO'). '' si no hay fecha."""
    d = week_start(start_iso, week_index)
    if d is None:
        return ""
    nombres = ["", "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
               "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
    return nombres[d.month]


def week_of_date(start_iso: str, target: date, total_weeks: int) -> int | None:
    """Devuelve el nº de semana (1-based) en que cae `target`, o None si fuera de rango."""
    d0 = parse_iso(start_iso)
    if d0 is None or target is None:
        return None
    monday0 = d0 - timedelta(days=d0.weekday())
    monday_t = target - timedelta(days=target.weekday())
    delta_weeks = (monday_t - monday0).days // 7 + 1
    if 1 <= delta_weeks <= total_weeks:
        return delta_weeks
    return None


def parse_spanish_date(text: str, default_year: int | None = None) -> date | None:
    """Interpreta fechas en español libres: '20 de agosto', '15 de septiembre de 2026',
    '20/08/2026', '2026-08-20'. Devuelve date o None."""
    t = text.lower().strip()
    # ISO directa
    d = parse_iso(t)
    if d:
        return d
    import re
    # dd/mm/aaaa o dd-mm-aaaa
    m = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", t)
    if m:
        dd, mm, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if yy < 100:
            yy += 2000
        try:
            return date(yy, mm, dd)
        except ValueError:
            return None
    # "20 de agosto [de 2026]"
    m = re.search(r"(\d{1,2})\s+de\s+([a-záéíóú]+)(?:\s+de\s+(\d{4}))?", t)
    if m:
        dd = int(m.group(1))
        mes = _MESES_LARGO.get(m.group(2))
        yy = int(m.group(3)) if m.group(3) else (default_year or date.today().year)
        if mes:
            try:
                return date(yy, mes, dd)
            except ValueError:
                return None
    return None
