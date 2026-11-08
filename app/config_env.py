"""Carga de variables desde un archivo .env (sin dependencias).

Lee pares CLAVE=VALOR de un archivo .env en la raíz del proyecto y los coloca en
os.environ SI no están ya definidos (las variables reales del entorno tienen
prioridad). Seguridad (RNF-3): la clave vive solo en tu .env local, nunca en el
código ni en el repositorio (.env está en .gitignore).
"""
from __future__ import annotations

import os


def load_dotenv(path: str = ".env") -> int:
    """Carga variables de `path` en os.environ. Devuelve cuántas cargó.

    - Ignora líneas vacías y comentarios (#).
    - No sobrescribe variables ya presentes en el entorno.
    - Acepta comillas opcionales alrededor del valor.
    """
    if not os.path.exists(path):
        return 0
    loaded = 0
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
                loaded += 1
    return loaded
