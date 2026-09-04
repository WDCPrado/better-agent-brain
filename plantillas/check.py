#!/usr/bin/env python3
"""Tres invariantes del brain:

1. Toda nota es alcanzable desde MEMORY.md siguiendo wikilinks. El índice global se
   mantiene corto porque cada contexto indexa a sus hijos; lo que no cuelga de ese
   árbol es una nota que nadie va a volver a leer.
2. Ningún nombre de nota se repite: Obsidian resuelve [[wikilinks]] por nombre, así
   que dos `auth.md` en carpetas distintas hacen ambiguo el enlace.
3. Los enlaces a notas que no existen se listan como pendientes, no como error:
   marcan algo que falta escribir.
"""
import re, sys
from pathlib import Path
from collections import deque

raiz = Path(__file__).parent
notas = {}          # nombre -> [rutas]
for f in raiz.rglob("*.md"):
    if any(x.startswith(".") for x in f.parts) or f.name == "MEMORY.md":
        continue
    notas.setdefault(f.stem, []).append(f.relative_to(raiz))

fallo = False

# 2. nombres duplicados
for nombre, rutas in sorted(notas.items()):
    if len(rutas) > 1:
        print(f"nombre ambiguo '{nombre}': {', '.join(map(str, rutas))}")
        fallo = True

enlaces = lambda p: {m.split("|")[0].split("#")[0].strip().rsplit("/", 1)[-1]
                     for m in re.findall(r"\[\[([^\]]+)\]\]", p.read_text())}

# 1. alcanzabilidad desde el índice
vistos, cola, rotos = set(), deque(enlaces(raiz / "MEMORY.md")), set()
while cola:
    nombre = cola.popleft()
    if nombre in vistos:
        continue
    vistos.add(nombre)
    if nombre in notas:
        cola.extend(enlaces(raiz / notas[nombre][0]))
    else:
        rotos.add(nombre)

for nombre in sorted(set(notas) - vistos):
    print(f"nota huérfana (no se llega desde MEMORY.md): {notas[nombre][0]}")
    fallo = True

# 3. pendientes, informativos
for nombre in sorted(rotos):
    print(f"pendiente por escribir: [[{nombre}]]")

print(f"{len(notas)} notas, {len(vistos & set(notas))} alcanzables")
sys.exit(1 if fallo else 0)
