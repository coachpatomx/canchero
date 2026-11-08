# Instrucciones de Tests de Integración

## 1. Integración entre unidades (automática)
- **U1→U2**: `tests/test_football_domain.py::test_integration_u1_u2_full_session`
- **U1→U4**: `tests/test_persistence.py::test_repository_save_load` (plan completo del motor)
- **U5 end-to-end (HTTP)**: `tests/test_webapp.py::test_create_plan_then_aligned_session`

```bash
.venv/bin/python -m pytest tests/test_football_domain.py tests/test_persistence.py tests/test_webapp.py -q
```

## 2. Prueba manual end-to-end (tu caso de uso)
```bash
pip install '.[web]'
python run_web.py        # http://127.0.0.1:8000
```
1. En la home, crea un plan de temporada (modelo `football_gonzalez`, formato `blind_5`, 17 semanas).
2. En "Sesión en lenguaje natural", escribe: *"esta semana quiero una sesión de conducción en espacio reducido"*.
3. Resultado esperado: sesión con banner verde **"Alineada al macrociclo vigente"**, diagrama SVG de cancha (con vallas/guía si es ciegos) y el contenido de conducción.
4. Abre el HTML imprimible y usa "Imprimir → Guardar como PDF".

## 3. Verificar degradaciones (robustez)
- **Sin WeasyPrint**: `is_pdf_available()` → False; el PDF se obtiene vía navegador.
- **Sin LLM**: NullConnector; toda la generación es determinista.
- **Sin macro**: la sesión se marca "sin macro" (banner rojo); el agente no inventa macro.
