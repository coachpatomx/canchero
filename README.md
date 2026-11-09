# Canchero — Agente de Fútbol

**Canchero** es un agente planificador de fútbol que encadena **macrociclo → mesociclo → microciclo → sesión** de forma coherente, con diagramas de cancha, y donde **conversas con el agente** para crear y ajustar todo. Local primero, agnóstico al tipo de fútbol (11, 7, sala y modalidades adaptadas), con motor determinista + LLM opcional (OpenAI / Claude / Ollama).

Tagline: *Sí la mueve planificando.*

## Qué hace (v1)

- **Hub de inicio** con 3 entradas: 🗓️ Macrociclos · 📋 Sesiones · 👥 Equipo.
- **Crear el macrociclo conversando** (entrevista estilo AI-DLC): el agente te hace preguntas (equipo, formato, semanas, fecha de inicio, modelo…) con opciones, explicación y recomendación. Modo **guiado** (paso a paso) o **experto** (una sola frase).
- **Editar el macrociclo hablando**: "sube el volumen de la semana 5", "marca la semana 8 como descarga", "competencia el 24 de agosto vs Cruz Azul", "cambia el título". Vista previa en vivo.
- **Macrociclo como matriz tipo Excel**: periodos, mesos, microciclos, **fechas de calendario reales**, fila de **sesiones**, **competencias que cruzan su columna**, rejilla de volumen/capacidades/aspectos; imprimible (apaisado) con colores. Escudo del club como marca de agua.
- **Crear sesiones conversando** y **editarlas hablando**: "hazla más intensa", "agrega una variante al calentamiento", "agrega otro ejercicio de tiro a puerta", "ponla a 75 minutos", y **"dibuja 5 jugadores en una banda y 5 en otra que conducen y pasan a media cancha"** → genera el diagrama desde tu descripción.
- **Dos plantillas de hoja**: *Canchero* (oscuro) y *Fútbol Inclusivo* (estilo profesional con encabezado equipo/entrenador/fecha). Se elige automáticamente según el formato (modalidad adaptada → Inclusivo).
- **Diagramas SVG consistentes**: una sola cancha base por sesión (cancha oficial de fútbol 5 ciegos cuando aplica: vallas, áreas, porterías, tercios), con flechas tipadas (pase punteada, conducción ondulada, carrera sólida), conos y jugadores numerados.
- **Autodiagnóstico del LLM** en `/diag` (dice si OpenAI está conectado y prueba una llamada real).
- Historial en **JSON portable**; export a HTML/PDF imprimible.
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
python -m pytest -q            # 90 passed
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
