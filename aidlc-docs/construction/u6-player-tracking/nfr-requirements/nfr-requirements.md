# NFR Requirements — U6 Seguimiento Individual

**Hereda**: stack Python 3.11+.

## 1. Tecnología
- Python stdlib puro, paquete `app/player_tracking/`. Depende de U2 (posiciones) e I18nText de U1.
- Sin dependencias de terceros.

## 2. NFR aplicables
| NFR | Aplica | Cómo |
|-----|--------|------|
| RNF-6 portabilidad | Sí | Roster serializable a dict JSON (round-trip) para que U4 lo guarde. |
| RNF-2 offline | Sí | Todo local. |
| D6 bilingüe | Sí | contenido de objetivos y observaciones en I18nText. |
| PII | Sí | nombres reales de jugadores = datos locales del usuario; no se transmiten a terceros. |

## 3. Verificación (PBT parcial)
- 6 propiedades del Functional Design §6: inmutabilidad, rango de progreso, mastered, trazabilidad, round-trip, selección de objetivos de sesión.

## 4. Restricciones
- Sin reloj interno (created_at inyectado).
- Inmutabilidad: las operaciones devuelven copias nuevas.
