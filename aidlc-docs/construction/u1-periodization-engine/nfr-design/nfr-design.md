# NFR Design — U1 Motor de Periodización

**Fase**: CONSTRUCCIÓN → NFR Design (U1)
**Fuentes**: `nfr-requirements.md` (U1), `functional-design.md` (U1).

---

## 1. Estructura del paquete

```
periodization_engine/
├── __init__.py              # API pública: re-exporta funciones y entidades
├── domain.py                # entidades inmutables (dataclasses frozen) + enums + I18nText
├── errors.py                # DomainError y variantes; Result helper
├── models/                  # los 6 modelos precargados como datos (ModelRules)
│   ├── __init__.py          # registry: listModels/getModel + registro de custom
│   ├── traditional.py
│   ├── blocks.py
│   ├── atr.py
│   ├── tactical.py
│   ├── structured.py
│   └── football_gonzalez.py
├── engine.py                # funciones de derivación puras (build/derive/computeLoadCurve)
├── loadtable.py             # tabla C3 de % carga por tipo de microciclo
└── serialization.py         # to_dict/from_dict (RNF-6 round-trip)
```

Frontera dura (RNF-7): ningún módulo importa de `app/`. Verificado por test estructural (propiedad 7).

---

## 2. Patrones de diseño aplicados

| NFR | Patrón / decisión |
|-----|-------------------|
| Determinismo (RNF-5) | Funciones puras; `MacrocycleId` = `sha256` de entradas normalizadas (JSON canónico ordenado). Sin `datetime.now()`, sin `random`. |
| Inmutabilidad | `@dataclass(frozen=True)` en todas las entidades; derivaciones devuelven copias nuevas. |
| Modelos como datos (RF-4) | `ModelRules` es una dataclass de datos; cada modelo builtin es una instancia. `registerCustomModel` valida y añade al registry en memoria (el llamador decide persistirlo vía U4). |
| Manejo de errores | `Result` = unión `Ok(value) | Err(DomainError)`. Se evita lanzar para flujo esperado. |
| Serialización (RNF-6) | `to_dict` produce dicts JSON-nativos (str/int/list/dict); enums → su `value` string; I18nText → `{es, en}`. `from_dict` reconstruye. Round-trip verificado por PBT. |
| Offline (RNF-2) | Runtime solo stdlib (`dataclasses`, `enum`, `hashlib`, `json`, `typing`). |

---

## 3. Representación de los enums bilingües

Enums internos con clave estable en inglés:

```
PeriodKind = {preparatory, competitive, transition, resistance, strength, speed, recovery}
MesocycleType = {base, development, stabilization, competitive, recovery}
MicrocycleType = {introductory, developmental, shock, recovery, precompetitive, competition}
MicroPhase = {recovery, stimulating, optimization, competitive}
SessionTypeHint = {selective, complex, supplementary}
```

Cada enum tiene una tabla de etiquetas `{es, en}` para que U5 muestre texto, pero el motor compara por la clave inglesa. Esto mantiene el determinismo independiente del idioma.

---

## 4. Normalización de entradas para el hash determinista

Antes de hashear `SeasonParams`:
1. Fechas → ISO-8601 string.
2. Si viene `durationWeeks` y `endDate`, se canoniza a `durationWeeks` (verdad única).
3. Listas de objetivos → ordenadas alfabéticamente.
4. Se serializa a JSON con `sort_keys=True` y separadores fijos → `sha256`.

Garantiza que entradas lógicamente equivalentes produzcan el mismo id.

---

## 5. Versionado del motor

- `ENGINE_VERSION` constante en `__init__.py`. Se incluye en `Provenance` y en el hash del id.
- Cambiar reglas de derivación → subir versión → ids distintos (evita confundir planes viejos con la lógica nueva). Documentado para U4/U5.

---

## 6. Estrategia de test (PBT parcial + ejemplos)

- `tests/` fuera del paquete runtime.
- **Hypothesis** genera `SeasonParams` válidos aleatorios y verifica las 7 propiedades + round-trip de serialización.
- Tests de ejemplo concretos por modelo (p. ej. un macro de 40 semanas tradicional produce períodos esperados) para fijar comportamiento legible.
