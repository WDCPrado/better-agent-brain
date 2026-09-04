---
name: init-brain
description: Crea o reorganiza el cerebro de memoria de la persona — un vault de Obsidian donde el agente escribe lo que no se deduce del código ni del historial. Entrevista a la persona, lee sus repos, arma los contextos y deja el sistema andando (índice, check, hook y la regla en el archivo del agente). Sirve para Claude Code y para Codex. Úsala cuando pidan /init-brain, "arma mi memoria", "configurar el cerebro", "instalar better-agent-brain", o cuando el índice exista pero esté desordenado y haya que reorganizarlo sin perder información.
---

# init-brain

Deja funcionando un cerebro: un vault de Obsidian donde el agente escribe, entre sesiones,
**lo que no se deduce leyendo el código ni el historial de git**. No es documentación del repo;
es lo que quedaría en la cabeza de un colega que lleva años en el proyecto.

El resultado es un vault que se lee solo desde su índice, un `check.sh` que avisa cuando se
pudre, un hook que recuerda escribirlo y una regla en el archivo del agente para que todas las
sesiones lo usen.

## Los dos agentes

Este sistema no es de una herramienta en particular. Instala en la que exista:

| | Claude Code | Codex |
|---|---|---|
| Reglas globales | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` |
| Skills | `~/.claude/skills/` | `~/.codex/skills/` |
| Hooks | `settings.json` | `hooks.json` |

Si están los dos, configura los dos y **apunta ambos al mismo vault**. Dos cerebros para una
persona es el peor resultado posible: cada sesión escribiría en la mitad que el otro no lee.

---

## Paso 0 — Encontrar el vault (haz esto antes que nada)

**Nunca escribas dentro del repo donde vive esta skill.** Ese repo es solo el instalador: se
clona, se instala y se puede borrar. El vault es otra cosa, en otra ruta.

Cómo distinguirlos, sin ambigüedad:

| | Repo de setup | Vault (el cerebro) |
|---|---|---|
| Tiene | `skills/`, `plantillas/` | `MEMORY.md` y `contextos/` |
| Rol | se instala una vez | se escribe para siempre |

**Un directorio es un vault si y solo si contiene `MEMORY.md`.** Es el marcador; no uses el
nombre de la carpeta para decidir.

Para encontrar el vault de esta máquina, en este orden y parando en el primero que dé:

1. **El archivo de reglas del agente** (`~/.claude/CLAUDE.md` o `~/.codex/AGENTS.md`) ya trae la
   ruta, porque este mismo comando la escribió la primera vez:
   ```bash
   grep -hoE '[~/][^ `]*/MEMORY\.md' ~/.claude/CLAUDE.md ~/.codex/AGENTS.md 2>/dev/null | sort -u
   ```
   Extrae **rutas**, no menciones: esos archivos hablan de `MEMORY.md` en varias líneas y solo
   una es el puntero. Si sale una sola ruta, ese es el vault. Si salen dos distintas, para y
   pregunta: la memoria está partida en dos y hay que decidir cuál queda.

   **Ese puntero es el único que hay:** no inventes un archivo de configuración aparte, porque
   un segundo puntero es un segundo lugar donde equivocarse.
2. Si no está, pregunta dónde va el vault y propón `~/brain`.

Si la persona ya tenía un cerebro y el puntero no existe, pídele la ruta antes de crear nada:
**crear un vault nuevo cuando ya había uno es el peor error posible** de este comando, porque
parte la memoria en dos y ninguna de las dos mitades vuelve a estar completa.

---

## Paso 1 — Reconocer el estado

Mira el vault y decide en cuál de los tres casos estás. El caso decide todo lo que sigue:

| Estado | Cómo se ve | Qué haces |
|---|---|---|
| **Nuevo** | la ruta no existe, o existe vacía | entrevista completa y creas todo |
| **Vacío** | hay `MEMORY.md` pero casi ninguna nota | entrevista completa, respetas lo que haya |
| **Con información** | hay notas y contextos reales | **modo reorganizar**, ver paso 5 |

---

## Paso 2 — La entrevista

Es una conversación, no un formulario. Pregunta por bloques, con las preguntas de un bloque
juntas, y **deja siempre saltar un bloque**: un cerebro a medias que crece después es mejor que
un interrogatorio que la persona abandona.

Antes de preguntar, averigua lo que puedas solo, y **preséntalo para confirmar en vez de
preguntarlo**. El sistema operativo, la distro, el shell, el gestor de paquetes y los repos que
haya en las carpetas de trabajo salen de mirar la máquina. Preguntar lo que se puede leer gasta
la paciencia que necesitas para lo que no.

### Bloque 1 — La persona

Es la dueña del cerebro. De acá cuelga todo lo suyo.

- Cómo se llama y cómo quiere que la llamen las notas.
- **Qué construye por su cuenta.** Por cada proyecto: si hay repo git, pide la URL o la ruta y
  léelo; si no lo hay, pide una descripción en dos frases. Un proyecto es cualquier cosa con
  partes de las que se acumulen hechos, tenga o no repo, tarjeta o clientes.
- Cómo le gusta que se trabaje: idioma de las notas, qué le carga que el agente haga, qué espera
  antes de que toque código. Esto es oro y casi nadie lo escribe: va a `forma-de-trabajo/`.

### Bloque 2 — Las organizaciones donde trabaja

Una por empleador o cliente. Por cada una:

- A qué se dedica y qué hace ella ahí. Sin el negocio, las decisiones técnicas no se entienden.
- Sus proyectos y repos: URL o ruta para leerlos.
- **Sus reglas propias**, que le ganan a las preferencias personales del bloque 1: cómo se
  nombran las ramas, quién aprueba, qué no se toca nunca, dónde viven los issues.

### Bloque 3 — Los terceros de los que depende

Lo que no construyó pero usa todos los días y le da problemas: el sistema operativo, el editor,
un proveedor cloud, un servicio de pagos.

- El sistema operativo lo detectas tú; confírmalo y pregunta **por qué lo usa y qué le ha
  costado**. Eso último es lo único que vale escribir: lo que dice la documentación oficial no
  va al cerebro.
- Si tiene más de un sistema —doble booteo, un Windows para una cosa puntual, un servidor—
  anótalo, porque explica decisiones que si no parecen arbitrarias.

---

## Paso 3 — Leer antes de escribir

Por cada repo que te hayan dado, léelo lo justo para poder escribir su contexto: README,
`package.json` o equivalente, la forma de las carpetas, el archivo de reglas si tiene. **No lo
resumas.** El contexto de un repo responde "¿qué es esto y cómo funciona?" con lo que *no* está
escrito ahí: qué rompe si lo tocas, qué pareció buena idea y no lo era, qué depende de qué.

Si un repo no aporta ningún hecho de ese tipo todavía, escribe su contexto en cuatro líneas y
sigue. Va a crecer solo.

---

## Paso 4 — Escribir el vault

### La forma

```
MEMORY.md              el índice; es lo único que se carga en cada sesión
contextos/             ¿qué es esto y cómo funciona?   se edita
decisiones/            ¿por qué está así?              inmutable
tecnicas/              ¿cómo se hace esto?             se edita
forma-de-trabajo/      ¿cómo trabaja esta persona?     se edita
```

**Solo `contextos/` se anida**, porque un repo pertenece a una organización y a nada más:

```
contextos/<organizacion>/<organizacion>.md
contextos/<organizacion>/<repo>/<repo>.md
contextos/<organizacion>/<repo>/<repo>-<subsistema>.md
```

Las otras tres son planas a propósito: una decisión pertenece a la organización **y** al repo a
la vez, y anidarla obligaría a elegir un dueño único. La carpeta dice *qué tipo* de nota es; el
frontmatter `contexto` dice *de quién* es.

Cada nota vive en la carpeta que lleva su nombre y **es el índice de sus hijos**. No crees un
`index.md` aparte: se desincroniza del contenido.

### El frontmatter

```yaml
---
name: cache-redis
description: una línea; es la que va al índice y la que decide si alguien la abre
contexto:
  - "[[la-organizacion]]"
  - "[[el-repo]]"
