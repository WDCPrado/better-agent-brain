#!/usr/bin/env bash
# Verifica que el brain no se pudra. Sin dependencias: solo python3.
exec python3 "$(dirname "$0")/check.py"
