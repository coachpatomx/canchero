# Functional Design — U4 Persistencia y Exportación

**Fase**: CONSTRUCCIÓN → Functional Design (U4)
**Unidad**: U4 — Persistencia y Exportación, en `app/persistence/`
**Fuentes directas**: `requirements.md` (RF-6, RF-9, RNF-6), `session-output-reference.md` (maqueta de la plantilla mejorada), `component-methods.md` (C7 PlanRepository, C8 Exporter), decisión D2 (JSON tras interfaz, migrable a SQLite).
**Decisiones aplicadas**: D2 (JSON en disco), D6 (export bilingüe), PDF = HTML base siempre + PDF nativo opcional vía WeasyPrint (decisión del usuario 2026-11-07).

---

## 1. Propósito y fronteras

U4 **guarda, reabre y exporta**. Dos responsabilidades:
- **Persistencia**: planes (macro+meso+sesiones), historial y biblioteca de ejercicios, como **archivos JSON en disco** (D2, RNF-6). Portabilidad = copiar una carpeta.
- **Exportación**: la sesión/plan a un documento imprimible con la maqueta de la plantilla mejorada.

**Depende de**: U1 (serialización de ciclos), U2 (serialización de ejercicios/formatos), U3 (SVG para incrustar). **No depende** de U5.

**Lo que U4 NO hace**:
- No genera la planificación (U1/U5) ni el contenido (U2) ni los diagramas (U3).
- No decide el idioma (lo recibe como parámetro).

---

## 2. Persistencia — interfaz de repositorio (D2)

Todo el acceso a disco pasa por una **interfaz** `PlanRepository`, para poder migrar JSON→SQLite al escalar sin tocar el resto.

```
interface PlanRepository:
    save(plan: TrainingPlan) -> PlanRef
    load(ref: PlanRef) -> Result<TrainingPlan, DomainError>
    list_history(filter: HistoryFilter) -> list<PlanRef>
    delete(ref: PlanRef) -> Result<None, DomainError>
    save_exercise(ex: Exercise) -> ExerciseRef
    load_exercise(ref: ExerciseRef) -> Result<Exercise, DomainError>
    list_exercises(filter) -> list<ExerciseRef>
```

**Implementación v1: `JsonFileRepository`**
- Raíz de datos configurable (por defecto `data/`), con subcarpetas `plans/` y `library/`.
- Cada plan → `data/plans/<plan_id>.json`. Cada ejercicio de biblioteca → `data/library/<ex_id>.json`.
- `PlanRef` = `{ id, title, created_at, model_id, format_id }` (metadatos para listar el historial sin cargar todo).
- Escritura atómica: escribir a `.tmp` y renombrar, para no corromper si se interrumpe.
- Índice de historial: `data/plans/_index.json` con la lista de `PlanRef` (se actualiza en save/delete).

> `created_at` es el único dato temporal real; lo recibe de la capa de aplicación (U5), **no** lo genera U4 con el reloj (mantener U4 testeable). Alternativamente, U4 acepta un `clock` inyectable; por defecto usa un timestamp fijo en tests.

---

## 3. Modelo de datos del Plan (`TrainingPlan`)

Agrega todo lo necesario para reabrir y exportar una planificación completa.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | str | Id del plan (= id del macro de U1, hash determinista). |
| `title` | I18nText | Título del plan. |
| `created_at` | str | ISO-8601 (inyectado por U5). |
| `macro` | Macrocycle | Árbol de U1 (serializado con su serializer). |
| `format_id` | str | Formato de fútbol (U2). |
| `sessions` | list<SessionDoc> | Sesiones materializadas (con tareas + diagramas). |
| `objectives` | tuple<str> | Objetivos de temporada. |
| `lang` | str | Idioma por defecto del plan. |

`SessionDoc` = metadatos de encabezado (semana, meso, micro, fecha, carga) + lista de `Exercise` (U2) + SVGs pre-renderizados opcionales + objetivos individuales (enlazados a U6 cuando exista).

