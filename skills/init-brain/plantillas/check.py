#!/usr/bin/env python3
"""Invariantes del cerebro. Sale con 1 si alguna se rompió; lo demás es aviso.

Rompen (exit 1):
1. Toda nota es alcanzable desde MEMORY.md siguiendo wikilinks. El índice global se
   mantiene corto porque cada contexto indexa a sus hijos; lo que no cuelga de ese
   árbol es una nota que nadie va a volver a leer.
2. Ningún nombre de nota se repite: Obsidian resuelve [[wikilinks]] por nombre, así
   que dos `auth.md` en carpetas distintas hacen ambiguo el enlace.
3. El frontmatter es coherente: `name` es el nombre del archivo, `fecha` es una fecha
   y cada `contexto` apunta a una nota que existe.
4. Pertenencia: cada contexto que una nota declara la enlaza; una nota sin contexto la
   enlaza MEMORY.md. Declarar un dueño que no te indexa es una huérfana disfrazada.
5. `deriva-de` es recíproco: la nota vieja enlaza a la que la reemplaza, o quien lea
   la vieja nunca sabrá que hay una nueva.

Avisan:
6. Los enlaces a notas que no existen se listan como pendientes: marcan algo que
   falta escribir.
7. Una nota de más de LARGO líneas fuera de `contextos/` huele a bitácora: la decisión
   se queda con el porqué, los hechos van a su contexto y lo reusable a `tecnicas/`.
   Un contexto acumula hechos por diseño, así que su límite es LARGO_CONTEXTO; pasado
   ese, lo que nace es un subcontexto.
8. Una técnica o forma de trabajo de más de EDAD_DIAS días que ninguna nota enlaza salvo
   su propio índice es candidata a borrar. Se lista; borrarla es de quien escribe, porque
   el check no sabe si sigue siendo cierta. `BRAIN_EDAD_DIAS` cambia el umbral.

Esto es lo que el código garantiza. Que una nota diga la verdad, o siga vigente, no
lo comprueba nadie más que quien la escribe.
"""
import os, re, sys
from datetime import date, timedelta
from pathlib import Path
from collections import deque

LARGO = 80
LARGO_CONTEXTO = 120
EDAD_DIAS = int(os.environ.get("BRAIN_EDAD_DIAS", 365))
VIEJAS_EN = ("tecnicas", "forma-de-trabajo")
raiz = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
indice = raiz / "MEMORY.md"

# Los ejemplos van entre backticks —`[[wikilinks]]`, bloques de código— y no son
# enlaces: contarlos llena el cierre de "pendientes" que nadie va a escribir nunca.
sin_codigo = lambda t: re.sub(r"`{1,3}[^`]*`{1,3}", "", t, flags=re.S)
nombre_de = lambda m: m.split("|")[0].split("#")[0].strip().rsplit("/", 1)[-1]
enlaces_en = lambda t: {nombre_de(m) for m in re.findall(r"\[\[([^\]]+)\]\]", sin_codigo(t))}


def frontmatter(texto):
    """Solo lo que el check necesita; sin YAML de verdad para no depender de nada."""
    m = re.match(r"---\n(.*?)\n---\n?(.*)", texto, re.S)
    if not m:
        return None, texto
    cab, cuerpo = m.group(1), m.group(2)
    campo = lambda k: (re.search(rf"^{k}:\s*(.*)$", cab, re.M) or [None, None])[1]
    bloque = re.search(r"^contexto:\s*(\[.*?\]|\n(?:\s+-.*\n?)*)", cab, re.M)
    return {
        "name": (campo("name") or "").strip(),
        "fecha": (campo("fecha") or "").strip(),
        "contexto": enlaces_en(bloque.group(1)) if bloque else set(),
        "deriva-de": enlaces_en(campo("deriva-de") or ""),
    }, cuerpo


notas, textos = {}, {}
for f in raiz.rglob("*.md"):
    rel = f.relative_to(raiz)   # se filtra la ruta relativa: un vault en ~/.brain no es oculto
    if any(p.startswith(".") for p in rel.parts) or f == indice:
        continue
    notas.setdefault(f.stem, []).append(rel)
    textos[f.stem] = f.read_text()

fallo = False
def error(msg):
    global fallo
    print(msg); fallo = True

indice_enlaces = enlaces_en(indice.read_text()) if indice.exists() else set()
if not notas and indice_enlaces:
    error(f"el índice enlaza {len(indice_enlaces)} notas pero no se encontró ninguna: "
          "¿el vault está en otra carpeta, o sus notas quedaron excluidas?")

# 2. nombres duplicados
for nombre, rutas in sorted(notas.items()):
    if len(rutas) > 1:
        error(f"nombre ambiguo '{nombre}': {', '.join(map(str, rutas))}")

# 3, 4, 5, 7: frontmatter, pertenencia, deriva-de, tamaño
for nombre in sorted(notas):
    ruta, texto = notas[nombre][0], textos[nombre]
    fm, cuerpo = frontmatter(texto)
    if fm is None:
        error(f"{ruta}: sin frontmatter"); continue
    if fm["name"] != nombre:
        error(f"{ruta}: name '{fm['name']}' no es el nombre del archivo")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fm["fecha"]):
        error(f"{ruta}: fecha '{fm['fecha']}' no es AAAA-MM-DD")
    if not fm["contexto"] and nombre not in indice_enlaces:
        error(f"{ruta}: sin contexto y MEMORY.md no la enlaza; o es de alguien, o es transversal")
    for ctx in sorted(fm["contexto"]):
        if ctx not in notas:
            error(f"{ruta}: contexto [[{ctx}]] no existe")
        elif nombre not in enlaces_en(textos[ctx]):
            error(f"{ruta}: declara contexto [[{ctx}]] pero {notas[ctx][0]} no la indexa")
    for vieja in sorted(fm["deriva-de"]):
        if vieja in notas and nombre not in enlaces_en(textos[vieja]):
            error(f"{ruta}: deriva de [[{vieja}]] pero la vieja no enlaza a la nueva")
    largo = LARGO_CONTEXTO if ruta.parts[0] == "contextos" else LARGO
    if cuerpo.count("\n") > largo:
        print(f"aviso: {ruta} pasa de {largo} líneas; huele a bitácora, considera dividirla")

# 1. alcanzabilidad desde el índice
vistos, cola, rotos = set(), deque(indice_enlaces), set()
while cola:
    nombre = cola.popleft()
    if nombre in vistos:
        continue
    vistos.add(nombre)
    if nombre in notas:
        cola.extend(enlaces_en(textos[nombre]))
    else:
        rotos.add(nombre)

for nombre in sorted(set(notas) - vistos):
    error(f"nota huérfana (no se llega desde MEMORY.md): {notas[nombre][0]}")

# 6. pendientes, informativos
for nombre in sorted(rotos):
    print(f"pendiente por escribir: [[{nombre}]]")

# 8. viejas que nadie enlaza salvo su índice
limite = (date.today() - timedelta(days=EDAD_DIAS)).isoformat()
for nombre in sorted(notas):
    ruta, (fm, _) = notas[nombre][0], frontmatter(textos[nombre])
    if ruta.parts[0] not in VIEJAS_EN or not fm or not fm["fecha"] or fm["fecha"] > limite:
        continue
    quien = {n for n in notas if n != nombre and nombre in enlaces_en(textos[n])} - fm["contexto"]
    if not quien:
        print(f"aviso: {ruta} tiene más de {EDAD_DIAS} días y solo la enlaza su índice; candidata a borrar")

print(f"{len(notas)} notas, {len(vistos & set(notas))} alcanzables")
sys.exit(1 if fallo else 0)
