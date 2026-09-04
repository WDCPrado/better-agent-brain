# claude-brain

Un cerebro para Claude Code: memoria entre sesiones, en archivos de texto que tú controlas.

Claude no recuerda nada de una sesión a la otra. Lo que se pierde no es el código —eso está en
git— sino **lo que costó descubrir**: por qué se descartó la librería obvia, qué rompe si tocas
ese endpoint, qué restricción del proveedor no está documentada en ninguna parte. Eso se vuelve
a explicar cada vez, o se vuelve a aprender a golpes.

Este repo instala un comando, `/init-claude-brain`, que te entrevista, lee tus repos y deja
funcionando un **vault de Obsidian versionado en git** donde Claude escribe esas cosas al
terminar de trabajar, y las lee antes de empezar.

## Qué no es

No es un RAG ni un índice de transcripciones. No hay embeddings, ni base vectorial, ni un
servicio corriendo. Son archivos markdown y un índice de una pantalla que se carga entero en
cada sesión.

La apuesta es que **destilar gana a grabar**: una nota escrita a mano con el hecho que importa
vale más que la conversación completa donde ese hecho apareció. Cuando el índice quepa en el
contexto —y cabe hasta unos cientos de notas— la recuperación es perfecta y cuesta cero.

Además lo puedes leer tú. Es un vault de Obsidian; el grafo es tuyo.

## Instalación

```bash
git clone https://github.com/<usuario>/claude-brain.git
cd claude-brain
./instalar.sh
```

Luego, en Claude Code:

```
/init-claude-brain
```

**Este repo no es tu cerebro.** Es solo el instalador: copia el comando a `~/.claude/skills/` y
después se puede borrar. Tu vault se crea en otra ruta, con su propio git, y es tuyo.

Si vas a modificar la skill, instala con `./instalar.sh --link` para que quede enlazada a este
repo en vez de copiada.

## Qué hace `/init-claude-brain`

1. **Busca tu vault** antes de tocar nada. El puntero es el import del índice en tu
   `~/.claude/CLAUDE.md`, así que si ya tienes un cerebro lo encuentra y no crea uno nuevo.
2. **Te entrevista** en tres bloques: tú y lo que construyes por tu cuenta; las organizaciones
   donde trabajas, con sus proyectos y sus reglas; y los terceros de los que dependes. Lo que se
   puede detectar solo —el sistema operativo, los repos que tienes— te lo muestra para confirmar
   en vez de preguntártelo.
3. **Lee los repos** que le pases, por URL o por ruta.
4. **Escribe el vault**: los contextos, el índice y las cuatro carpetas.
5. **Deja el sistema andando**: `check.sh` para que no se pudra, un hook que recuerda escribir y
   publicar, y el bloque en tu `CLAUDE.md` para que todas las sesiones lo usen.

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

## Mantenimiento

```bash
./check.sh    # dentro de tu vault
```

Verifica que toda nota sea alcanzable desde el índice, que ningún nombre esté repetido, y lista
los enlaces a notas que todavía no existen —que no son errores: son lo que falta escribir.
