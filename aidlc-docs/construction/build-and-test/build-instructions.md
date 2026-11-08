# Instrucciones de Build

**Proyecto**: Agente de Fútbol. **Lenguaje**: Python 3.11+ (probado en 3.14). **Raíz**: `/kiro`.

## 1. Requisitos
- Python 3.11 o superior.
- No se necesita compilación: es Python puro.

## 2. Entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
```

## 3. Dependencias
El **núcleo funciona sin dependencias de terceros** (RNF-2 offline). Las dependencias son opcionales por grupo:

```bash
# Para correr los tests:
pip install hypothesis pytest

# Para la app web (RF-2):
pip install '.[web]'             # FastAPI + uvicorn + python-multipart

# Para PDF nativo (RF-6, opcional):
pip install '.[pdf]'             # WeasyPrint

# Para LLM en la nube (RF-10, opcional):
pip install '.[llm]'             # SDK del proveedor
```

## 4. Estructura instalable
Definida en `pyproject.toml`:
- `periodization_engine` (+ `.models`) — motor reutilizable.
- `app` y submódulos: `football_domain` (+ `.adapted`), `diagrams`, `persistence`, `planning_service`, `llm`, `interface`, `player_tracking`.

## 5. Verificación del build
```bash
.venv/bin/python -c "import periodization_engine, app.football_domain, app.diagrams, app.persistence, app.planning_service, app.player_tracking; print('imports OK')"
```
