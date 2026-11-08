# NFR Requirements — U4 Persistencia y Exportación

**Hereda**: stack Python 3.11+ de U1/U2/U3.

## 1. Tecnología
- Python 3.11+, paquete `app/persistence/`.
- **Persistencia**: JSON con stdlib `json` (D2). Sin ORM ni DB en v1. Interfaz de repositorio para migrar a SQLite al escalar.
- **HTML export**: strings + CSS, stdlib. Cero dependencias.
- **PDF export**: **WeasyPrint opcional** (dependencia opcional en pyproject, grupo `pdf`). Import perezoso. Si ausente → degradación a vía HTML.

## 2. NFR aplicables
| NFR | Aplica | Cómo |
|-----|--------|------|
| RNF-6 portabilidad | Sí | JSON por carpeta; round-trip verificado. |
| RNF-2 offline | Sí | HTML y JSON locales; PDF nativo opcional (no requerido). |
| RNF-4 tecnología | Sí | Python stdlib + WeasyPrint opcional. |
| D2 JSON tras interfaz | Sí | PlanRepository. |
| D6 bilingüe | Sí | export por idioma. |

## 3. Rendimiento
- save/load de un plan < 50 ms (archivos pequeños). HTML < 50 ms. PDF depende de WeasyPrint (no crítico).

## 4. Verificación (PBT parcial)
- Round-trip `load(save(plan)) == plan`; HTML determinista y bien formado; conteo de historial; sin `.tmp` residual; degradación PDF sin librería.

## 5. Restricciones
- Escritura atómica (tmp+rename) para no corromper datos.
- No usar reloj del sistema dentro de U4 (created_at inyectado); clock opcional para tests.
- WeasyPrint nunca importado a nivel de módulo (no romper arranque offline).
