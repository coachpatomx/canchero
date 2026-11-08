"""Autor de sesiones enriquecidas por LLM (RF-10).

Construye un prompt EXPERTO con todo el contexto (modalidad adaptada, categoría,
fase del microciclo, carga objetivo, fundamentos, materiales) y pide al LLM una
sesión estructurada al nivel de una plantilla profesional: calentamiento →
parte física → actividades con variantes → juego/partido condicionado →
vuelta a la calma. Degrada a la plantilla determinista si no hay LLM.

La ESTRUCTURA (fase del micro, carga, duración) la fija el motor (determinista);
el LLM solo redacta el CONTENIDO dentro de ese marco (RF-10).
"""
from __future__ import annotations

import json

from app.football_domain import get_format
from app.football_domain.adapted.profiles import PROFILES

# Vocabulario de apoyo por modalidad adaptada para guiar al LLM.
_MODALITY_BRIEF = {
    "blind_5": (
        "Fútbol 5 para ciegos (IBSA). 4 jugadores de campo B1 con antifaz + portero "
        "vidente. Balón sonoro, vallas laterales, guía tras portería. El jugador dice "
        "'voy' al disputar. Prioriza orientación por sonido, comunicación verbal "
        "constante, recepción perfilada y conducción con balón sonoro."
    ),
    "cp_7": (
        "Fútbol 7 PC (IFCPF). Parálisis cerebral, clasificación FT1-FT3. Sin fuera de "
        "juego, saque de banda con una mano. Adapta ritmo y complejidad al perfil "
        "funcional; cuida equilibrio y transiciones."
    ),
    "down": (
        "Fútbol para personas con síndrome de Down / discapacidad intelectual (Virtus). "
        "Instrucciones simples y progresivas, mucha repetición y refuerzo positivo, "
        "consignas claras y demostración."
    ),
    "amputee": (
        "Fútbol para amputados (WAFF). Jugadores de campo con muletas de antebrazo sin "
        "prótesis; portero con amputación de brazo. Cuida equilibrio, apoyos y fatiga "
        "por uso de muletas."
    ),
    "football_11": "Fútbol 11 convencional.",
    "football_7": "Fútbol 7 convencional.",
    "futsal": "Fútbol sala.",
}


