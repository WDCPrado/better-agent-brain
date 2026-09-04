#!/usr/bin/env bash
# Hook UserPromptSubmit: avisa cuando la sesión avanzó y el brain sigue igual,
# y cuando lo que se escribió no salió de esta máquina.
#
# Son dos olvidos distintos. El primero se mide en mensajes desde el último
# commit del vault: un commit reinicia la cuenta sola, porque el estado guarda
# el hash y no un contador que haya que limpiar a mano. El segundo se mira
# directo contra origin y avisa una vez por commit nuevo sin publicar —una nota
# que solo existe aquí no es memoria—, no en cada mensaje, o se vuelve ruido.
# Nunca bloquea ni falla ruidosamente: un aviso que rompe la sesión se desactiva.
set -uo pipefail
BRAIN="$(cd "$(dirname "$0")" && pwd)"
UMBRAL=${BRAIN_UMBRAL:-15}

sid=$(timeout 1 cat 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get("session_id","-"))' 2>/dev/null) || sid="-"
estado="${TMPDIR:-/tmp}/brain-aviso-${sid//[^A-Za-z0-9_-]/}"
commit=$(git -C "$BRAIN" log -1 --format=%H 2>/dev/null) || exit 0

leido=$(cat "$estado" 2>/dev/null) || leido=""
if [ "${leido%% *}" = "$commit" ]; then
  n=$(( ${leido##* } + 1 ))
else
  n=1                      # commit nuevo: el brain se escribió, la cuenta parte de cero
fi
printf '%s %s' "$commit" "$n" > "$estado"

avisos=()

# Escrito pero no publicado. Se avisa una vez por commit, no en cada mensaje.
sin_push=$(git -C "$BRAIN" rev-list --count @{u}..HEAD 2>/dev/null) || sin_push=0
if [ "${sin_push:-0}" -gt 0 ] && [ "$(cat "$estado-push" 2>/dev/null)" != "$commit" ]; then
  printf '%s' "$commit" > "$estado-push"
  avisos+=("El brain tiene $sin_push commit(s) sin publicar. Corre 'git -C $BRAIN push origin main' ahora y confirma que quedó limpio: una nota que solo existe en esta máquina no es memoria.")
fi

if [ "$n" -ge "$UMBRAL" ]; then
  printf '%s 0' "$commit" > "$estado"   # avisado: no repetir hasta otros UMBRAL mensajes
  avisos+=("El brain (~/Projects/harness/claude/claude-brain) no cambia desde hace $UMBRAL mensajes. Si en este tramo apareció algo que no se deduce del código ni del historial de git —una decisión y su porqué, un camino descartado, una restricción de un proveedor, un riesgo sin dueño, una técnica que costó— escríbelo ahora como nota, actualiza el índice del contexto al que pertenece, corre ./check.sh, commitea y pushea. Si no apareció nada, sigue sin comentarlo.")
fi

[ ${#avisos[@]} -eq 0 ] && exit 0

printf '%s\n' "${avisos[@]}" | python3 -c '
import json, sys
print(json.dumps({"hookSpecificOutput": {
  "hookEventName": "UserPromptSubmit",
  "additionalContext": " ".join(l.strip() for l in sys.stdin if l.strip())
}}))'
