# Code Summary — U4 Persistencia y Exportación

**Estado**: COMPLETA. Suite total **53 passed** (18 U1 + 13 U2 + 11 U3 + 11 U4).

## Código generado (en workspace root `/kiro`)
```
app/persistence/
├── __init__.py          # API pública de U4
├── repository.py        # interfaz PlanRepository (Protocol) — D2
├── json_repository.py   # JsonFileRepository: save/load/history/library, escritura atómica, índice
├── plan.py              # TrainingPlan, SessionDoc, PlanRef + serialización (compone U1+U2)
├── html_export.py       # HtmlExporter: maqueta plantilla mejorada + SVG + CSS @media print
└── pdf_export.py        # PdfExporter: WeasyPrint opcional, import perezoso, degradación limpia
tests/test_persistence.py # 9 ejemplos + 2 propiedades PBT
```

## Qué cumple
- **RF-9 historial + biblioteca**: planes en `data/plans/` con `_index.json`; ejercicios en `data/library/`.
- **RF-6 editable + export PDF (dos vías)**: HTML imprimible siempre (navegador → PDF) + PDF nativo con un clic si WeasyPrint está. Ambas reutilizan la misma maqueta.
- **RNF-6 portabilidad**: JSON por carpeta; round-trip `load(save(plan))==plan` verificado por PBT.
- **D2**: interfaz de repositorio → migrable a SQLite sin tocar llamadores.
- **D6**: export bilingüe es/en.
- **RNF-2 offline**: HTML/JSON sin red; WeasyPrint import perezoso, no rompe arranque.

## Decisiones de implementación
- Escritura atómica (tmp + os.replace) → no corrompe datos si se interrumpe.
- Índice de historial separado → listar sin cargar planes completos.
- `created_at` inyectado por la capa de app (no reloj en U4) → testeable.
- `is_pdf_available()` usa `find_spec` sin importar WeasyPrint; `to_pdf_*` degrada a `Err(PdfEngineUnavailable)` con mensaje bilingüe que sugiere la vía navegador.

## Verificación
- 53 tests verdes. Smoke test: plan guardado en JSON, reabierto idéntico, historial OK, HTML imprimible de 13 KB con diagramas embebidos; PDF nativo reporta no disponible (WeasyPrint ausente) → degradación correcta.

## Pendientes conocidos (no bloquean)
- `individual_goals` en SessionDoc es un dict ligero; se enlazará con el modelo real de U6.
- Migración a SQLite: la interfaz ya lo permite; no implementada en v1 (local).
