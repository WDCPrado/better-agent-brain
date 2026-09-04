# better-agent-brain

Memoria entre sesiones para agentes de código, en archivos de texto que tú controlas.
Funciona con **Claude Code** y con **Codex**.

Tu agente no recuerda nada de una sesión a la otra. Lo que se pierde no es el código —eso está
en git— sino **lo que costó descubrir**: por qué se descartó la librería obvia, qué se rompe si
tocas ese endpoint, qué restricción del proveedor no está documentada en ninguna parte. Eso se
vuelve a explicar cada vez, o se vuelve a aprender a golpes.

Este repo instala un comando, `/init-brain`, que te entrevista, lee tus repos y deja funcionando
un **vault de Obsidian** donde el agente escribe esas cosas al terminar de trabajar, y las lee
antes de empezar.

## Qué no es

No es un RAG ni un índice de transcripciones. No hay embeddings, ni base vectorial, ni un
servicio corriendo. Son archivos markdown y un índice de una pantalla que se carga entero en
cada sesión.

La apuesta es que **destilar gana a grabar**: una nota escrita a mano con el hecho que importa
vale más que la conversación completa donde ese hecho apareció. Mientras el índice quepa en el
contexto —y cabe hasta unos cientos de notas— la recuperación es perfecta y cuesta cero.

Además lo puedes leer tú. Es un vault de Obsidian; el grafo es tuyo.

## Instalación

```bash
git clone https://github.com/<usuario>/better-agent-brain.git
cd better-agent-brain
./instalar.sh
```

Detecta los agentes que tengas (`~/.claude`, `~/.codex`) e instala el comando en cada uno. Luego:

```
/init-brain
```

**Este repo no es tu cerebro.** Es solo el instalador: copia el comando y después se puede
borrar. Tu vault se crea en otra ruta y es tuyo.

Si vas a modificar la skill, instala con `./instalar.sh --link` para que quede enlazada a este
repo en vez de copiada.

## Qué hace `/init-brain`

1. **Busca tu vault** antes de tocar nada. El puntero es la ruta del índice en el archivo de
   reglas de tu agente (`~/.claude/CLAUDE.md` o `~/.codex/AGENTS.md`), así que si ya tienes un
   cerebro lo encuentra y **no crea uno nuevo al lado**.
2. **Te entrevista** en tres bloques: tú y lo que construyes por tu cuenta; las organizaciones
   donde trabajas, con sus proyectos y sus reglas; y los terceros de los que dependes. Lo que se
   puede detectar solo —el sistema operativo, los repos que tienes— te lo muestra para confirmar
   en vez de preguntártelo.
3. **Lee los repos** que le pases, por URL o por ruta.
4. **Escribe el vault**: los contextos, el índice y las cuatro carpetas.
5. **Deja el sistema andando**: `check.sh` para que no se pudra, un hook que recuerda escribir, y
   la regla en el archivo de tu agente —en los dos, si tienes los dos, apuntando al mismo vault.

Si ya tenías notas, entra en **modo reorganizar**: mueve información, no la crea ni la corrige.
Cuando algo del vault contradice lo que respondiste, para y te pregunta cuál de las dos gana.

## La forma del vault

```
MEMORY.md              el índice; lo único que se carga en cada sesión
contextos/             ¿qué es esto y cómo funciona?   se edita
decisiones/            ¿por qué está así?              inmutable
tecnicas/              ¿cómo se hace esto?             se edita
forma-de-trabajo/      ¿cómo trabajas y por qué?       se edita
```

`MEMORY.md` lista solo cuatro secciones —la persona, sus organizaciones, los terceros que usa y
lo transversal—, así que **no crece cuando crece el cerebro**. Todo lo demás se alcanza bajando
por los enlaces de cada contexto. Esa es la razón por la que se puede cargar entero, siempre.

## Git es tuyo, no de este sistema

El vault **no tiene que ser un repo**, y `/init-brain` no lo convierte en uno. El hook y el
`check.sh` funcionan igual en disco pelado.

Versionarlo tiene ventajas reales —ver cómo evolucionó lo que sabías, sobrevivir a un disco
muerto—, pero es tu decisión y tu disciplina. Si la tomas, esa regla va en `forma-de-trabajo/`,
que es parte de tu memoria, no del instalador.

## Mantenimiento

```bash
./check.sh    # dentro de tu vault
```

Verifica que toda nota sea alcanzable desde el índice, que ningún nombre esté repetido, y lista
los enlaces a notas que todavía no existen —que no son errores: son lo que falta escribir.
