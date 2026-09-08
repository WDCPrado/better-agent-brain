---
name: init-brain
description: Crea o reorganiza el cerebro de memoria de la persona — un vault de Obsidian donde el agente escribe lo que no se deduce del código ni del historial. Entrevista a la persona, lee sus repos, arma los contextos y deja el sistema andando (índice, check, hook y la regla en el archivo del agente). Sirve para Claude Code y para Codex, y varios agentes pueden compartir un mismo cerebro: al configurar el segundo pregunta si va a escribirlo o solo leerlo. Úsala cuando pidan /init-brain (Claude Code) o $init-brain (Codex), "arma mi memoria", "configurar el cerebro", "instalar better-agent-brain", o cuando el índice exista pero esté desordenado y haya que reorganizarlo sin perder información.
---

# init-brain

Deja funcionando un cerebro: un vault de Obsidian donde el agente escribe, entre sesiones,
**lo que no se deduce leyendo el código ni el historial de git**. No es documentación del repo;
es lo que quedaría en la cabeza de un colega que lleva años en el proyecto.

El resultado es un vault que se lee solo desde su índice, un `check.sh` que avisa cuando se
pudre, un hook que recuerda escribirlo y una regla en el archivo del agente para que todas las
sesiones lo usen.

## Un agente por vez: el que te invocó

Este sistema no es de una herramienta en particular, pero **escribe únicamente en el agente desde
el que te están corriendo**. Nunca modifiques la configuración de otro, ni siquiera para preguntar
si conviene: quien corre el comando en una herramienta no está pidiendo nada sobre las demás.

**La restricción es de escritura, no de lectura.** En el paso 0 tienes que **leer los archivos de
todos los agentes** para encontrar el vault: leer no es tocar, y el puntero puede estar en
cualquiera de ellos. Saltarte esa lectura es lo que provoca el peor error de este comando —crear
un cerebro nuevo al lado de uno que ya existía.

