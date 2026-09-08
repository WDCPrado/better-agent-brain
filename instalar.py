#!/usr/bin/env python3
"""Deja /init-brain disponible en los agentes que encuentre en esta máquina.

No toca ningún vault: el cerebro se crea después, corriendo el comando.

Por defecto copia, para que este repo se pueda borrar después de instalar.
Con --link deja un enlace simbólico, que es lo que quieres si vas a editar la
skill. En Windows los symlinks piden permisos especiales, así que si falla se
cae a copiar y lo dice.

Corre igual en Linux, macOS y Windows: solo Python, sin dependencias.
"""
import pathlib
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parent
ORIGEN = REPO / "skills" / "init-brain"   # las plantillas viven dentro, así los dos
                                          # modos dejan exactamente la misma estructura

# El comando cambia por agente: Claude Code usa slash commands; en Codex las
# skills son menciones con $ (o se eligen con /skills).
AGENTES = [("Claude Code", ".claude", "/init-brain"), ("Codex", ".codex", "$init-brain")]


def borrar(p: pathlib.Path) -> None:
    if p.is_symlink() or p.is_file():
        p.unlink()
    elif p.exists():
        shutil.rmtree(p)


def instalar(base: pathlib.Path, enlazar: bool) -> str:
    """Devuelve el modo usado, o lanza si no se pudo.

    La versión nueva se arma aparte y entra de un solo movimiento: si algo falla a
    medias, la anterior sigue donde estaba. Y si la anterior era una copia —quizá
    editada a mano— queda como `init-brain.anterior`, por si hay que volver."""
    destino = base / "skills" / "init-brain"
    destino.parent.mkdir(parents=True, exist_ok=True)
    nuevo = destino.with_name("init-brain.nuevo")
    anterior = destino.with_name("init-brain.anterior")
    borrar(nuevo)

    modo = "copiado"
    if enlazar:
        try:
            nuevo.symlink_to(ORIGEN, target_is_directory=True)
            modo = "enlazado"
        except OSError:
            pass  # Windows sin modo desarrollador: se copia y se avisa
    if modo == "copiado":
        shutil.copytree(ORIGEN, nuevo)

    habia = destino.is_symlink() or destino.exists()
    if habia:
        borrar(anterior)
        destino.rename(anterior)
    try:
        nuevo.rename(destino)
    except Exception:
        if habia:
            anterior.rename(destino)
        raise
    if habia and anterior.is_symlink():
        anterior.unlink()  # un enlace no guarda nada propio; una copia sí, y se queda de respaldo
    return modo


def main() -> int:
    enlazar = "--link" in sys.argv[1:]
    casa = pathlib.Path.home()

    print("Instalando /init-brain:", flush=True)
    encontrados = []
    for nombre, carpeta, _ in AGENTES:
        base = casa / carpeta
        if not base.is_dir():
            continue
        try:
            modo = instalar(base, enlazar)
        except Exception as e:
            print(f"  {nombre}: no se pudo ({e})", file=sys.stderr)
            continue
        encontrados.append(nombre)
        aviso = " (symlink no permitido, se copió)" if enlazar and modo == "copiado" else ""
        print(f"  {nombre:<12} -> {base / 'skills' / 'init-brain'}{aviso}")
        anterior = base / "skills" / "init-brain.anterior"
        if anterior.exists():
            print(f"  {'':<12}    la versión anterior quedó en {anterior}; bórrala cuando no la necesites")

    if not encontrados:
        print(
            "  Ningún agente encontrado (~/.claude ni ~/.codex).\n"
            "  Instala Claude Code o Codex y ábrelo una vez para que cree su carpeta.",
            file=sys.stderr,
        )
        return 1

    if not enlazar:
        print("\nEste repo ya no hace falta; puedes borrarlo.")
    print("\nAbre tu agente y escribe:")
    for nombre, _, comando in AGENTES:
        if nombre in encontrados:
            print(f"  {nombre:<12} {comando}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
