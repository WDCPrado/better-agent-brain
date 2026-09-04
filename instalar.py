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
ORIGEN = REPO / "skills" / "init-brain"
PLANTILLAS = REPO / "plantillas"

AGENTES = [("Claude Code", ".claude"), ("Codex", ".codex")]


def instalar(base: pathlib.Path, enlazar: bool) -> str:
    """Devuelve el modo usado, o lanza si no se pudo."""
    destino = base / "skills" / "init-brain"
    destino.parent.mkdir(parents=True, exist_ok=True)

    if destino.is_symlink() or destino.exists():
        (destino.unlink if destino.is_symlink() else lambda: shutil.rmtree(destino))()

    if enlazar:
        try:
            destino.symlink_to(ORIGEN, target_is_directory=True)
            return "enlazado"
        except OSError:
            pass  # Windows sin modo desarrollador: se copia y se avisa

    shutil.copytree(ORIGEN, destino)
    shutil.copytree(PLANTILLAS, destino / "plantillas")
    return "copiado"


def main() -> int:
    enlazar = "--link" in sys.argv[1:]
    casa = pathlib.Path.home()

    print("Instalando /init-brain:", flush=True)
    encontrados = 0
    for nombre, carpeta in AGENTES:
        base = casa / carpeta
        if not base.is_dir():
            continue
        try:
            modo = instalar(base, enlazar)
        except Exception as e:
            print(f"  {nombre}: no se pudo ({e})", file=sys.stderr)
            continue
        encontrados += 1
        aviso = " (symlink no permitido, se copió)" if enlazar and modo == "copiado" else ""
        print(f"  {nombre:<12} -> {base / 'skills' / 'init-brain'}{aviso}")

    if not encontrados:
        print(
            "  Ningún agente encontrado (~/.claude ni ~/.codex).\n"
            "  Instala Claude Code o Codex y ábrelo una vez para que cree su carpeta.",
            file=sys.stderr,
        )
        return 1

    if not enlazar:
        print("\nEste repo ya no hace falta; puedes borrarlo.")
    print("Abre tu agente y corre /init-brain")
    return 0


if __name__ == "__main__":
    sys.exit(main())
