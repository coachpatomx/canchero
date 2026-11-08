# Functional Design — U3 Diagramas y Gráficas

**Fase**: CONSTRUCCIÓN → Functional Design (U3)
**Unidad**: U3 — Diagramas y Gráficas, en `app/diagrams/`
**Fuentes directas**: `knowledge-base/metodologia-fmf.md` (C1 momentos/zonas del campo), `session-output-reference.md` (diagrama por tarea + diagrama de organización), `requirements.md` (RF-5), `component-methods.md` (C5 DiagramRenderer), decisión D3 (SVG generado).
**Decisiones aplicadas**: D3 (SVG), D6 (bilingüe en leyendas).

---

## 1. Propósito y fronteras

U3 **dibuja**. Toma el `DiagramSpec` de una tarea (datos que produce U2) y la `LoadCurve` del motor (U1) y genera **SVG** (D3): texto XML que se puede incrustar en la web (U5) y en el PDF (U4), sin dependencias de terceros.

**Depende de**: U2 (tipos de tarea/formato) y U1 (`LoadCurve`). **No depende** de U4/U5.

**Lo que U3 NO hace**:
- No decide el contenido del ejercicio (eso es U2).
- No calcula cargas (eso es U1); solo las grafica.
- No persiste ni exporta a PDF (eso es U4); entrega el string SVG.
- No es un editor de pizarra interactivo (fuera de alcance v1, RF-5): diagramas **esquemáticos / basados en plantilla**.

---

## 2. Qué dibuja (RF-5 + plantilla)

Tres salidas, todas SVG:

1. **Diagrama de tarea** (`render_task_diagram`): media cancha o cancha esquemática con jugadores (equipo A/B), conos, balones, zonas resaltadas (de los momentos C1), flechas de movimiento, y **marcadores adaptados** (vallas laterales, guía, antifaz-zona) cuando el formato es adaptado.
2. **Diagrama de organización** (`render_organization_diagram`): cancha completa del formato con zonas, para la vista global de la sesión.
3. **Gráfica de carga** (`render_load_chart`): curva de volumen/intensidad por microciclo (secundario), para presentar la periodización.

---

## 3. Modelo de render

### 3.1 Lienzo (Pitch)
- Coordenadas internas en un sistema normalizado (0–1000 de ancho) escalado a las dimensiones del formato (`field_length_m` × `field_width_m`), manteniendo proporción.
- Se dibuja: rectángulo del campo, línea media, áreas y porterías esquemáticas. Para media cancha, solo una mitad.

### 3.2 Primitivas SVG (sin librerías)
Funciones puras que devuelven fragmentos de string SVG:
- `_rect`, `_line`, `_circle`, `_polygon`, `_text`, `_arrow` (línea + marcador de punta), `_cone` (triángulo).
- Colores por rol: equipo A, equipo B, balón, cono, zona (relleno translúcido), marcador adaptado.

### 3.3 Colocación determinista
- Jugadores se reparten en una **cuadrícula determinista** según `players_a`/`players_b` (sin aleatoriedad): equipo A a la izquierda, B a la derecha, balón al centro.
- Conos en el borde del espacio de trabajo. Zonas como rectángulos semitransparentes posicionados por clave (`final_third`, `middle`, etc., de C1).
- Marcadores adaptados:
  - `side_boards` → líneas gruesas en las bandas (fútbol ciegos).
  - `guide` → icono/etiqueta tras la portería.
  - `zones` → divisiones de zona (defensa/medio/ataque) que usa el árbitro-guía.

### 3.4 Leyenda bilingüe (D6)
- Cada diagrama incluye una leyenda con las claves usadas, en el idioma pedido (`lang`), resolviendo `I18nText`.

---

## 4. API pública (contrato)

```
render_task_diagram(exercise: Exercise, fmt: FootballFormat, lang: str = "es") -> SvgDiagram
render_organization_diagram(tasks: list[Exercise], fmt: FootballFormat, lang: str = "es") -> SvgDiagram
render_load_chart(curve: LoadCurve, lang: str = "es") -> SvgChart
```

`SvgDiagram` / `SvgChart` = dataclass con `{ svg: str, width: int, height: int, title: I18nText }`. El `svg` es el documento completo (`<svg ...>...</svg>`), listo para incrustar.

---

## 5. Determinismo y verificación (PBT parcial)

- **Determinista**: mismas entradas → mismo SVG byte a byte (sin reloj, sin random). Clave para que los diagramas sean reproducibles y testeables.
- Propiedades:
  1. **SVG bien formado**: toda salida parsea como XML válido (`xml.etree`).
  2. **Dimensiones correctas**: `width/height` > 0 y coinciden con el atributo del `<svg>`.
  3. **Conteo de jugadores**: el nº de marcadores de jugador dibujados == `players_a + players_b`.
  4. **Determinismo**: dos llamadas con las mismas entradas dan el mismo string.
  5. **Marcadores adaptados presentes**: si el formato es adaptado con `side_boards`, el SVG contiene ese elemento.
  6. **Puntos de la gráfica**: la curva tiene un punto por microciclo de entrada.

---

## 6. Errores
Reutiliza `Result`/`DomainError` (U1). Variante nueva si hace falta: `InvalidDiagramSpec` (p. ej. jugadores negativos). Degradación: si falta `diagram_spec`, dibuja un campo vacío con leyenda "sin datos de tarea".

---

## 7. Trazabilidad requisitos → diseño

| Requisito | Cubierto por |
|-----------|--------------|
| RF-5 diagramas tácticos (prioritario) | §2.1 render_task_diagram + §3 primitivas |
| RF-5 gráficas de carga (secundario) | §2.3 render_load_chart |
| soporte RF-8 (adaptado visible) | §3.3 marcadores adaptados |
| D3 SVG | §3.2 SVG sin librerías |
| D6 bilingüe | §3.4 leyenda por idioma |
| RNF-2 offline | SVG generado localmente, sin red |

---

## 8. Estructura de código prevista

```
app/
└── diagrams/
    ├── __init__.py       # API pública de U3
    ├── svg_primitives.py # _rect/_line/_circle/_arrow/_cone/_text (strings SVG)
    ├── pitch.py          # lienzo del campo (completo / media cancha) por formato
    ├── task_diagram.py   # render_task_diagram (jugadores, conos, zonas, adaptados)
    ├── organization.py   # render_organization_diagram
    └── load_chart.py     # render_load_chart (curva vol/intensidad)
```
