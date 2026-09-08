#!/usr/bin/env python3
"""Las pruebas del instalador y del check. Se corren con `python3 pruebas.py`.

Cada una es un escenario de la revisión del 2026-09-07: lo que fallaba, ahora falla
ruidosamente o ya no falla. Sin framework: asserts y la biblioteca estándar.
"""
import importlib.util, os, pathlib, shutil, subprocess, sys, tempfile

REPO = pathlib.Path(__file__).resolve().parent
CHECK = REPO / "skills" / "init-brain" / "plantillas" / "check.py"


def vault(raiz, notas):
    """Escribe un vault de prueba: {ruta relativa: texto}. MEMORY.md incluido."""
    for rel, texto in notas.items():
        p = raiz / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(texto)
    return raiz


def nota(name, contexto=(), extra=""):
    ctx = "".join(f'\n  - "[[{c}]]"' for c in contexto) or " []"
    return f"---\nname: {name}\ndescription: x\ncontexto:{ctx}\nfecha: 2026-01-01\ntags: []\n{extra}---\n\ncuerpo\n"


def check(raiz):
    r = subprocess.run([sys.executable, str(CHECK), str(raiz)], capture_output=True, text=True)
    return r.returncode, r.stdout


BASE = {
    "MEMORY.md": "- [[org]]\n",
    "contextos/org/org.md": nota("org") + "- [[repo]]\n- [[decision]]\n",
    "contextos/org/repo/repo.md": nota("repo", ["org"]),
    "decisiones/decision.md": nota("decision", ["org"]),
}


def prueba_carpeta_oculta():
    """5.3: un vault bajo ~/.brain inventariaba cero notas y salía verde."""
    with tempfile.TemporaryDirectory() as tmp:
        visible = vault(pathlib.Path(tmp) / "brain", BASE)
        oculta = vault(pathlib.Path(tmp) / ".brain", BASE)
        assert check(visible) == check(oculta), "el inventario cambia con una carpeta oculta"
        assert check(visible)[0] == 0 and "3 notas, 3 alcanzables" in check(visible)[1]


def prueba_inventario_vacio():
    with tempfile.TemporaryDirectory() as tmp:
        raiz = vault(pathlib.Path(tmp), {"MEMORY.md": "- [[org]]\n"})
        codigo, salida = check(raiz)
        assert codigo == 1 and "no se encontró ninguna" in salida, salida


def prueba_pertenencia():
    """Declarar un contexto que no te indexa es una huérfana disfrazada."""
    with tempfile.TemporaryDirectory() as tmp:
        notas = dict(BASE)
        notas["tecnicas/truco.md"] = nota("truco", ["repo"])   # repo no la lista
        codigo, salida = check(vault(pathlib.Path(tmp), notas))
        assert codigo == 1 and "repo.md no la indexa" in salida, salida
        notas["contextos/org/repo/repo.md"] += "- [[truco]]\n"
        assert check(vault(pathlib.Path(tmp), notas))[0] == 0


def prueba_deriva_reciproca():
    with tempfile.TemporaryDirectory() as tmp:
        notas = dict(BASE)
        notas["decisiones/nueva.md"] = nota("nueva", ["org"], 'deriva-de: "[[decision]]"\n')
        notas["contextos/org/org.md"] += "- [[nueva]]\n"
        codigo, salida = check(vault(pathlib.Path(tmp), notas))
        assert codigo == 1 and "la vieja no enlaza a la nueva" in salida, salida
        notas["decisiones/decision.md"] += "\nreemplazada por [[nueva]]\n"
        assert check(vault(pathlib.Path(tmp), notas))[0] == 0


def prueba_frontmatter_y_tamano():
    with tempfile.TemporaryDirectory() as tmp:
        notas = dict(BASE)
        notas["decisiones/decision.md"] = notas["decisiones/decision.md"].replace("2026-01-01", "ayer") + "x\n" * 90
        codigo, salida = check(vault(pathlib.Path(tmp), notas))
        assert codigo == 1 and "no es AAAA-MM-DD" in salida and "huele a bitácora" in salida, salida


def cargar_instalador():
    spec = importlib.util.spec_from_file_location("instalar", REPO / "instalar.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def prueba_reinstalar_no_destruye():
    """5.1: reinstalar borraba la skill antes de tener la nueva; un fallo la dejaba sin nada."""
    inst = cargar_instalador()
    with tempfile.TemporaryDirectory() as tmp:
        base = pathlib.Path(tmp)
        assert inst.instalar(base, enlazar=False) == "copiado"
        skill = base / "skills" / "init-brain"
        (skill / "MIO.md").write_text("personalizado")

        original = pathlib.Path.rename
        def rename_roto(self, target):
            if self.name == "init-brain.nuevo":
                raise OSError("disco lleno")
            return original(self, target)
        pathlib.Path.rename = rename_roto
        try:
            try:
                inst.instalar(base, enlazar=False)
                assert False, "debía fallar"
            except OSError:
                pass
        finally:
            pathlib.Path.rename = original
        assert (skill / "MIO.md").read_text() == "personalizado", "el fallo destruyó la skill anterior"

        assert inst.instalar(base, enlazar=False) == "copiado"
        assert (skill / "SKILL.md").exists() and not (skill / "MIO.md").exists()
        assert (base / "skills" / "init-brain.anterior" / "MIO.md").exists(), "la copia anterior no quedó de respaldo"
        assert not (base / "skills" / "init-brain.nuevo").exists()

        # Se guarda una sola versión anterior, la inmediata: la copia que reemplaza un enlace
        # queda de respaldo; un enlace reemplazado no guarda nada propio y se descarta.
        if os.name != "nt":
            assert inst.instalar(base, enlazar=True) == "enlazado"
            assert skill.is_symlink()
            assert (base / "skills" / "init-brain.anterior" / "SKILL.md").exists()
            assert inst.instalar(base, enlazar=True) == "enlazado"
            assert not (base / "skills" / "init-brain.anterior").exists()


if __name__ == "__main__":
    pruebas = [v for k, v in sorted(globals().items()) if k.startswith("prueba_")]
    for p in pruebas:
        p()
        print("ok ", p.__name__)
    print(f"{len(pruebas)} pruebas pasan")
