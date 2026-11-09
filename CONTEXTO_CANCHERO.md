# Canchero — Contexto del proyecto (respaldo para la IA)

Si se pierde el hilo del chat, cárgame este archivo para retomar con todo el contexto.

## Quién y qué
- Usuario: **coachpatomx** (Patricio Ramírez Ríos), entrenador de fútbol inclusivo (ciegos y débiles visuales) y otras modalidades.
- Proyecto: **Canchero**, agente planificador de fútbol. Tagline: "Sí la mueve planificando".
- Construido con metodología AI-DLC. Responder SIEMPRE en español, tono directo y claro.

## Dónde vive
- Workspace de desarrollo (donde trabaja la IA): `/kiro`.
- Compu del usuario (Windows): `C:\Users\pator\canchero`. Python + Git instalados.
- Repo privado: `github.com/coachpatomx/canchero` (rama `main`).
- Flujo de subida: la IA hace commit en `/kiro` y push con el token del usuario:
  `git push https://coachpatomx:TU_TOKEN@github.com/coachpatomx/canchero.git main`
  (el usuario revoca el token tras cada push porque se ve en el chat).
- En la compu: `git pull` → `.venv\Scripts\python run_web.py` → `http://127.0.0.1:8000` → Ctrl+Shift+R.
- Diagnóstico de IA: `/diag`.

## Estado técnico
- **90 tests en verde** (`.venv/bin/python -m pytest -q`).
- LLM: conectores OpenAI (gpt-4o-mini, activo en la compu del usuario), Anthropic, Ollama, chain. Config por `.env`:
  `AGENTE_LLM_PROVIDER=openai`, `AGENTE_LLM_MODEL=gpt-4o-mini`, `AGENTE_LLM_API_KEY_VAR=OPENAI_API_KEY`, `OPENAI_API_KEY=sk-...` (sin `#`).
- Sin LLM, todo degrada a modo determinista/reglas (nunca se rompe).

## Arquitectura (unidades)
- `periodization_engine/` — motor determinista (6 modelos de periodización; agnóstico al deporte).
- `app/football_domain/` — formatos (football_11/7, futsal, blind_5, cp_7, down, amputee) + perfiles adaptados.
- `app/diagrams/` — SVG: `svg_primitives`, `pitch`, `drill_diagram` (cancha de ciegos, flechas tipadas), `load_chart`.
- `app/persistence/` — JSON + `html_export.py` (hoja de sesión, matriz de macro, plantillas Canchero/Inclusivo) + `json_repository.py` (save/load/update_session, save_plan_meta).
- `app/planning_service/` — `orchestrator.py` (genera plan/sesión + LLM), `plan_editor.py` (chat del macro), `session_editor.py` (chat de sesión), `macro_interview.py` y `session_interview.py` (entrevistas), `calendar_map.py` (fechas), `session_author.py` (prompt de sesión).
- `app/interface/` — `webapp.py` (rutas FastAPI, GET), `templates.py` (toda la UI), `static/` (logo canchero.svg/png, escudo-inclusivo.png, escudo-club.png).
- `app/player_tracking/` — roster y objetivos individuales.

## Decisiones clave
- **Formularios web por GET** (el preview de Kiro bloquea POST).
- **Diagramas**: la IA devuelve datos estructurados (jugadores/conos/flechas en metros) y el motor los dibuja offline. **Una sola cancha base por sesión** (consistente en todos los bloques); cancha oficial de fútbol 5 ciegos (40x20: vallas, áreas, 2 porterías, tercios) cuando el formato es adaptado. Flechas: pase punteada roja, conducción ondulada amarilla, carrera sólida blanca. Jugadores numerados (a=azul, b=amarillo, c=verde).
- **Dos plantillas de hoja**: `dark` (Canchero) y `inclusivo` (estilo América). Automática por formato (adaptado → inclusivo). Escudo de club como marca de agua (genérico `escudo-club.png`).
- **Chat iterativo (agente)**: el usuario quería que NO fuera un formulario sino conversar. Hecho para macro y sesión: crear hablando + editar hablando, con OpenAI (lista de acciones) y fallback por reglas. Respuesta genérica si es fuera de tema (no se buguea). Overlay "Chambeando…" al generar.
- **Matriz del macro**: tipo Excel, con fechas reales (desde la fecha de inicio), fila de sesiones (según días/semana), competencias que cruzan su columna; colores forzados al imprimir (`print-color-adjust`).
- Estado de las entrevistas viaja como JSON en la URL (cuidado con la doble codificación: JSON crudo en inputs de form, URL-encoded en enlaces — ya corregido).

## Bugs ya resueltos (no repetir)
- Diagramas "chorizo" vertical → ahora apaisados, aspecto acotado.
- Loop en entrevistas guiado/experto → por doble codificación de `answers`; corregido.
- Chat que se "comía" frases (nombre de equipo) → ahora parte varias instrucciones.
- Fechas que caían en 2024 → usan el año de la fecha de inicio del plan.
- Una fecha suelta ya no cambia el inicio del macro (pide aclarar).
- Canchas inconsistentes entre bloques → una sola cancha base por sesión.
- Chat de sesión aplicaba una sola acción → ahora varias en una oración.

## Pendientes / backlog
- Colocación de jugadores en diagrama más fiel (depende del LLM; afinar prompt con ejemplos reales del usuario).
- Hoja Canchero con estructura tipo América U19.
- Módulo Equipo multidisciplinario (nutrición/psicología/profilaxis) — hoy placeholder.
- Login / multiusuario (necesita base de datos, hoy es JSON por carpeta).
- Deploy online (servidor/nube + costos) — dejar paso a paso.
- Export Excel de la matriz con formato/colores (hoy solo el básico; el PDF por impresión ya sale bien).

## Cómo subir cambios (recordatorio)
1. En `/kiro`: `git add <archivos>` → `git commit -m "..."`.
2. `git push https://coachpatomx:TOKEN@github.com/coachpatomx/canchero.git main`.
3. El usuario: revoca el token, hace `git pull` en su compu, reinicia y Ctrl+Shift+R.
