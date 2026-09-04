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
# Nunca bloquea ni falla ruidosamente: un aviso que rompe la sesión se desactiva.
set -uo pipefail
VAULT="$(cd "$(dirname "$0")" && pwd)"
UMBRAL=${BRAIN_UMBRAL:-15}

sid=$(timeout 1 cat 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("session_id","-"))' 2>/dev/null) || sid="-"
estado="${TMPDIR:-/tmp}/brain-aviso-${sid//[^A-Za-z0-9_-]/}"

huella=$(find "$VAULT" -name '*.md' -not -path '*/.git/*' -printf '%T@\n' 2>/dev/null | sort -rn | head -1) || exit 0
[ -n "$huella" ] || exit 0

leido=$(cat "$estado" 2>/dev/null) || leido=""
if [ "${leido%% *}" = "$huella" ]; then
  n=$(( ${leido##* } + 1 ))
else
  n=1                      # el vault cambió: se escribió algo, la cuenta parte de cero
fi
printf '%s %s' "$huella" "$n" > "$estado"

if [ "$n" -ge "$UMBRAL" ]; then
  printf '%s 0' "$huella" > "$estado"   # avisado: no repetir hasta otros UMBRAL mensajes
  echo "El cerebro ($VAULT) no cambia desde hace $UMBRAL mensajes. Si en este tramo apareció algo que no se deduce del código ni del historial —una decisión y su porqué, un camino descartado, una restricción de un proveedor, un riesgo sin dueño, una técnica que costó— escríbelo ahora como nota, dale su contexto, agrégalo al índice de ese contexto y corre ./check.sh. Si no apareció nada, sigue sin comentarlo."
fi
