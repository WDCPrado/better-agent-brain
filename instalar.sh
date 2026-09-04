#!/usr/bin/env bash
# Atajo para Unix. El instalador de verdad es instalar.py, que corre igual en
# Linux, macOS y Windows.
exec python3 "$(dirname "$0")/instalar.py" "$@"
