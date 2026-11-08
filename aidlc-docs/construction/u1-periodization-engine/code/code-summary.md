# Code Summary — U1 Motor de Periodización

**Estado**: COMPLETA. 18 tests verdes (11 ejemplos + 7 propiedades PBT, incluida round-trip de serialización).

## Código generado (en workspace root `/kiro`)

```
periodization_engine/           # paquete reutilizable, agnóstico al deporte (RNF-7)
├── __init__.py                 # API pública + ENGINE_VERSION = "1.0.0"
├── errors.py                   # DomainError (bilingüe) + Ok/Err/Result
├── domain.py                   # entidades frozen + enums + I18nText
├── loadtable.py                # tabla C3 de cargas por tipo de microciclo
├── engine.py                   # derivación pura macro→meso→micro→slots + hash
├── serialization.py            # to_dict/from_dict (round-trip, RNF-6)
└── models/                     # 6 modelos builtin + registry (RF-4)
    ├── traditional.py  blocks.py  atr.py
    ├── tactical.py  structured.py  football_gonzalez.py
pyproject.toml                  # núcleo stdlib-only; hypothesis/pytest solo test
tests/
├── test_engine_examples.py     # 11 ejemplos concretos
└── test_engine_properties.py   # 7 propiedades con Hypothesis
```

## Qué cumple
- **RF-1 / RF-10 (determinista)**: encadena macro→meso→micro→slots; id = hash de entradas; mismas entradas → mismo árbol.
- **RF-4**: `register_custom_model` acepta reglas del usuario (modelo = datos).
- **D4**: 6 modelos precargados (incluido A. González para torneos cortos).
- **RNF-2**: núcleo solo stdlib, offline.
- **RNF-5**: `Provenance` + trazabilidad padre↔hijo; verificado por PBT.
- **RNF-6**: serialización JSON round-trip.
- **RNF-7**: paquete aislado, sin fútbol; test estructural lo verifica.
- **D6**: textos de modelo y errores bilingües es/en.

## Decisiones de implementación relevantes
- Reparto de semanas por período con método del mayor residuo (Hamilton) para que la suma sea exacta incluso con pocas semanas; si hay más períodos que semanas, se eligen los de mayor peso (determinista).
- El motor cuenta semanas/días; el mapeo a fechas reales lo hará U5.
- Valor de carga por defecto = punto medio del rango C3, modulado por nivel de forma inicial solo en el primer período preparatorio.

## Cómo ejecutar los tests
```
python3 -m venv .venv
.venv/bin/pip install hypothesis pytest
.venv/bin/python -m pytest -q      # -> 18 passed
```

## Pendientes conocidos (no bloquean U1)
- Las etiquetas bilingües de enums (período/micro/fase) aún no tienen tabla LABELS poblada; se consumirá desde U5 cuando se construya la UI. El contrato ya transporta las claves.
