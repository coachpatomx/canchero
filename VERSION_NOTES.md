# Canchero — Notas de versión

## v1.0 (noviembre 2026)

Primera versión completa y funcional. 90 tests en verde.

### Lo que incluye
- **Hub de inicio** con 3 tarjetas: Macrociclos, Sesiones, Equipo.
- **Macrociclos**
  - Creación conversacional (entrevista guiada / modo experto) con opciones, explicación y recomendación de modelo de periodización.
  - Edición por chat: volumen/intensidad por semana o mesociclo, marcar descarga, objetivos, nombre de equipo/entrenador/coordinador, título, fecha de inicio y competencias.
  - Matriz tipo Excel: periodos, mesos, microciclos, meses y fechas reales, fila de sesiones, competencias que cruzan su columna, rejillas de volumen/capacidades/aspectos. Imprimible apaisado con colores. Escudo del club como marca de agua.
- **Sesiones**
  - Creación conversacional (entrevista) y edición por chat (más/menos intensa, variantes, duración total o por bloque, agregar ejercicio, cambiar plantilla, metadatos).
  - "Dibuja …": genera el diagrama de un bloque desde la descripción en lenguaje natural.
  - Dos plantillas de hoja (Canchero / Fútbol Inclusivo), automática según formato.
  - Diagramas consistentes: una cancha base por sesión (oficial de ciegos cuando aplica), flechas tipadas, conos, jugadores numerados; imagen genérica para estiramiento.
- **IA**: OpenAI / Anthropic / Ollama / cadena. Fallback por reglas offline. Autodiagnóstico en `/diag`. Indicador "Chambeando…" al generar.
- **Modalidades**: fútbol 11, 7, sala; adaptados: ciegos (blind_5), PC (cp_7), Down, amputados.
- **6 modelos** de periodización + personalizados.

### Pendientes conocidos (para v2)
- La colocación/orden de jugadores en el diagrama depende del LLM; mejora con descripciones claras (no 100% garantizado).
- El chat por reglas (sin OpenAI) es limitado por diseño; la inteligencia real viene del LLM.
- El export a **Excel** de la matriz aún es el básico (el PDF por impresión ya sale con formato/colores).

### Backlog (próximas versiones)
- Darle la vuelta a la hoja *Canchero* con la estructura tipo América U19.
- Módulo **Equipo** multidisciplinario (nutrición, psicología, profilaxis) — hoy placeholder.
- **Login / multiusuario** (cada entrenador su historial privado) — requiere base de datos.
- **Deploy online** para compartir con otros entrenadores — requiere servidor/nube + costos.
- Entrevista de sesión en modo experto; memoria de conversación / deshacer.

### Cómo correr
```
python run_web.py   →  http://127.0.0.1:8000
```
Diagnóstico de IA: `http://127.0.0.1:8000/diag`
