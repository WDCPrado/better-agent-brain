<!--
  Bloque para el archivo de reglas del agente: ~/.claude/CLAUDE.md en Claude Code,
  ~/.codex/AGENTS.md en Codex. Si están los dos, va en ambos y apuntando al MISMO
  vault. Reemplaza RUTA_DEL_VAULT por la ruta real: esa línea es el puntero oficial
  al vault y lo que permite volver a encontrarlo en la próxima sesión.
  Si ese archivo lo genera un repo espejo, escribe allá y copia desde ahí.
-->

## Base de conocimiento (brain)

Vive en `RUTA_DEL_VAULT`, un vault de Obsidian. Es la memoria entre sesiones: lo que no se
deduce leyendo el código ni el historial. **Lee su índice antes de trabajar:**

@RUTA_DEL_VAULT/MEMORY.md

(Claude Code expande esa línea y el índice ya está en tu contexto. Codex **no** la expande:
la ve como texto. Si en tu agente el índice no aparece arriba, un hook `SessionStart` puede
inyectarlo —`indice.py`— y si tampoco lo hay, **ábrelo con una lectura de archivo antes de
responder**: no es opcional.)

Es el único almacén: no crees notas de contexto dentro de los repos ni uses el directorio de
memoria por proyecto de Claude Code.

**Antes de trabajar**, si el índice muestra algo relacionado, léelo y sigue sus enlaces. Si no,
busca igual: `rg -il '<repo-o-tema>' RUTA_DEL_VAULT` (o `grep -ril` si no tienes ripgrep). Para todo lo de un contexto, busca su
wikilink: `rg -l '\[\[nombre-del-contexto\]\]'`.

**Al terminar**, escribe lo que no se deduce del código ni del historial de git. Una nota = un
hecho. Nunca dupliques lo que ya dice el README, el archivo de reglas del repo o el diff.

### Las cuatro carpetas

| Carpeta | Responde | Vida |
|---|---|---|
| `contextos/` | ¿qué es esto y cómo funciona? Una nota por persona, organización, repo, subsistema o herramienta de la que acumulas hechos | se edita |
| `decisiones/` | ¿por qué está así? Incluye la investigación que la sustenta | inmutable |
| `tecnicas/` | ¿cómo se hace esto? Reusable; su `contexto` dice dónde se aprendió | se edita |
| `forma-de-trabajo/` | ¿cómo trabaja esta persona y por qué? | se edita |

**Solo `contextos/` se anida**, porque un repo pertenece a una organización y a nada más. Las
otras tres quedan planas: una decisión pertenece a la organización **y** al repo a la vez, y
anidarla obligaría a elegir un dueño único. La carpeta dice *qué tipo* de nota es; el frontmatter
`contexto` dice *de quién* es.

Cada nota vive en la carpeta que lleva su nombre y **es el índice de sus hijos**. No crees un
`index.md` aparte: se desincroniza del contenido.

**Un contexto no es solo una organización o un repo.** Es cualquier cosa de la que acumules
hechos y que responda "¿qué es esto y cómo funciona?": el escritorio de la máquina, una
herramienta, un servicio de terceros. La señal es contar — **a la tercera nota del mismo tema
nace su contexto** y esas notas se mudan a él. Antes de eso viven en `Transversal`, que es la
sala de espera y no el destino.

**Ninguna nota nace huérfana.** En el mismo turno en que la escribes: dale su `contexto` en el
frontmatter y agrégale su línea en el índice de ese contexto. Del índice global solo cuelgan los
contextos raíz y lo transversal.

**Agregar es también corregir.** Al sumar un hecho a un contexto, relee la nota entera y borra o
corrige lo que ese hecho deja falso: dos párrafos que se contradicen en la misma nota son peor
que ninguno.

**Una nota que crece como bitácora se divide.** Si la editas por tercera vez en el día o pasa de
80 líneas, ya no es un hecho: la decisión se queda con el porqué, los hechos van a su contexto y
lo reusable a `tecnicas/`.

### El índice

`MEMORY.md` es el mapa: la persona, sus organizaciones, los terceros de los que depende y lo
transversal. Nada más, para que no crezca cuando crece el brain.

Todo nombre de archivo es único en el vault, porque Obsidian resuelve `[[wikilinks]]` por nombre
y no por ruta. Los contextos internos llevan el prefijo de su padre.

Enlaza **por pertenencia, nunca por comparación**: un enlace es una arista del grafo, así que
"a diferencia de X" dibuja una relación que no existe — ahí el nombre va sin corchetes. Un
enlace a una nota que no existe está bien: marca algo que falta escribir, y `check.sh` lo lista
como pendiente en vez de como error.

### Frontmatter

```yaml
---
name: cache-redis
description: una línea; es la que va al índice
contexto:
  - "[[la-organizacion]]"
  - "[[el-repo]]"
fecha: 2026-01-15
tags: [cache]
---
```

**Lo que ordena es la fecha, no un campo de estado.** En el índice de cada contexto las
decisiones van de la más reciente a la más antigua, con la fecha a la vista, y la de arriba
manda. Cuando una nota reemplaza a otra lleva `deriva-de: "[[la-vieja]]"`, y la vieja gana una
línea arriba diciendo qué cambió y en qué fecha. **Manda solo dentro del índice de un mismo
contexto**: una nota reciente de otro contexto no reemplaza nada, y una hipótesis no entra al
vault —se escribe cuando es decisión.

### Al cerrar

Corre `./check.sh`. Rompe si una nota no cuelga de `MEMORY.md`, si un nombre se repite, si el
frontmatter no cuadra, si un contexto declarado no la indexa o si un `deriva-de` no tiene vuelta;
avisa los enlaces pendientes de escribir y las notas demasiado largas fuera de `contextos/`. Con
el vault en git, el
hook `pre-commit` lo corre solo y nada que lo rompa entra al historial.

Qué se hace después con el vault —versionarlo, publicarlo, dejarlo en disco— lo decide quien lo
escribe. Si hay una regla al respecto, va en `forma-de-trabajo/` y manda por sobre esto.
