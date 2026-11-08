# NFR Design — U4 Persistencia y Exportación

## 1. Estructura
`app/persistence/` (ver Functional Design §8). `__init__.py` re-exporta la API.

## 2. Patrones
| NFR | Decisión |
|-----|----------|
| Interfaz de repositorio (D2) | `PlanRepository` abstracto (Protocol/ABC); `JsonFileRepository` implementa. U5 depende de la interfaz, no de la implementación → migración a SQLite sin tocar llamadores. |
| Escritura atómica (RNF-6) | Escribir a `<path>.tmp` y `os.replace` → rename atómico en POSIX. |
| Round-trip (RNF-6) | `plan.py` reutiliza serializers de U1 (macrocycle) y U2 (exercise/format); from_dict/to_dict componibles. |
| HTML determinista | Plantilla por concatenación de strings con orden fijo; números/fechas formateados fijo. |
| PDF opcional (RNF-2) | `pdf_export.py` importa WeasyPrint dentro de la función; `is_pdf_available()` hace `importlib.util.find_spec`. |
| Idioma (D6) | Toda cadena de la maqueta tiene variante es/en; se elige por `lang`. |

## 3. Índice de historial
`data/plans/_index.json` lista `PlanRef`. save/delete lo actualizan atómicamente. list_history lee solo el índice (no carga planes completos) → rápido.

## 4. Degradación PDF
`to_pdf_*` → si `not is_pdf_available()`: `Err(PdfEngineUnavailable)` con mensaje bilingüe sugiriendo imprimir desde el navegador. Nunca lanza ImportError.

## 5. Test
`tests/test_persistence.py`: repositorio en carpeta temporal (`tmp_path`), round-trip, historial, atomicidad; HTML bien formado con SVG embebido; `is_pdf_available` y degradación. WeasyPrint NO requerido para que los tests pasen.
