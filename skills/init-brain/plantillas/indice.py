#!/usr/bin/env python3
"""Hook SessionStart: inyecta el índice del cerebro al empezar la sesión.

Solo hace falta en agentes que NO expanden imports en su archivo de reglas.
Claude Code sí los expande —`@ruta/MEMORY.md` en `CLAUDE.md` basta—, así que
ahí este hook sobra. Codex no: la línea del import le queda como texto y el
índice nunca llega al contexto, salvo que el modelo decida abrir el archivo.
Este script cierra esa diferencia imprimiéndolo, porque lo que un hook
SessionStart escribe en stdout entra como contexto antes de la primera vuelta.

Va junto al MEMORY.md que inyecta: se ubica solo, sin rutas escritas a mano.

Nunca falla ruidosamente: si el índice no está, se calla. Un hook que rompe
la sesión termina desactivado, y sin índice el resto del sistema sigue
funcionando —el agente solo tiene que buscar en vez de tener el mapa servido.
"""
import pathlib

INDICE = pathlib.Path(__file__).resolve().parent / "MEMORY.md"

try:
    texto = INDICE.read_text().strip()
    if texto:
        # Neutral a propósito: si este agente escribe el cerebro o solo lo lee lo dicen
        # sus reglas. Ordenar "escribe al terminar" desde acá contradecía al lector.
        print(f"Índice del cerebro ({INDICE}). Es la memoria entre sesiones: baja por sus enlaces antes de trabajar.\n\n{texto}")
except Exception:
    pass
