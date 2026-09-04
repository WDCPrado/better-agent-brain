<!--
  Bloque para un agente LECTOR: lee el cerebro, no lo escribe.
  Va en el archivo de reglas del agente (~/.claude/CLAUDE.md en Claude Code,
  ~/.codex/AGENTS.md en Codex). Reemplaza RUTA_DEL_VAULT por la ruta real:
  esa línea es el puntero al vault y lo que permite volver a encontrarlo.
  Si ese archivo lo genera un repo espejo, escribe allá y copia desde ahí.

  Es a propósito mucho más corto que reglas.md: un lector no necesita saber
  cómo se escribe una nota, sino dónde buscar lo que ya está escrito.
-->

## Base de conocimiento (brain) — solo lectura

Vive en `RUTA_DEL_VAULT`, un vault de Obsidian. Es la memoria entre sesiones: lo que no se deduce
leyendo el código ni el historial. **Lee su índice antes de trabajar:**

@RUTA_DEL_VAULT/MEMORY.md

(Claude Code expande esa línea y el índice ya está en tu contexto. Codex **no** la expande: la ve
como texto. Si en tu agente el índice no aparece arriba, un hook `SessionStart` puede inyectarlo
—`indice.py`— y si tampoco lo hay, **ábrelo con una lectura de archivo antes de responder**: no
es opcional.)

El índice tiene cuatro secciones —la persona, las organizaciones donde trabaja, los terceros que
usa y lo transversal— y cada contexto indexa a sus hijos. Si algo del índice se relaciona con lo
que estás haciendo, ábrelo y sigue sus enlaces. Si no aparece nada, busca igual:

```
rg -il '<repo-o-tema>' RUTA_DEL_VAULT          # o grep -ril si no tienes ripgrep
rg -l '\[\[nombre-del-contexto\]\]'            # todo lo que pertenece a un contexto
```

**Este agente no escribe en el cerebro.** Otro agente es el que lo mantiene, así que no crees ni
edites notas, no toques `MEMORY.md` y no corras su `check`. Si en tu sesión aparece algo que
merecería quedar escrito —una decisión y su porqué, un camino descartado, una restricción de un
proveedor, una técnica que costó— **dilo al final, en una línea**, para que la persona lo lleve
al agente que sí escribe. No lo escribas tú.

Tampoco confíes en que una nota esté al día si el código la contradice: la memoria refleja lo que
era cierto cuando se escribió. Si ves una contradicción, dila.
