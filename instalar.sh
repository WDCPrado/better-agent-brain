#!/usr/bin/env bash
# Deja /init-claude-brain disponible en Claude Code. No toca ningún vault:
# el cerebro se crea después, corriendo el comando.
#
# Por defecto copia, para que este repo se pueda borrar después de instalar.
# Con --link deja un symlink, que es lo que quieres si vas a editar la skill.
set -euo pipefail
REPO="$(cd "$(dirname "$0")" && pwd)"
DESTINO="${CLAUDE_HOME:-$HOME/.claude}/skills/init-claude-brain"

mkdir -p "$(dirname "$DESTINO")"
rm -rf "$DESTINO"   # no falla si no existe

if [ "${1:-}" = "--link" ]; then
  ln -s "$REPO/skills/init-claude-brain" "$DESTINO"
  echo "Enlazado (modo desarrollo): $DESTINO"
else
  cp -r "$REPO/skills/init-claude-brain" "$DESTINO"
  cp -r "$REPO/plantillas" "$DESTINO/plantillas"
  echo "Instalado: $DESTINO"
  echo "Este repo ya no hace falta; puedes borrarlo."
fi

echo "Abre Claude Code y corre /init-claude-brain"