---

## 4. Exportación — base HTML + PDF opcional

### 4.1 `HtmlExporter` (siempre disponible, cero dependencias)
```
to_html_session(session: SessionDoc, lang: str) -> str
to_html_plan(plan: TrainingPlan, lang: str) -> str
```
- Produce un documento HTML autocontenido con **CSS de impresión** (`@media print`) y los **SVG de U3 embebidos inline**.
- Maqueta de la **plantilla mejorada**: encabezado (equipo, fecha, torneo/meso/micro/sesión, carga, objetivo), tabla de tareas (tipo, duración, dimensiones, descripción, diagrama), materiales agregados, volumen/cargas, los 4 aspectos, y bloque de objetivos individuales (de U6).
- El usuario imprime desde el navegador → "Guardar como PDF". **Esto ya es un PDF.**

### 4.2 `PdfExporter` (opcional, activable)
```
is_pdf_available() -> bool          # True si WeasyPrint importable
to_pdf_session(session, lang) -> Result<bytes, DomainError>
to_pdf_plan(plan, lang) -> Result<bytes, DomainError>
```
- Reutiliza **el mismo HTML** de `HtmlExporter` y lo pasa por WeasyPrint → bytes PDF.
- Si WeasyPrint no está instalado: `is_pdf_available()` devuelve False y los `to_pdf_*` devuelven `Err(PdfEngineUnavailable)` con mensaje bilingüe que sugiere usar la ruta "imprimir desde el navegador".
- **Import perezoso**: WeasyPrint se importa dentro de la función, no a nivel de módulo, para no romper el arranque si no está (RNF-2).

> Resultado: PDF disponible SIEMPRE (vía navegador) y con un clic si WeasyPrint está. Una sola maqueta (el HTML), sin duplicar diseño.

---

## 5. Determinismo y verificación (PBT parcial)

- **Round-trip de persistencia**: `load(save(plan)) == plan` (propiedad central, RNF-6). Determinista.
- **HTML determinista**: mismo plan+lang → mismo HTML.
- **HTML bien formado**: parsea como XML/HTML (contiene el SVG válido de U3).
- **Historial**: tras N `save`, `list_history` devuelve N refs; tras `delete`, N-1.
- **Escritura atómica**: no quedan archivos `.tmp` tras un save correcto.
- **Degradación PDF**: si WeasyPrint ausente, `is_pdf_available()==False` y `to_pdf_*` devuelve Err (no lanza).

---

## 6. Errores
Reutiliza `Result`/`DomainError` (U1). Variantes nuevas: `PlanNotFound`, `ExerciseNotFound`, `CorruptData` (JSON inválido en disco), `PdfEngineUnavailable`.

---

## 7. Trazabilidad requisitos → diseño

| Requisito | Cubierto por |
|-----------|--------------|
| RF-6 editable + export PDF | §3 TrainingPlan editable + §4 HTML/PDF |
| RF-9 historial + biblioteca | §2 PlanRepository (plans/ + library/ + índice) |
| RNF-6 portabilidad | §2 JSON por carpeta + round-trip §5 |
| D2 JSON tras interfaz | §2 interfaz + JsonFileRepository |
| D6 bilingüe | §4 export por idioma |
| RNF-2 offline | §4.2 PDF opcional con import perezoso |

---

## 8. Estructura de código prevista

```
app/
└── persistence/
    ├── __init__.py          # API pública de U4
    ├── repository.py        # interfaz PlanRepository
    ├── json_repository.py   # JsonFileRepository (D2): save/load/history/library, escritura atómica
    ├── plan.py              # TrainingPlan, SessionDoc, PlanRef, serialización
    ├── html_export.py       # HtmlExporter (maqueta plantilla mejorada + SVG + CSS print)
    └── pdf_export.py        # PdfExporter (WeasyPrint opcional, import perezoso)
```