fecha: 2026-09-03
tags: [cache]
---
```

`contexto` es lo que hace útil el vault: una nota puede pertenecer a la organización y al repo a
la vez, así que los backlinks de la organización muestran sus repos y toda decisión que los
toque. Los contextos de un repo llevan además `repo: <ruta o URL>`.

El nombre del archivo es el slug y nada más, sin prefijo de fecha: es lo que resuelve el
`[[wikilink]]`. **Todo nombre es único en el vault**, porque Obsidian resuelve los enlaces por
nombre y no por ruta; por eso los contextos internos llevan el prefijo de su padre.

### El índice

`MEMORY.md` lista **solo** los contextos raíz y lo transversal, en cuatro secciones:

```markdown
## La persona
## Organizaciones donde trabaja
## Terceros que usa
## Transversal
```

Todo lo demás se alcanza bajando por los enlaces de cada contexto. Así el índice no crece cuando
crece el cerebro, que es la única razón por la que se puede cargar entero en cada sesión.

### Las reglas al escribir

- **Una nota = un hecho.** Si el título necesita una "y", son dos notas.
- **Nunca dupliques** lo que ya dicen el README, el archivo de reglas del repo o el diff. Si se
  deduce leyendo el código, no va.
- **Ninguna nota nace huérfana.** En el mismo turno que la escribes: dale su `contexto` y
  agrégale su línea en el índice de ese contexto.
- Enlaza con `[[wikilinks]]` **por pertenencia, nunca por comparación**. Un enlace es una arista
  del grafo: "a diferencia de X" dibuja una relación que no existe. En ese caso escribe el
  nombre sin corchetes.
- Un enlace a una nota que todavía no existe está bien: marca algo que falta escribir, y
  `check.sh` lo lista como pendiente, no como error.
- **Lo que ordena es la fecha, no un campo de estado.** En el índice de cada contexto las
  decisiones van de la más reciente a la más antigua, con la fecha a la vista, y la de arriba
  manda. Cuando una nota reemplaza a otra lleva `deriva-de: "[[la-vieja]]"` y la vieja gana una
  línea arriba diciendo qué cambió y cuándo.
- Convierte las fechas relativas a absolutas: "el mes pasado" no significa nada en dos años.

---

## Paso 5 — Modo reorganizar (cuando ya había información)

Este es el caso delicado. La regla que manda:

> **Reorganizar mueve información; no la crea, no la corrige y no la borra.**

Qué sí haces: mover notas a la carpeta o al contexto que les corresponde, crear los contextos
padre que falten, rehacer `MEMORY.md` con las cuatro secciones, arreglar frontmatter incompleto,
agregar al índice las notas huérfanas.

Qué **no** haces sin preguntar: reescribir el cuerpo de una nota, fusionar dos notas, borrar
una, o cambiar un hecho porque no cuadra con lo que te dijeron recién en la entrevista.

**Cuando lo que dice una nota contradiga lo que respondió la persona, para y pregunta.** Muestra
las dos versiones y deja que elija. La nota puede estar vieja, pero también puede guardar un
matiz que la respuesta rápida de hoy se comió. No adivines cuál de las dos gana.

Al renombrar un contexto, arrastra todo con él: el archivo, su carpeta, el `name:` del
frontmatter y **todos los `[[wikilinks]]` del vault que lo apuntan**. Después corre `check.sh`:
si el conteo de alcanzables bajó, rompiste un enlace.

---

## Paso 6 — Dejar el sistema andando

Un vault que nadie lee ni escribe no es memoria. Instala las tres piezas, en cada agente que
exista en la máquina:

1. **Las carpetas y el `check.sh`.** Copia `check.py` y `check.sh` de `plantillas/` a la raíz
   del vault. Verifica tres cosas: que toda nota sea alcanzable desde `MEMORY.md` siguiendo
   enlaces, que ningún nombre esté repetido, y qué enlaces quedan pendientes de escribir.

2. **El hook.** Copia `aviso.sh` al vault y regístralo como hook `UserPromptSubmit` —en
   `settings.json` para Claude Code, en `hooks.json` para Codex—. Avisa cuando pasan muchos
   mensajes sin que el vault cambie. **Va en la configuración de la máquina, no en un repo de
   configuración versionado**, porque lleva una ruta local.

3. **La regla en el archivo del agente.** Sin esto, ninguna sesión sabe que el cerebro existe.
   Usa `plantillas/reglas.md` y escríbela en `~/.claude/CLAUDE.md`, en `~/.codex/AGENTS.md`, o
   en los dos, con la ruta real del vault.

   **Antes de escribirla, comprueba si ese archivo lo genera otro repo** (un "espejo" de
   configuración): si es copia de un archivo versionado en otro lado, editar el destino se
   pierde en la próxima sincronización. Búscalo así:

   ```bash
   grep -rl "$(head -c 200 ~/.claude/CLAUDE.md | tail -c 100)" ~ --include='*.md' 2>/dev/null
   ```

   Si aparece un espejo, **escribe primero en el repo espejo y desde ahí copia** — y anota ese
   hecho como nota del vault, porque ninguna sesión futura puede adivinarlo.

### Sobre git

**El vault no tiene por qué ser un repo, y este comando no lo convierte en uno.** Versionarlo,
publicarlo o dejarlo solo en disco es decisión de quien lo escribe, no de este sistema: el hook
y el `check.sh` funcionan igual en los tres casos.

Al terminar, menciónalo **una vez**, como opción: un vault en git deja ver cómo evolucionó lo
que se sabía, y sobrevive a que se muera el disco. Si la persona dice que sí, `git init` y ya;
la disciplina de commitear y publicar es suya y se anota en `forma-de-trabajo/`, no acá.

---

## Al cerrar

Corre `check.sh` y muestra el resultado.

Termina diciendo, en pocas líneas: cuántas notas quedaron, qué contextos se crearon, qué quedó
pendiente de escribir, y **una cosa concreta que la persona pueda hacer ahora** para probar que
funciona — por ejemplo, abrir el vault en Obsidian, o pedirle al agente algo que use un hecho
que acaba de quedar escrito.
