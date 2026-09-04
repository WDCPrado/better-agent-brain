#!/usr/bin/env python3
"""Hook UserPromptSubmit: avisa cuando la sesión avanzó y el cerebro sigue igual.

Se mide en mensajes desde el último cambio del vault. La huella es la fecha del
.md más reciente, así que escribir una nota reinicia la cuenta sola: no hay un
contador que alguien tenga que limpiar a mano.

No sabe nada de git a propósito. Publicar el vault —si es que se publica— es
decisión de quien lo escribe, no de este sistema.

Todo en Python y sin dependencias para que corra igual en Linux, macOS y
Windows: `find -printf` y `timeout` son de GNU, y bash no existe en Windows.

Nunca bloquea ni falla ruidosamente: un aviso que rompe la sesión se desactiva.
"""
import json
import os
import pathlib
import re
import sys
import tempfile

UMBRAL = int(os.environ.get("BRAIN_UMBRAL", "15"))
VAULT = pathlib.Path(__file__).resolve().parent


def session_id():
    """El JSON de la sesión llega por stdin, pero puede no llegar nunca (una
    prueba a mano, otro agente). En Unix se espera un segundo; en Windows
    select() no sirve sobre stdin, así que solo se lee si no es una consola."""
    try:
        if sys.stdin is None or sys.stdin.closed:
            return "-"
        if os.name == "nt":
            if sys.stdin.isatty():
                return "-"
        else:
            import select

            if not select.select([sys.stdin], [], [], 1.0)[0]:
                return "-"
        return str(json.load(sys.stdin).get("session_id", "-"))
    except Exception:
        return "-"


def main():
    fechas = [p.stat().st_mtime for p in VAULT.rglob("*.md") if ".git" not in p.parts]
    if not fechas:
        return
    huella = f"{max(fechas):.0f}"

    sid = re.sub(r"[^A-Za-z0-9_-]", "", session_id())
    estado = pathlib.Path(tempfile.gettempdir()) / f"brain-aviso-{sid}"

    previo = estado.read_text().split() if estado.exists() else []
    n = int(previo[1]) + 1 if len(previo) == 2 and previo[0] == huella else 1
    estado.write_text(f"{huella} {n}")

    if n >= UMBRAL:
        estado.write_text(f"{huella} 0")  # avisado: no repetir hasta otros UMBRAL mensajes
        print(
            f"El cerebro ({VAULT}) no cambia desde hace {UMBRAL} mensajes. Si en este tramo "
            "apareció algo que no se deduce del código ni del historial —una decisión y su "
            "porqué, un camino descartado, una restricción de un proveedor, un riesgo sin "
            "dueño, una técnica que costó— escríbelo ahora como nota, dale su contexto, "
            "agrégalo al índice de ese contexto y corre el check. Si no apareció nada, sigue "
            "sin comentarlo."
        )


try:
    main()
except Exception:
    pass  # un hook que rompe la sesión se desactiva; mejor callarse
