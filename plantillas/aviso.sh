#!/usr/bin/env bash
# Hook UserPromptSubmit: avisa cuando la sesión avanzó y el cerebro sigue igual.
#
# Se mide en mensajes desde el último cambio del vault. La huella es la fecha del
# .md más reciente, así que escribir una nota reinicia la cuenta sola: no hay un
# contador que alguien tenga que limpiar a mano.
#
# No sabe nada de git a propósito. Publicar el vault —si es que se publica— es
# decisión de quien lo escribe, no de este sistema.
#
# Todo el trabajo lo hace python3, que ya hace falta para check.sh. Así el hook
# no depende de `find -printf` ni de `timeout`, que son de GNU y no existen en
# macOS. Nunca bloquea ni falla ruidosamente: un aviso que rompe la sesión se
# desactiva.
set -uo pipefail
VAULT="$(cd "$(dirname "$0")" && pwd)"

python3 - "$VAULT" "${BRAIN_UMBRAL:-15}" "${TMPDIR:-/tmp}" <<'PY' 2>/dev/null || exit 0
import json, os, pathlib, re, select, sys

vault, umbral, tmp = pathlib.Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]

# El hook recibe el JSON de la sesión por stdin, pero puede no llegar nunca
# (una prueba a mano, otro agente): se espera un segundo y se sigue igual.
sid = "-"
if sys.stdin and select.select([sys.stdin], [], [], 1.0)[0]:
    try:
        sid = str(json.load(sys.stdin).get("session_id", "-"))
    except Exception:
        pass

fechas = [p.stat().st_mtime for p in vault.rglob("*.md") if ".git" not in p.parts]
if not fechas:
    sys.exit(0)
huella = f"{max(fechas):.0f}"

estado = pathlib.Path(tmp) / f"brain-aviso-{re.sub(r'[^A-Za-z0-9_-]', '', sid)}"
previo = estado.read_text().split() if estado.exists() else []
n = int(previo[1]) + 1 if len(previo) == 2 and previo[0] == huella else 1
estado.write_text(f"{huella} {n}")

if n >= umbral:
    estado.write_text(f"{huella} 0")   # avisado: no repetir hasta otros `umbral` mensajes
    print(
        f"El cerebro ({vault}) no cambia desde hace {umbral} mensajes. Si en este tramo "
        "apareció algo que no se deduce del código ni del historial —una decisión y su porqué, "
        "un camino descartado, una restricción de un proveedor, un riesgo sin dueño, una técnica "
        "que costó— escríbelo ahora como nota, dale su contexto, agrégalo al índice de ese "
        "contexto y corre ./check.sh. Si no apareció nada, sigue sin comentarlo."
    )
PY
