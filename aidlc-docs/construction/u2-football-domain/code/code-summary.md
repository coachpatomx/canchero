# Code Summary — U2 Dominio Fútbol

**Estado**: COMPLETA. Suite total **31 passed** (18 U1 + 13 U2).

## Código generado (en workspace root `/kiro`)
```
app/
├── __init__.py
└── football_domain/
    ├── __init__.py            # API pública de U2
    ├── game_model.py          # enums de dominio + GameModelVocabulary (C1/C2) bilingüe
    ├── exercise.py            # Exercise + plantilla mejorada (materiales/cargas/volumen/aspectos/diagram_spec)
    ├── formats.py             # FootballFormat como datos + 7 precargados + registry
    ├── suggest.py             # suggest_tasks_for_phase (tabla fase→tarea C5/C6 + herencia de carga)
    ├── library.py             # biblioteca en memoria (U4 persiste)
    ├── serialization.py       # to_dict/from_dict Exercise/Format (round-trip RNF-6)
    └── adapted/
        ├── __init__.py
        ├── profiles.py        # 4 AdaptationProfile: ciegos, PC, Down, amputados
        └── apply.py           # apply_adaptations (idempotente, no-op convencional)
conftest.py                    # sys.path raíz para tests
tests/test_football_domain.py  # 9 ejemplos + 4 propiedades PBT
```

## Qué cumple
- **RF-7 multi-formato**: 7 formatos precargados (11, 7, sala + 4 adaptados); `register_format` para añadir más como datos.
- **RF-8 fútbol adaptado (4 modalidades)**: perfiles de ciegos (validado), PC/Down/amputados (reglas `validated=false`, pendientes de revisión del usuario). `apply_adaptations` inyecta materiales y marcadores.
- **RF-9 biblioteca**: `create_exercise`/`get_library` con filtro.
- **Soporte RF-1/RF-5/RF-11**: `suggest_tasks_for_phase` consume el `SessionSlot` de U1 y produce tareas con `diagram_spec` (datos para U3) y carga heredada.
- **RNF-5 trazabilidad**: la tarea hereda la carga del slot; verificado por PBT.
- **RNF-6 portabilidad**: round-trip de Exercise y Format.
- **RNF-7 frontera**: U2 importa de U1; U1 no importa de app/ (test estructural de U1).
- **D6**: todo texto de usuario en I18nText es/en.

## Decisiones de implementación
- `suggest_tasks_for_phase` usa tabla determinista fase→(tipo de tarea, estrategia didáctica, espacio); la carga la toma del slot sin recalcular.
- Reglas no validadas quedan visibles vía `unvalidated_rules(fmt)` para que U5 muestre aviso al entrenador.
- `apply_adaptations` es idempotente (marca `applied_adaptations`) y no-op en formatos convencionales.

## Integración verificada
Smoke test U1+U2: macro González 17 semanas → tareas de fútbol para ciegos por día, con balón sonoro/antifaz/vallas/guía inyectados y carga coherente con cada fase.

## Pendientes conocidos (no bloquean)
- `suggest_tasks_for_phase` devuelve una tarea base por slot; variantes/redacción fina quedan para el enriquecimiento LLM (U5).
- Reglas finas de PC/Down/amputados pendientes de validación del usuario (por diseño).