| | Claude Code | Codex |
|---|---|---|
| Reglas globales | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` |
| Skills | `~/.claude/skills/` | `~/.codex/skills/` |
| Hooks | `settings.json` | `hooks.json` |

Se invoca distinto en cada uno: en Claude Code es `/init-brain`; en Codex las skills son
menciones, así que es `$init-brain` —o `/skills`, que abre un selector e inserta la mención—.
Cuando cierres, dile a la persona la forma que corresponde a **su** agente.

En Windows la carpeta del agente es `%USERPROFILE%\.claude` / `%USERPROFILE%\.codex`; el resto
es igual. **Nunca escribas rutas con `~` dentro de los archivos de configuración en Windows**:
resuélvelas completas, porque ahí `~` no se expande.

La razón es que el archivo de reglas de otro agente puede venir de un **repo espejo**: entonces
el cambio no es local, hay que commitearlo y publicarlo, y esos repos aparecen recién al
buscarlos —quien te invocó puede ni saber que existen—. Publicar en un repo ajeno a lo que te
pidieron es exactamente lo que este comando no debe hacer.

**Compartir el vault entre agentes es deseable** —dos cerebros para una persona es el peor
resultado, porque cada sesión escribiría en la mitad que la otra no lee—, pero se consigue de la
forma obvia: corriendo `/init-brain` desde el otro agente, que encontrará el vault existente por
el mismo paso 0 y se conectará solo. Al cerrar puedes mencionarlo en una línea, como sugerencia
y nada más.

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

1. **El archivo de reglas de cualquier agente** ya trae la ruta, porque este mismo comando la
   escribió la primera vez. **Míralos todos, no solo el tuyo**: si la persona instaló el cerebro
   desde Claude Code, el puntero está en `~/.claude/CLAUDE.md` aunque ahora te esté corriendo en
   Codex, y viceversa. Leerlos es obligatorio; escribir en ellos, no.
   Busca en **todos** esos archivos una ruta que termine en `MEMORY.md`. Léelos directamente si
   es más simple —funciona en cualquier sistema—; en Unix este atajo los cubre de una:
   ```bash
   grep -hoE '[~/][^ `]*/MEMORY\.md' ~/.claude/CLAUDE.md ~/.codex/AGENTS.md 2>/dev/null | sort -u
   ```
   Busca **rutas**, no menciones: esos archivos hablan de `MEMORY.md` en varias líneas y solo
   una es el puntero. Si sale una sola ruta, ese es el vault. Si salen dos distintas, para y
   pregunta: la memoria está partida en dos y hay que decidir cuál queda.

   **Ese puntero es el único que hay:** no inventes un archivo de configuración aparte, porque
   un segundo puntero es un segundo lugar donde equivocarse.
2. Si no está, pregunta dónde va el vault y propón `~/brain`.

Si la persona ya tenía un cerebro y el puntero no existe, pídele la ruta antes de crear nada:
**crear un vault nuevo cuando ya había uno es el peor error posible** de este comando, porque
parte la memoria en dos y ninguna de las dos mitades vuelve a estar completa.

---

## Paso 1 — El estado y el rol de este agente

Primero, mira el vault y decide en cuál de los tres casos estás:

| Estado | Cómo se ve | Qué haces |
|---|---|---|
| **Nuevo** | la ruta no existe, o existe vacía | entrevista completa y creas todo |
| **Vacío** | hay `MEMORY.md` pero casi ninguna nota | entrevista completa, respetas lo que haya |
| **Con información** | hay notas y contextos reales | **modo reorganizar**, ver paso 5 |

### El rol: escritor o lector

Un cerebro puede servir a varios agentes, y **no todos tienen por qué escribirlo**. Uno lo
mantiene y los demás lo aprovechan: así la memoria no se llena de versiones distintas del mismo
hecho, escritas por herramientas que no se leen entre sí.

**Si el vault estaba Nuevo o Vacío, este agente es escritor y no preguntes nada:** un cerebro que
nadie escribe no llega a existir. Sáltate el resto de esta sección.

**Si el vault tenía información, ya hay alguien manteniéndolo.** Antes de escribir una sola
línea —en el vault o en la configuración— pregunta:

> Ya tienes un cerebro con N notas. ¿Qué rol quieres que tenga **este** agente?
>
> - **Escritor** — lo lee y también lo mantiene: escribe notas nuevas al terminar.
> - **Lector** — lo lee para trabajar, pero no lo escribe; el otro agente sigue a cargo.

Y para saber cuál sugerir, mira quién escribe hoy: si otro archivo de reglas ya trae el bloque
completo, ese agente es el escritor y **lector es la opción razonable** para este.

El rol cambia lo que sigue:

| | Escritor | Lector |
|---|---|---|
| Entrevista (paso 2) y escritura (paso 4) | sí | **no, sáltalas** |
| Reorganizar (paso 5) | sí | **no** |
| Regla en el archivo del agente | `plantillas/reglas.md` | `plantillas/reglas-lectura.md` |
| `check.py` y el hook `aviso.py` | sí | **no**: nada que verificar ni que recordar escribir |
| Hook `indice.py` (`SessionStart`) | si el agente no expande imports | igual: leer el índice es lo suyo |

Un lector termina rapidísimo: paso 0, esta pregunta, la regla corta, y listo. **No toques el
vault**, ni siquiera para ordenarlo: no es el agente a cargo.

El rol no queda guardado en ninguna parte — se ve en el archivo de reglas de cada agente, según
qué bloque tenga. Cambiarlo es volver a correr `/init-brain` y elegir el otro.

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
  agrégale su línea en el índice de ese contexto. `check.py` lo verifica en los dos sentidos.
- **Agregar es también corregir.** Al sumar un hecho a un contexto, relee la nota entera y
  corrige lo que ese hecho deja falso.
- **Una nota que crece como bitácora se divide.** Pasadas las 80 líneas ya no es un hecho: la
  decisión se queda con el porqué, los hechos van a su contexto y lo reusable a `tecnicas/`.
- Enlaza con `[[wikilinks]]` **por pertenencia, nunca por comparación**. Un enlace es una arista
  del grafo: "a diferencia de X" dibuja una relación que no existe. En ese caso escribe el
  nombre sin corchetes.
- Un enlace a una nota que todavía no existe está bien: marca algo que falta escribir, y
  `check.sh` lo lista como pendiente, no como error.
- **Lo que ordena es la fecha, no un campo de estado.** En el índice de cada contexto las
  decisiones van de la más reciente a la más antigua, con la fecha a la vista, y la de arriba
  manda —solo dentro del índice de un mismo contexto; una hipótesis no entra al vault hasta que
  sea decisión—. Cuando una nota reemplaza a otra lleva `deriva-de: "[[la-vieja]]"` y la vieja
  gana una línea arriba diciendo qué cambió y cuándo.
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

Un vault que nadie lee ni escribe no es memoria. Instala las piezas **en el agente que te
invocó**, y solo en ese.

**Si este agente es lector**, no copies `check.py` ni instales `aviso.py`: no hay nada que
verificar ni que recordarle escribir. Sí instálale `indice.py` si su agente no expande imports
(punto 2), y usa `plantillas/reglas-lectura.md` en el punto 3. Con eso terminaste.

Si es escritor, las tres:

1. **Las carpetas y el check.** Copia `check.py` de `plantillas/` a la raíz del vault (y
   `check.sh`, que es solo un atajo para Unix). Se corre con `python3 check.py` en cualquier
   sistema. Rompe si una nota no cuelga de `MEMORY.md`, si un nombre se repite, si el
   frontmatter no cuadra, si un contexto declarado no indexa a la nota o si un `deriva-de` no
   tiene vuelta; avisa los enlaces pendientes y las notas de más de 80 líneas fuera de
   `contextos/`. Es lo que el código garantiza; que una nota sea verdad o siga vigente lo
   pone quien la escribe.

2. **Los hooks.** Copia `aviso.py` al vault —y `indice.py` si hace falta, ver abajo— y
   regístralos con la ruta completa y el intérprete del sistema:

   | | Comando |
   |---|---|
   | Linux / macOS | `python3 /ruta/al/vault/aviso.py` |
   | Windows | `python C:\ruta\al\vault\aviso.py` |

   Van en la configuración de la máquina —`settings.json` en Claude Code, `hooks.json` en
   Codex—, **no en un repo de configuración versionado**, porque llevan una ruta local. Los dos
   agentes aceptan `SessionStart` y `UserPromptSubmit`, y lo que el hook escribe en stdout entra
   como contexto.

   - **`aviso.py` va en `UserPromptSubmit`**, en cualquier agente que escriba el cerebro. Avisa
     cuando pasan muchos mensajes sin que el vault cambie. Un lector no lo necesita.
   - **`indice.py` va en `SessionStart`, y solo si el agente no expande imports.** Claude Code sí
     los expande, así que ahí sobra: el `@ruta/MEMORY.md` de la regla ya mete el índice en cada
     sesión. **Codex no los expande** —la línea le queda como texto—, así que sin este hook el
     índice nunca llega solo y la memoria depende de que el modelo decida abrir el archivo. Con
     él, Codex arranca con el mapa igual que Claude. Instálalo tanto para un escritor como para
     un lector: leer el índice es justamente lo que un lector viene a hacer.

3. **La regla en el archivo del agente.** Sin esto, ninguna sesión sabe que el cerebro existe.
   Escríbela en el archivo del agente que te invocó, con la ruta real del vault: usa
   `plantillas/reglas.md` si es escritor, o `plantillas/reglas-lectura.md` si es lector.

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
que se sabía, y sobrevive a que se muera el disco. Si la persona dice que sí, `git init`, copia
`plantillas/pre-commit` a `.githooks/pre-commit` y corre `git config core.hooksPath .githooks`:
así el check corre solo en cada commit y nada que lo rompa entra al historial. La disciplina de
commitear y publicar es suya y se anota en `forma-de-trabajo/`, no acá.

---

## Al cerrar

**Si este agente quedó como lector**, di en dos líneas qué vault va a leer, que no lo va a
escribir y quién sigue a cargo de escribirlo. Nada más: no corras el check, que es del escritor.

**Si quedó como escritor**, corre `python3 check.py` en el vault y muestra el resultado. Termina
diciendo, en pocas líneas: cuántas notas quedaron, qué contextos se crearon, qué quedó pendiente
de escribir, y **una cosa concreta que la persona pueda hacer ahora** para probar que funciona —
por ejemplo, abrir el vault en Obsidian, o pedirle al agente algo que use un hecho que acaba de
quedar escrito.

En cualquiera de los dos casos, si hay otro agente en la máquina sin configurar, menciónalo en
una línea: correr `/init-brain` allá lo conecta al mismo cerebro, como lector o escritor.
