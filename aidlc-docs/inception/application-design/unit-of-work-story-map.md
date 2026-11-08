# Mapa de Requisitos → Unidades — Agente de Fútbol

**Etapa**: INCEPCIÓN → Units Generation
**Nota**: Se omitió la etapa de User Stories (usuario único). Este mapa sustituye el "story map" usando **capacidades / flujos de uso** derivados de los requisitos funcionales, asignados a unidades. Garantiza que ningún requisito queda sin dueño.

---

## Capacidades de usuario (flujos) → unidades

| # | Capacidad / flujo de uso | Requisitos | Unidad principal | Apoyo |
|---|--------------------------|-----------|------------------|-------|
| F1 | **Armar el macrociclo** a partir de datos de temporada (de una vez o por partes) | RF-1, RF-4 | U1 | U5 (orquestador, entrada) |
| F2 | **Bajar la metodología**: derivar meso → micro → sesiones coherentes | RF-1, RNF-5 | U1 | U5 |
| F3 | **Elegir/definir modelo de periodización** (5 precargados + propio) | RF-4 | U1 | U5 |
| F4 | **Generar una sesión** con tareas coherentes con la fase y la carga | RF-1 | U5 (orq.) | U1, U2 |
| F5 | **Pedir una sesión suelta en lenguaje natural** alineada al macro ("conducción en espacio reducido esta semana") | RF-11 | U5 (orq.) | U1, U2, U3 |
| F6 | **Describir ejercicios** (tipo, dimensiones, materiales, carga, volumen, aspectos) | RF-1, RF-9 | U2 | U5, LLM(U5) |
| F7 | **Generar diagramas** de cancha (tarea y organización) en SVG | RF-5 | U3 | U2 |
| F8 | **Ver gráficas de carga** (volumen/intensidad por micro/meso) | RF-5 | U3 | U1 |
| F9 | **Elegir formato de fútbol** (11, 7, sala, ciegos) | RF-7 | U2 | — |
| F10 | **Activar adaptaciones** de fútbol adaptado (balón sonoro, guías, zonas) | RF-8 | U2 (adapted) | — |
| F11 | **Seguimiento individual**: roster, objetivos Potenciar/Mejorar/Eliminar, observaciones | (indiv.) | U6 | U2, U5 |
| F12 | **Editar la planificación** por formulario o chat y regenerar | RF-6, RF-3 | U5 (orq.) | todas |
| F13 | **Doble modo de entrada**: parámetros (formulario) y entrevista (preguntas) | RF-3 | U5 | U1 |
| F14 | **Guardar/reabrir** planes y **biblioteca** de ejercicios | RF-9 | U4 | U2 |
| F15 | **Exportar a PDF** imprimible bilingüe | RF-6, D6 | U4 | U3, U6 |
| F16 | **Enriquecer contenido** con LLM opcional (nube o local) | RF-10 | U5 (conector) | — |
| F17 | **Funcionar sin conexión** (solo reglas) | RNF-2 | U1, U2, U3, U4 | — |
| F18 | **Respaldar datos** copiando una carpeta (JSON) | RNF-6 | U4 | — |
| F19 | **Seleccionar idioma** es/en | D6 | U5 | U2 (catálogos) |

---

## Cobertura por unidad

- **U1 Motor**: F1, F2, F3, F4(apoyo), F8(apoyo), F13(apoyo), F17.
- **U2 Dominio Fútbol**: F6, F9, F10, F11(apoyo), F14(apoyo), F17, F19(apoyo).
- **U3 Diagramas**: F7, F8, F15(apoyo), F17.
- **U4 Persistencia/Export**: F14, F15, F17, F18.
- **U5 Interfaz+Orquestador**: F4, F5, F12, F13, F16, F19; coordina F1–F15.
- **U6 Seguimiento Individual**: F11.

**Verificación**: cada flujo F1–F19 tiene unidad responsable; cada unidad U1–U6 tiene al menos un flujo. Sin huecos ni requisitos huérfanos.

---

## Primeras capacidades a construir (hilo end-to-end, Q2=A)

Para ver valor pronto, el primer hilo vertical cubre: **F1 → F2 → F4 → F6 → F7 → F14 → F15** (armar macro → bajar a sesión → describir ejercicio → diagrama → guardar → PDF), con fútbol 11 + ciegos (Q4=A). Luego se suma **F11** (seguimiento individual) y el resto (F3 completo, F5, F9 7/sala, F10, F12 chat, F16 LLM, F19 bilingüe).
