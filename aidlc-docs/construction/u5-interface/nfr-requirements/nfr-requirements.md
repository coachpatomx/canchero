# NFR Requirements — U5 Interfaz Web + Chat + LLM

**Hereda**: stack Python 3.11+.

## 1. Tecnología
- **Orquestador** (`planning_service/`, `llm/`): Python stdlib puro. **Sin** dependencia de FastAPI (RNF-1: núcleo desacoplado de la UI; reutilizable si se escala a web multiusuario).
- **Web** (`interface/`): **FastAPI + uvicorn**, dependencia opcional grupo `web`. Server-rendered HTML (sin build de frontend).
- **LLM**: conector genérico; SDKs de proveedores son dependencias opcionales (grupo `llm`), import perezoso. Por defecto NullConnector (offline).

## 2. NFR aplicables
| NFR | Aplica | Cómo |
|-----|--------|------|
| RNF-1 local escalable | Sí | Orquestador sin UI; la web es una capa fina encima. |
| RNF-2 offline | Sí | Todo el flujo determinista sin red; LLM opcional. |
| RNF-3 secretos | Sí | API key solo por variable de entorno; nunca en código ni en disco de datos. |
| RF-10 híbrido | Sí | estructura determinista + texto LLM opcional. |
| D6 bilingüe | Sí | render por idioma. |

## 3. Rendimiento
- generate_plan de temporada completa < 300 ms (sin LLM). Render de página < 100 ms.

## 4. Verificación (PBT parcial)
- 6 propiedades del Functional Design §8: trazabilidad, no-inventar-macro, LLM-off-determinista, herencia de carga, round-trip, secretos.
- Tests del orquestador **sin** levantar servidor (lógica pura); tests de la web con el TestClient de FastAPI.

## 5. Restricciones
- SDK de LLM y FastAPI con import perezoso / dependencia opcional; los tests core no los requieren.
- Nunca registrar (log) la API key.
- El orquestador no importa FastAPI.
