#!/usr/bin/env bash
# Deja /init-brain disponible en los agentes que encuentre en esta máquina.
# No toca ningún vault: el cerebro se crea después, corriendo el comando.
#
# Por defecto copia, para que este repo se pueda borrar después de instalar.
# Con --link deja un symlink, que es lo que quieres si vas a editar la skill.
set -uo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
MODO="${1:-copiar}"

instalar_en() {
  local base="$1" nombre="$2"
  [ -d "$base" ] || return 1
  local destino="$base/skills/init-brain"
  mkdir -p "$base/skills"
  rm -rf "$destino"
  if [ "$MODO" = "--link" ]; then
    ln -s "$REPO/skills/init-brain" "$destino" || return 1
  else
    cp -r "$REPO/skills/init-brain" "$destino" || return 1
    cp -r "$REPO/plantillas" "$destino/plantillas" || return 1
  fi
  echo "  $nombre  ->  $destino"
  return 0
}

echo "Instalando /init-brain:"
encontrado=0
instalar_en "${CLAUDE_HOME:-$HOME/.claude}" "Claude Code" && encontrado=1
instalar_en "${CODEX_HOME:-$HOME/.codex}"   "Codex      " && encontrado=1

if [ "$encontrado" -eq 0 ]; then
  echo "  ningún agente encontrado (~/.claude ni ~/.codex)." >&2
  echo "  Instala Claude Code o Codex primero, o pasa CLAUDE_HOME=/ruta." >&2
  exit 1
fi

[ "$MODO" = "--link" ] || echo
[ "$MODO" = "--link" ] || echo "Este repo ya no hace falta; puedes borrarlo."
echo "Abre tu agente y corre /init-brain"
