# Agente de Fútbol

Planificador de entrenamientos de fútbol que **encadena macrociclo → mesociclo → sesión** de forma coherente, con diagramas de cancha de lo que se va a practicar. Local primero, agnóstico al tipo de fútbol (11, 7, sala y modalidades adaptadas), construido con metodología determinista + LLM opcional.

/ Football training planner that chains macrocycle → mesocycle → session coherently, with pitch diagrams. Local-first, format-agnostic, deterministic engine + optional LLM.

## Qué hace

- Genera un **plan de temporada** a partir de parámetros (duración, días/semana, partidos, modelo, formato) y deriva mesociclos, microciclos y sesiones coherentes, con sus cargas.
- Permite pedir una **sesión concreta en lenguaje natural** ("esta semana quiero una sesión de conducción en espacio reducido") y la **alinea al macrociclo vigente** — sin inventar un macro si no existe.
- Dibuja **diagramas SVG** de cada tarea (jugadores, conos, balón, zonas) y de las modalidades adaptadas (vallas, guía en fútbol para ciegos).
- Guarda el historial y la biblioteca de ejercicios en **JSON portable**, y exporta a documento imprimible (HTML siempre; **PDF** con un clic si instalas WeasyPrint).
- **Seguimiento individual** por jugador (Potenciar / Mejorar / Eliminar).

## Modalidades soportadas (v1)

Convencional: fútbol 11 (base), 7, sala. Adaptado: **fútbol 5 ciegos**, **fútbol 7 PC**, **Down/discapacidad intelectual**, **amputados**. (Las reglas finas de PC/Down/amputados están marcadas como pendientes de validación.)

## Modelos de periodización (6 + personalizados)

Tradicional (Matveyev), Por bloques (Issurin), ATR, Periodización Táctica (Frade), Entrenamiento Estructurado (Seirul·lo), y Esquema de A. González para torneos cortos. Puedes registrar el tuyo.

## Instalación y uso

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install '.[web]'          # app web local
python run_web.py             # abre http://127.0.0.1:8000
```

Opcionales:
```bash
pip install '.[pdf]'          # PDF nativo (WeasyPrint)
pip install '.[llm]'          # OpenAI + Anthropic (Ollama no necesita SDK)
```

### LLM opcional (3 proveedores enchufables)

El enriquecimiento con IA es opcional; el agente funciona completo sin él. Elige proveedor con una variable de entorno (la clave **nunca** va en el código):

```bash
# OpenAI (pago por uso; carga unos pocos USD de saldo de API, no ChatGPT Plus)
export AGENTE_LLM_PROVIDER=openai
export AGENTE_LLM_MODEL=gpt-4o-mini
export AGENTE_LLM_API_KEY_VAR=OPENAI_API_KEY
export OPENAI_API_KEY=sk-...        # tu clave real, solo en tu entorno

# Anthropic (Claude): AGENTE_LLM_PROVIDER=anthropic + ANTHROPIC_API_KEY

# Ollama (local, gratis, offline): instala Ollama aparte, luego:
export AGENTE_LLM_PROVIDER=ollama
export AGENTE_LLM_MODEL=llama3

# Cadena de respaldo (usa el primero disponible; nunca deja sin respuesta):
export AGENTE_LLM_PROVIDER=chain
export AGENTE_LLM_CHAIN=ollama,openai
```

Si no configuras nada, el agente usa el modo determinista (offline, gratis).

## Tests

```bash
pip install hypothesis pytest
python -m pytest -q            # 89 passed
```

## Arquitectura

```
periodization_engine/   # motor determinista reutilizable (sin fútbol)
app/
  football_domain/      # formatos, ejercicios, modalidades adaptadas
  diagrams/             # render SVG
  persistence/          # JSON + export HTML/PDF
  planning_service/     # orquestador (encadena todo)
  llm/                  # conector LLM opcional
  interface/            # web local (FastAPI)
  player_tracking/      # seguimiento individual
data/                   # tus planes y biblioteca (JSON, respaldo = copiar la carpeta)
```

El motor de periodización es un paquete independiente y reutilizable: un futuro agente de otro deporte puede usarlo sin tocar el fútbol.

## Privacidad

Agente local de un solo usuario. Los nombres de jugadores y planes se guardan solo en tu carpeta `data/`. Funciona sin conexión; el LLM es el único componente que requiere internet y es opcional.
