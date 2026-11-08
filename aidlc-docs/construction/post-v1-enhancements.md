# Mejoras post-v1 (2026-11-07) — tanda solicitada por el usuario

Tras cerrar la construcción (80 tests), el usuario pidió completar tres puntos
que estaban como "siguiente iteración". Resultado: **89 tests passed**.

## 1. Modalidades adaptadas corregidas con reglamentos oficiales

Se verificaron fuentes oficiales y se corrigieron los 4 perfiles. Cada perfil
ahora lleva `governing_body` y `source_url`, y sus reglas pasan a `validated=True`
(salvo notas de aplicación local).

| Modalidad | Federación | Correcciones aplicadas |
|-----------|-----------|------------------------|
| Ciegos (fútbol 5) | **IBSA** (Laws 2025-2029) | 4 jugadores de campo B1 + portero (vidente/B2/B3); clasificación fijada a B1 en campo. |
| PC (fútbol 7) | **IFCPF** | Regla de composición: ≥1 FT1 y ≤1 FT3 en campo; 2×30 min; confirmadas sin-offside y saque con una mano. |
| Down / DI | **Virtus** | Corrección conceptual: clases II1/II2/II3; **Down = II2** (DI + impedimento adicional); elegibilidad CI ≤ 75 antes de los 22. |
| Amputados | **WAFF** | Confirmado 7 (6 campo + portero); jugadores de campo con muletas de antebrazo sin prótesis; portero amputación de brazo. |

Fuentes: ibsasport.org, ifcpf.com, virtus.sport, amputeefootball.org (contenido
reformulado para cumplir licencias). Nota: el usuario (experto en ciegos) sigue
siendo la autoridad final; las reglas son datos editables.

## 2. Conectores LLM reales + cadena de respaldo

- `openai_connector.py` (OpenAI, SDK opcional, clave por entorno).
- `anthropic_connector.py` (Claude, SDK opcional).
- `ollama_connector.py` (local/gratis, HTTP stdlib, sin dependencias).
- `chain_connector.py` (fallback ordenado, p. ej. `ollama,openai` → Null).
- `build_connector` elige según `AGENTE_LLM_PROVIDER`; `enrich_session` ya usa el
  LLM para reescribir SOLO la redacción del objetivo (nunca estructura/cargas).
- Todos degradan limpio: sin SDK/clave/servidor → `is_enabled()=False`, sigue
  determinista. Verificado por `tests/test_llm_connectors.py` (sin red ni claves).

### Configuración (ejemplo OpenAI)
```
export AGENTE_LLM_PROVIDER=openai
export AGENTE_LLM_MODEL=gpt-4o-mini
export AGENTE_LLM_API_KEY_VAR=OPENAI_API_KEY
export OPENAI_API_KEY=sk-...        # solo en tu entorno
# o cadena de respaldo local-primero:
export AGENTE_LLM_PROVIDER=chain
export AGENTE_LLM_CHAIN=ollama,openai
```

## 3. Pantallas de roster en la web (U6 friendly)

- `GET /roster`: lista de jugadores con sus objetivos (Potenciar/Mejorar/Eliminar + progreso).
- `POST /roster/player`: añadir jugador por nombre y posición.
- `POST /roster/objective`: asignar objetivo individual.
- Enlace desde la home. Verificado por HTTP (añadir jugador aparece en pantalla).

## Estado
- Suite: **89 passed**.
- Dependencias opcionales nuevas: grupo `llm` ahora incluye `anthropic`. Ollama no
  requiere SDK. Nada de esto es necesario para el modo offline por defecto.
