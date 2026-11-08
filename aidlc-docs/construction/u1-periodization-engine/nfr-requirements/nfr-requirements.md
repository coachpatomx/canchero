# NFR Requirements — U1 Motor de Periodización

**Fase**: CONSTRUCCIÓN → NFR Requirements (U1)
**Fuentes**: `requirements.md` (RNF-1..RNF-7), `functional-design.md` (U1), decisiones D1–D6.

---

## 1. Selección de tecnología (resuelve RNF-4)

**Lenguaje elegido: Python 3.11+**

Justificación:
- RNF-4 lo señala como candidato principal (ecosistema fuerte para datos, PDF, gráficos, LLMs).
- El motor es lógica pura: Python con `dataclasses` inmutables (`frozen=True`) expresa bien entidades de dominio sin boilerplate.
- Permite PBT de primera clase con **Hypothesis** (extensión PBT activada parcial).
- Un solo lenguaje en todo el proyecto reduce fricción (U2–U6 también Python; web local con FastAPI/Flask en U5).

**Decisiones técnicas del paquete U1**:
- Paquete independiente `periodization_engine/` sin dependencias de `app/` (RNF-7, frontera dura).
- **Cero dependencias de terceros en el núcleo** del motor (solo stdlib). Esto maximiza reutilidad y offline. Hypothesis es dependencia **solo de test**, no de runtime.
- Tipado estático con type hints + verificación opcional `mypy`.
- Entidades inmutables (`@dataclass(frozen=True)`), funciones puras a nivel de módulo o `@staticmethod`.

---

## 2. Requisitos no funcionales aplicables a U1

| NFR | Aplica a U1 | Cómo se concreta |
|-----|-------------|------------------|
| RNF-1 local escalable | Sí | Motor sin I/O ni estado global; se importa como librería. Escala sin cambios. |
| RNF-2 offline | Sí | Núcleo 100% stdlib, sin red. El LLM (opcional) no vive en U1. |
| RNF-3 secretos | N/A | U1 no maneja claves ni credenciales. |
| RNF-4 tecnología | Sí | Python 3.11+, stdlib-only en runtime. |
| RNF-5 coherencia/trazabilidad | Sí | Determinismo por hash de entradas; `Provenance`; verificado con PBT. |
| RNF-6 portabilidad | Parcial | U1 no persiste, pero sus entidades deben ser **serializables a JSON** (dict plano) para que U4 las guarde. Se expone `to_dict()`/`from_dict()`. |
| RNF-7 motor reutilizable | Sí | Paquete aislado, sin fútbol, sin dependencias de `app/`. |

---

## 3. Requisitos de rendimiento

- Generar un macrociclo anual completo (≈52 microciclos, ≈260 slots) debe ser **instantáneo a escala humana** (< 100 ms en hardware de usuario). Es aritmética sobre estructuras pequeñas; no hay riesgo real, pero se fija como techo.
- Sin estado persistente entre llamadas → sin fugas de memoria ni calentamiento.

---

## 4. Requisitos de calidad / verificación (PBT parcial)

- Las 7 propiedades del Functional Design §8 se implementan con Hypothesis.
- Cobertura objetivo del núcleo del motor: alta en ramas de derivación (las reglas de los 6 modelos).
- `to_dict()`/`from_dict()` deben cumplir **round-trip**: `from_dict(to_dict(x)) == x` (propiedad PBT adicional, encaja con RNF-6).

---

## 5. Requisitos de internacionalización (D6)

- U1 no traduce; transporta claves/textos i18n `{es, en}` en nombres de modelo y etiquetas de error de dominio.
- Los enums (tipos de período, microciclo, fase) son **claves estables en inglés** internas; la UI (U5) mapea a texto bilingüe. El motor nunca decide el idioma mostrado.

---

## 6. Restricciones

- No usar fecha/hora del sistema dentro del motor (rompería determinismo). Las fechas entran por `SeasonParams`.
- No usar aleatoriedad.
- No leer variables de entorno ni archivos.
