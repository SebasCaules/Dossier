"""Dónde están el Python con las dependencias y los programas de TeX.

dependencias.py deja un entorno de Python propio en ~/.local/share/dossier/venv y, si no
había LaTeX, TinyTeX en la carpeta del usuario. usar() hace que el script que lo llama
corra con ese Python y encuentre TeX aunque no esté en el PATH. Solo usa la biblioteca
estándar: tiene que funcionar antes de que haya nada instalado.
"""
from __future__ import annotations

import glob
import os
import shutil
import sys
from pathlib import Path


def carpeta_datos() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
    return Path(base) / "dossier"


VENV = carpeta_datos() / "venv"


def python_del_entorno() -> Path:
    return VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def en_el_entorno() -> bool:
    try:
        return Path(sys.prefix).resolve() == VENV.resolve()
    except OSError:
        return False


def carpetas_tex() -> list[str]:
    """Carpetas con latexmk, de la más probable a la menos: TinyTeX del usuario, MacTeX,
    TeX Live instalado a mano (el año más nuevo primero)."""
    home = os.path.expanduser("~")
    patrones = [f"{home}/Library/TinyTeX/bin/*", f"{home}/.TinyTeX/bin/*", "/Library/TeX/texbin",
                "/usr/local/texlive/*/bin/*", "/opt/texlive/*/bin/*"]
    carpetas: list[str] = []
    for patron in patrones:
        for carpeta in sorted(glob.glob(patron), reverse=True):
            if os.path.exists(os.path.join(carpeta, "latexmk")) and carpeta not in carpetas:
                carpetas.append(carpeta)
    return carpetas


def poner_tex_en_el_path() -> str | None:
    """Si latexmk no está en el PATH, suma la primera carpeta de TeX que lo tenga (vale para
    este proceso y sus hijos). Devuelve la carpeta de latexmk, o None si no hay TeX."""
    ruta = shutil.which("latexmk")
    if ruta:
        return os.path.dirname(ruta)
    for carpeta in carpetas_tex():
        os.environ["PATH"] = carpeta + os.pathsep + os.environ.get("PATH", "")
        return carpeta
    return None


def usar() -> None:
    """TeX en el PATH y, si existe el entorno de la skill, volver a correr el script con su
    Python. DOSSIER_ENTORNO evita el bucle (y, puesto a mano, deja el Python de siempre)."""
    poner_tex_en_el_path()
    py = python_del_entorno()
    if py.exists() and not en_el_entorno() and not os.environ.get("DOSSIER_ENTORNO"):
        os.environ["DOSSIER_ENTORNO"] = "1"
        os.execv(str(py), [str(py), "-B"] + sys.argv)  # -B: sin __pycache__ en la skill