def build_prompt(request, fmt, micro_ctx: dict, lang: str = "es") -> str:
    """Arma el prompt del LLM con todo el contexto disponible."""
    modality = _MODALITY_BRIEF.get(fmt.id, fmt.name.es)
    players = request.n_players or fmt.players_on_field

    ctx_lines = [
        f"- Modalidad: {modality}",
        f"- Formato: {fmt.name.es} ({players} jugadores por equipo)",
        f"- Duración total objetivo: {request.duration_min} minutos",
    ]
    if request.category:
        ctx_lines.append(f"- Categoría/edad: {request.category} (ajusta volumen, "
                         "complejidad y lenguaje a esta edad)")
    if request.schedule:
        ctx_lines.append(f"- Horario: {request.schedule}")
    if micro_ctx:
        ctx_lines.append(
            f"- Posición en la temporada: semana {micro_ctx.get('week')}, "
            f"microciclo tipo '{micro_ctx.get('micro_type')}', "
            f"carga objetivo volumen {micro_ctx.get('volume')}% / "
            f"intensidad {micro_ctx.get('intensity')}%, "
            f"fase del día '{micro_ctx.get('phase')}'. "
            "RESPETA esta carga: no propongas una sesión más dura ni más suave."
        )
    if request.technical_focus:
        ctx_lines.append(f"- Fundamento técnico a trabajar: {request.technical_focus}")
    if request.tactical_focus:
        ctx_lines.append(f"- Fundamento táctico: {request.tactical_focus}")
    if request.physical_focus:
        ctx_lines.append(f"- Capacidad física: {request.physical_focus}")
    if request.materials:
        ctx_lines.append(f"- Material disponible: {request.materials}")
    context = "\n".join(ctx_lines)

    schema = (
        '{\n'
        '  "titulo": "string",\n'
        '  "objetivo": "string (objetivo general de la sesión)",\n'
        '  "objetivo_especifico": "string",\n'
        '  "bloques": [\n'
        '    {\n'
        '      "fase": "calentamiento|activacion|parte_principal|juego|vuelta_calma",\n'
        '      "nombre": "string",\n'
        '      "duracion_min": number,\n'
        '      "dimensiones": "string (ej. 15x15 m)",\n'
        '      "descripcion": "string (instrucciones claras y accionables)",\n'
        '      "variantes": ["string", "string"],\n'
        '      "materiales": ["string"],\n'
        '      "aspectos": {"tecnico": ["string"], "tactico": ["string"], '
        '"fisico": ["string"], "psicologico": ["string"]},\n'
        '      "diagrama": {\n'
        '        "ancho_m": number, "alto_m": number,\n'
        '        "jugadores": [{"x": number, "y": number, "equipo": "a|b", "num": number}],\n'
        '        "conos": [{"x": number, "y": number}],\n'
        '        "porterias": [{"x": number, "y": number}],\n'
        '        "balones": [{"x": number, "y": number}],\n'
        '        "zonas": [{"x": number, "y": number, "w": number, "h": number, "etiqueta": "string"}],\n'
        '        "flechas": [{"x1": number, "y1": number, "x2": number, "y2": number, '
        '"tipo": "carrera|conduccion|pase"}]\n'
        '      }\n'
        '    }\n'
        '  ],\n'
        '  "carga_total": "string (ej. media-alta)",\n'
        '  "notas_adaptacion": "string (adaptaciones específicas de la modalidad)"\n'
        '}'
    )

    return (
        "Eres un preparador físico y entrenador experto en fútbol y en fútbol "
        "adaptado, con dominio de la metodología de periodización (FMF/MBP). "
        "Diseña UNA sesión de entrenamiento completa, realista y lista para llevar "
        "a la cancha, coherente con el contexto dado.\n\n"
        f"Petición del entrenador: \"{request.text}\"\n\n"
        f"Contexto:\n{context}\n\n"
        "Requisitos de la sesión (sigue esta estructura profesional, como una "
        "plantilla real de entrenador):\n"
        "1) CALENTAMIENTO: movilidad articular (lista concreta de movimientos con "
        "repeticiones/tiempo) + activación (desplazamientos, cambios de ritmo). "
        "Puede incluir conducción suave si el tema lo amerita.\n"
        "2) PARTE FÍSICA (si la fase/carga lo pide): trabajo específico (p. ej. "
        "HIIT, series, cambios de dirección) con tiempos y repeticiones.\n"
        "3) 1 a 3 ACTIVIDADES PRINCIPALES: con pasos numerados (qué hace cada "
        "jugador, el guía, el portero), progresión y 2-3 variantes por actividad.\n"
        "4) JUEGO / PARTIDO CONDICIONADO: formato, nº de equipos, regla que fuerza "
        "el contenido trabajado, tiempos.\n"
        "5) VUELTA A LA CALMA: estiramientos concretos y breve reflexión.\n"
        "- Las duraciones de los bloques DEBEN sumar aprox. la duración total pedida.\n"
        "- Instrucciones accionables y específicas, nada genérico. Usa el "
        "vocabulario del fútbol (perfilar, conducir, apoyo, desmarque, etc.).\n"
        "- Incluye las adaptaciones propias de la modalidad cuando aplique "
        "(p. ej. balón sonoro, decir 'voy', guía, antifaz en ciegos).\n"
        "- Ajusta volumen/complejidad a la categoría/edad indicada.\n"
        "- Etiqueta aspectos técnico/táctico/físico/psicológico por bloque.\n"
        "- Para CADA bloque incluye un 'diagrama' que represente fielmente el "
        "ejercicio: coordenadas en METROS con origen en la esquina inferior "
        "izquierda (x derecha, y arriba), dentro de ancho_m x alto_m (usa las "
        "dimensiones del bloque). Coloca jugadores (equipo 'a' azul / 'b' rojo, "
        "numerados), conos que delimiten el área o formen puertas, porterías si "
        "hay tiro, balones, zonas resaltadas, y flechas tipadas: 'carrera' "
        "(desplazamiento del jugador), 'conduccion' (lleva el balón), 'pase' "
        "(envío del balón). El diagrama debe COINCIDIR con la descripción "
        "(mismo nº de jugadores y espacio).\n\n"
        f"Responde ÚNICAMENTE con un JSON válido con este esquema (sin texto extra):\n{schema}"
    )


def parse_llm_session(raw: str) -> dict | None:
    """Extrae el JSON de la respuesta del LLM. None si no se puede parsear."""
    if not raw:
        return None
    text = raw.strip()
    # El modelo a veces envuelve en ```json ... ```
    if "```" in text:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            text = text[start:end + 1]
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "bloques" in data:
            return data
    except (json.JSONDecodeError, ValueError):
        return None
    return None
