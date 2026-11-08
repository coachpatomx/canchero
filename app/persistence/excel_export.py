"""Exportación del macrociclo/mesociclos a Excel (.xlsx) — formato tipo plantilla
de macrociclo (filas = contenidos/capacidades, columnas = microciclos/semanas).

Inspirado en la plantilla del usuario (macro de fútbol inclusivo) + buenas
prácticas: encabezado con metadatos, fila de períodos, fila de mesociclos, fila
de microciclos con % de carga, y bloques de capacidades por semana.

Genera el .xlsx escribiendo el formato OOXML mínimo con stdlib (zipfile), sin
depender de openpyxl. Así funciona offline y sin dependencias nuevas.
"""
from __future__ import annotations

import zipfile
from xml.sax.saxutils import escape


def _col(n: int) -> str:
    """Índice de columna (1-based) a letra Excel (1->A, 27->AA)."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _cell(col: int, row: int, value, is_number=False) -> str:
    ref = f"{_col(col)}{row}"
    if value is None or value == "":
        return f'<c r="{ref}"/>'
    if is_number:
        return f'<c r="{ref}"><v>{value}</v></c>'
    return f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">{escape(str(value))}</t></is></c>'


def _rows_for_plan(plan) -> list[list]:
    """Construye la matriz de filas del macrociclo."""
    macro = plan.macro
    micros = [m for meso in macro.mesocycles for m in meso.microcycles]
    micros.sort(key=lambda m: m.week_index)
    n = len(micros)

    # Traducciones a español (el motor usa claves inglesas internas).
    _period_es = {"preparatory": "Preparatorio", "competitive": "Competitivo",
                  "transition": "Transitorio", "resistance": "Resistencia",
                  "strength": "Fuerza", "speed": "Velocidad", "recovery": "Recuperación"}
    _micro_es = {"introductory": "Introductorio", "developmental": "Desarrollador",
                 "shock": "Choque", "recovery": "Recuperación",
                 "precompetitive": "Precompetitivo", "competition": "Competencia"}
    _model_es = {"traditional": "Tradicional (Matveyev)", "blocks": "Por bloques (Issurin)",
                 "atr": "ATR", "tactical": "Periodización Táctica (Frade)",
                 "structured": "Entrenamiento Estructurado (Seirul·lo)",
                 "football_gonzalez": "Esquema A. González"}

    rows: list[list] = []
    rows.append([f"MACROCICLO — {plan.title.es}"])
    rows.append([f"Modelo: {_model_es.get(macro.model_id, macro.model_id)}",
                 f"Semanas: {macro.total_weeks}",
                 f"Sesiones: {len(plan.sessions)}"])
    rows.append([])

    # Fila de períodos (por semana).
    week_to_period = {}
    for p in macro.periods:
        for w in range(p.start_week, p.end_week + 1):
            week_to_period[w] = _period_es.get(p.kind.value, p.kind.value)
    rows.append(["Período"] + [week_to_period.get(m.week_index, "") for m in micros])

    # Fila de mesociclo índice.
    meso_of_week = {}
    for i, meso in enumerate(macro.mesocycles, start=1):
        for m in meso.microcycles:
            meso_of_week[m.week_index] = f"M{i}"
    rows.append(["Mesociclo"] + [meso_of_week.get(m.week_index, "") for m in micros])

    # Fila de semana.
    rows.append(["Semana"] + [m.week_index for m in micros])
    # Tipo de microciclo.
    rows.append(["Tipo microciclo"] + [_micro_es.get(m.type.value, m.type.value) for m in micros])
    # Carga: volumen e intensidad.
    rows.append(["Volumen %"] + [m.target_volume_pct for m in micros])
    rows.append(["Intensidad %"] + [m.target_intensity_pct for m in micros])
    rows.append(["Sesiones/sem"] + [len(m.session_slots) for m in micros])
    rows.append([])
    rows.append(["Objetivos de temporada"] + list(plan.objectives))
    return rows


def _sheet_xml(rows: list[list]) -> str:
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    for r_idx, row in enumerate(rows, start=1):
        cells = []
        for c_idx, val in enumerate(row, start=1):
            is_num = isinstance(val, (int, float)) and not isinstance(val, bool)
            cells.append(_cell(c_idx, r_idx, val, is_number=is_num))
        out.append(f'<row r="{r_idx}">{"".join(cells)}</row>')
    out.append('</sheetData></worksheet>')
    return "".join(out)


def plan_to_xlsx_bytes(plan) -> bytes:
    """Devuelve los bytes de un .xlsx con el macrociclo."""
    import io

    rows = _rows_for_plan(plan)
    sheet = _sheet_xml(rows)

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '</Types>'
    )
    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )
    workbook = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Macrociclo" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    wb_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '</Relationships>'
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", wb_rels)
        z.writestr("xl/worksheets/sheet1.xml", sheet)
    return buf.getvalue()
