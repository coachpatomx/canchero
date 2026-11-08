# NFR Requirements — U3 Diagramas y Gráficas

**Fase**: CONSTRUCCIÓN → NFR Requirements (U3)
**Hereda**: stack Python 3.11+ de U1/U2.

## 1. Tecnología
- Python 3.11+, paquete `app/diagrams/`.
- **SVG generado a mano** (D3): strings XML, **sin librerías de terceros** de dibujo. Validación de SVG con `xml.etree` (stdlib). Cumple RNF-2 (offline) y mantiene el proyecto ligero.
- Depende de U2 (Exercise, FootballFormat) y U1 (LoadCurve).

## 2. NFR aplicables
| NFR | Aplica | Cómo |
|-----|--------|------|
| RNF-2 offline | Sí | SVG local, sin red ni fuentes externas. |
| RNF-4 tecnología | Sí | Python, stdlib. |
| RNF-6 portabilidad | Parcial | El SVG es texto; U4 lo incrusta en PDF/JSON. |
| D3 SVG | Sí | salida SVG string. |
| D6 bilingüe | Sí | leyendas en el idioma pedido. |

## 3. Rendimiento
- Render de un diagrama o gráfica < 50 ms (generación de string). Sin estado.

## 4. Verificación (PBT parcial)
- 6 propiedades del Functional Design §5, incluida "SVG parsea como XML válido" y determinismo.

## 5. Restricciones
- Sin reloj ni aleatoriedad (determinismo byte a byte).
- Sin dependencias binarias (nada de rasterizado/PNG en v1).
