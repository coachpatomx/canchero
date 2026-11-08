# NFR Design — U3 Diagramas y Gráficas

**Fase**: CONSTRUCCIÓN → NFR Design (U3)

## 1. Estructura
`app/diagrams/` (ver Functional Design §8). `__init__.py` re-exporta la API.

## 2. Patrones
| NFR | Decisión |
|-----|----------|
| SVG sin librerías (D3/RNF-2) | Primitivas puras que concatenan strings SVG; documento ensamblado por `pitch` + capas. |
| Determinismo | Colocación de jugadores/conos por cuadrícula calculada, sin random; números formateados con precisión fija. |
| XML válido | Escapar texto (`&`, `<`, `>`, comillas) en `_text`; test verifica parseo con `xml.etree`. |
| Bilingüe (D6) | Leyenda resuelve `I18nText` según `lang`; claves de zona/marcador mapeadas a etiquetas es/en. |
| Escalado | Sistema de coordenadas normalizado 0–1000 escalado a proporción del campo del formato. |

## 3. Manejo de errores / degradación
- `diagram_spec` ausente o inválido → campo vacío + leyenda "sin datos" (no rompe la generación de la sesión).

## 4. Test
`tests/test_diagrams.py`: ejemplos (ciegos con vallas, convencional) + propiedades (XML válido, conteo de jugadores, determinismo, puntos de gráfica). Hypothesis genera DiagramSpec y curvas.
