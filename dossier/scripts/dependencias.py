#!/usr/bin/env python3
"""Verifica e instala lo que la skill necesita para compilar, medir y dibujar.

    python3 dependencias.py                  dice qué hay y qué falta (sale con 1 si falta algo)
    python3 dependencias.py instalar         instala lo que falta, sin permisos de administrador
            [--capturas] [--sin-tex] [--sin-python] [--sin-prueba]

Qué instala y dónde:
  - LaTeX: si no hay lualatex y latexmk, TinyTeX (una versión chica de TeX Live) en
    ~/Library/TinyTeX (macOS) o ~/.TinyTeX (Linux), con los paquetes que usa dossier.sty.
    Si ya hay una distribución, solo los paquetes que le falten, con su tlmgr; si es del
    sistema y no se puede escribir en ella, dice el comando.
  - Python: un entorno propio en ~/.local/share/dossier/venv con matplotlib, numpy, Pillow,
    pypdf, pdfplumber y pypdfium2. Los scripts de la skill lo usan solos.
  - Con --capturas, Playwright y Chromium en ese entorno (para scripts/capturar.py).
Poppler no hace falta: si está, se usa; si no, las páginas se leen con pypdfium2.
Al final compila una hoja de prueba con la plantilla de la skill.
"""
from __future__ import annotations

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
sys.dont_write_bytecode = True
import _entorno  # noqa: E402

# Paquetes de TeX Live que usan las plantillas y los componentes de dossier.sty (sacados
# del registro de compilación de las plantillas y los ejemplos), más las letras de fuera
# de macOS y latexmk. tlmgr saltea los que ya están, y si un año de TeX Live renombra o
# funde un paquete (l3backend pasó a l3kernel), manda que estén los ARCHIVOS_CLAVE.
PAQUETES_TEX = """adjustbox amsmath babel babel-spanish bigintcalc bitset bookmark booktabs caption cm
collectbox enumitem environ epstopdf-pkg etoolbox fancyhdr fontspec geometry gettitlestring
graphics graphics-cfg graphics-def hycolor hyperref hyphen-spanish ifoddpage iftex infwarerr
intcalc kvdefinekeys kvoptions kvsetkeys l3kernel l3packages lastpage latex
latexconfig listings ltxcmds lua-uni-algos lualatex-math lualibs luaotfload microtype mptopdf
needspace pdfcol pdfescape pdftexcmds pgf refcount rerunfilecheck stringenc tcolorbox
tex-ini-files tikzfill titlesec tools trimspaces unicode-data unicode-math uniquecounter url
varwidth was xcolor xkeyval xurl latexmk firamath fira tex-gyre lm lm-math""".split()

# Un archivo por paquete que suele faltar en una distribución chica: si kpsewhich no
# encuentra alguno, se instala la lista entera.
ARCHIVOS_CLAVE = """fontspec.sty unicode-math.sty luaotfload.sty lualatex-math.sty tcolorbox.sty
tikzfill.image.sty pdfcol.sty environ.sty trimspaces.sty varwidth.sty titlesec.sty
titletoc.sty enumitem.sty needspace.sty lastpage.sty xurl.sty bookmark.sty adjustbox.sty
collectbox.sty ifoddpage.sty listings.sty icomma.sty caption.sty fancyhdr.sty booktabs.sty
microtype.sty spanish.ldf loadhyph-es.tex FiraMath-Regular.otf FiraMono-Regular.otf
texgyreheros-regular.otf""".split()

PAQUETES_PY = ["matplotlib", "numpy", "pillow", "pypdf", "pdfplumber", "pypdfium2"]
MODULOS_PY = ["matplotlib", "numpy", "PIL", "pypdf", "pdfplumber", "pypdfium2"]
TINYTEX = "https://github.com/rstudio/tinytex-releases/releases/download/daily/"
GET_PIP = "https://bootstrap.pypa.io/get-pip.py"
MARCA_PATH = "# TinyTeX, instalado por la skill dossier"


def decir(texto: str = "") -> None:
    print(texto, flush=True)


def correr(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run([str(c) for c in cmd], **kw)


# ---------------------------------------------------------------- LaTeX

def buscar_tex() -> dict | None:
    carpeta = _entorno.poner_tex_en_el_path()
    if not carpeta:
        return None
    lualatex = os.path.join(carpeta, "lualatex")
    if not os.path.exists(lualatex) and not shutil.which("lualatex"):
        return None
    tlmgr = os.path.join(carpeta, "tlmgr")
    kpse = os.path.join(carpeta, "kpsewhich")
    raiz = ""
    if os.path.exists(kpse):
        r = correr([kpse, "-var-value=TEXMFROOT"], capture_output=True, text=True)
        raiz = r.stdout.strip()
    return {"carpeta": carpeta, "tlmgr": tlmgr if os.path.exists(tlmgr) else None,
            "kpsewhich": kpse if os.path.exists(kpse) else None, "raiz": raiz,
            "escribible": bool(raiz) and os.access(raiz, os.W_OK),
            "tinytex": "TinyTeX" in carpeta}


def faltantes_tex(tex: dict) -> list[str]:
    if not tex.get("kpsewhich"):
        return list(ARCHIVOS_CLAVE)
    r = correr([tex["kpsewhich"], *ARCHIVOS_CLAVE], capture_output=True, text=True)
    hallados = {os.path.basename(x) for x in r.stdout.split()}
    return [a for a in ARCHIVOS_CLAVE if a not in hallados]


def tlmgr_instalar(tex: dict) -> bool:
    decir(f"Instalando los paquetes de LaTeX que usa la skill (tlmgr, {len(PAQUETES_TEX)} paquetes; "
          "un par de minutos)…")
    r = correr([tex["tlmgr"], "install", *PAQUETES_TEX], capture_output=True, text=True)
    faltan = faltantes_tex(tex)
    if faltan:
        salida = (r.stdout + r.stderr).strip()
        decir(f"tlmgr no dejó todo: faltan {', '.join(faltan)}.\n{salida[-1500:]}")
        if "newer" in salida or "más nuevo" in salida:
            decir(f"La distribución es más vieja que el repositorio: {tex['tlmgr']} update --self --all")
        return False
    luaotfload = os.path.join(tex["carpeta"], "luaotfload-tool")
    if os.path.exists(luaotfload):
        decir("Armando la base de letras de LuaTeX (la primera vez tarda un poco)…")
        correr([luaotfload, "--update"], capture_output=True)
    return True


def perfil_de_shell() -> Path:
    shell = os.path.basename(os.environ.get("SHELL", ""))
    if shell == "zsh":
        return Path.home() / ".zshrc"
    if shell == "bash":
        return Path.home() / (".bash_profile" if platform.system() == "Darwin" else ".bashrc")
    return Path.home() / ".profile"


def instalar_tinytex() -> dict | None:
    sistema, maquina = platform.system(), platform.machine().lower()
    if sistema == "Darwin":
        archivo, padre, nombre = "TinyTeX-1-darwin.tar.xz", Path.home() / "Library", "TinyTeX"
    elif sistema == "Linux" and maquina in ("x86_64", "amd64", "aarch64", "arm64"):
        musl = bool(glob.glob("/lib/libc.musl-*.so.1"))
        if maquina in ("aarch64", "arm64"):
            archivo = "TinyTeX-1-linux-arm64.tar.xz"
        else:
            archivo = "TinyTeX-1-linuxmusl-x86_64.tar.xz" if musl else "TinyTeX-1-linux-x86_64.tar.xz"
        padre, nombre = Path.home(), ".TinyTeX"
    else:
        decir(f"No hay TinyTeX listo para {sistema} {maquina}. Instalar TeX Live a mano:\n"
              "  https://tug.org/texlive/  (con lualatex y latexmk)")
        return None
    if not shutil.which("perl"):
        decir("TinyTeX necesita perl (tlmgr está escrito en perl). En Debian o Ubuntu: sudo apt install perl")
        return None
    destino = padre / nombre
    if destino.exists():
        decir(f"Ya existe {destino} pero no tiene latexmk: no lo piso. Borrarlo o completarlo a mano.")
        return None
    padre.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        paquete = Path(tmp) / archivo
        decir(f"Descargando TinyTeX ({archivo}, unos 60 MB)…")
        descargar(TINYTEX + archivo, paquete)
        decir(f"Descomprimiendo en {destino}…")
        with tarfile.open(paquete, "r:xz") as tar:
            try:
                tar.extractall(padre, filter="tar")
            except TypeError:  # Python anterior a 3.12
                tar.extractall(padre)
    binarios = sorted(glob.glob(str(destino / "bin" / "*")))
    if not binarios:
        decir("TinyTeX se descomprimió sin la carpeta bin: algo salió mal en la descarga.")
        return None
    carpeta = binarios[0]
    os.environ["PATH"] = carpeta + os.pathsep + os.environ.get("PATH", "")
    tlmgr = os.path.join(carpeta, "tlmgr")
    # PATH para las terminales nuevas. En Linux, enlaces en ~/.local/bin (como el instalador
    # oficial); en macOS, una línea en el perfil del shell, sin tocar /usr/local/bin.
    if sistema == "Linux":
        bin_usuario = Path.home() / ".local" / "bin"
        bin_usuario.mkdir(parents=True, exist_ok=True)
        correr([tlmgr, "option", "sys_bin", str(bin_usuario)], capture_output=True)
        correr([tlmgr, "path", "add"], capture_output=True)
        decir(f"Enlaces de TeX en {bin_usuario} (tiene que estar en el PATH).")
    else:
        perfil = perfil_de_shell()
        linea = f'export PATH="{carpeta}:$PATH"'
        actual = perfil.read_text(encoding="utf-8") if perfil.exists() else ""
        if linea not in actual:
            with perfil.open("a", encoding="utf-8") as f:
                f.write(f"\n{MARCA_PATH}\n{linea}\n")
            decir(f"TinyTeX queda en el PATH de las terminales nuevas (línea agregada a {perfil}).")
    return buscar_tex()


def descargar(url: str, destino: Path) -> None:
    # curl primero: el Python de python.org en macOS suele no tener los certificados.
    if shutil.which("curl"):
        if correr(["curl", "-fL", "--retry", "3", "-#", "-o", destino, url]).returncode == 0:
            return
    with urllib.request.urlopen(url) as r, destino.open("wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        hecho, ultimo = 0, 0.0
        while True:
            bloque = r.read(1 << 20)
            if not bloque:
                break
            f.write(bloque)
            hecho += len(bloque)
            if total and time.time() - ultimo > 2:
                ultimo = time.time()
                print(f"  {hecho * 100 // total} %", flush=True)


def instalar_latex() -> bool:
    tex = buscar_tex()
    if not tex:
        tex = instalar_tinytex()
        return bool(tex) and tlmgr_instalar(tex)
    faltan = faltantes_tex(tex)
    if not faltan:
        decir(f"LaTeX: completo ({tex['carpeta']}).")
        return True
    decir(f"LaTeX: faltan {len(faltan)} archivos ({', '.join(faltan[:5])}{'…' if len(faltan) > 5 else ''}).")
    if tex["tlmgr"] and tex["escribible"]:
        return tlmgr_instalar(tex)
    decir("La distribución es del sistema y no se puede escribir en ella sin permisos. Opciones:\n"
          f"  sudo {tex['tlmgr'] or 'tlmgr'} install {' '.join(PAQUETES_TEX)}\n"
          "  En Debian o Ubuntu: sudo apt install texlive-luatex texlive-latex-extra "
          "texlive-fonts-extra texlive-lang-spanish latexmk")
    return False


# ---------------------------------------------------------------- Python

def python_completo(py: Path) -> list[str]:
    """Los módulos que faltan en ese Python."""
    if not py.exists():
        return list(MODULOS_PY)
    codigo = ("import importlib.util as u; print(' '.join(m for m in %r if u.find_spec(m) is None))"
              % (MODULOS_PY,))
    r = correr([py, "-c", codigo], capture_output=True, text=True)
    return r.stdout.split() if r.returncode == 0 else list(MODULOS_PY)


def instalar_python(capturas: bool) -> bool:
    if sys.version_info < (3, 9):
        decir(f"Hace falta Python 3.9 o más nuevo (este es {platform.python_version()}).")
        return False
    py = _entorno.python_del_entorno()
    if not py.exists():
        decir(f"Creando el entorno de Python en {_entorno.VENV}…")
        _entorno.VENV.parent.mkdir(parents=True, exist_ok=True)
        r = correr([sys.executable, "-m", "venv", _entorno.VENV], capture_output=True, text=True)
        if r.returncode != 0 or not _tiene_pip(py):
            # Debian y Ubuntu traen Python sin ensurepip: entorno sin pip y get-pip.py.
            shutil.rmtree(_entorno.VENV, ignore_errors=True)
            r = correr([sys.executable, "-m", "venv", "--without-pip", _entorno.VENV],
                       capture_output=True, text=True)
            if r.returncode != 0:
                decir("No se pudo crear el entorno de Python:\n" + r.stderr.strip())
                return False
            with tempfile.TemporaryDirectory() as tmp:
                get_pip = Path(tmp) / "get-pip.py"
                descargar(GET_PIP, get_pip)
                if correr([py, get_pip, "-q"]).returncode != 0:
                    return False
    faltan = python_completo(py)
    paquetes = PAQUETES_PY + (["playwright"] if capturas else [])
    if faltan or capturas:
        decir(f"Instalando {', '.join(paquetes)} en el entorno (unos 100 MB)…")
        r = correr([py, "-m", "pip", "install", "-q", "--disable-pip-version-check", *paquetes])
        if r.returncode != 0:
            return False
    if capturas:
        decir("Instalando Chromium para las capturas…")
        if correr([py, "-m", "playwright", "install", "chromium"]).returncode != 0:
            return False
    decir(f"Python: completo ({_entorno.VENV}).")
    return True


def _tiene_pip(py: Path) -> bool:
    return py.exists() and correr([py, "-m", "pip", "--version"], capture_output=True).returncode == 0


# ---------------------------------------------------------------- estado y prueba

def estado() -> list[tuple[str, bool, bool, str]]:
    """(qué, está, hace falta, detalle)."""
    filas = []
    tex = buscar_tex()
    if tex:
        faltan = faltantes_tex(tex)
        filas.append(("LaTeX (lualatex, latexmk)", True, True, tex["carpeta"]))
        filas.append(("Paquetes y letras de LaTeX", not faltan, True,
                      "completos" if not faltan else f"faltan {len(faltan)}: {', '.join(faltan[:4])}…"))
    else:
        filas.append(("LaTeX (lualatex, latexmk)", False, True, "no hay"))
    py = _entorno.python_del_entorno()
    faltan_py = python_completo(py)
    filas.append(("Python y sus paquetes", not faltan_py, True,
                  str(_entorno.VENV) if not faltan_py else
                  ("no está el entorno" if not py.exists() else f"faltan {', '.join(faltan_py)}")))
    poppler = all(shutil.which(p) for p in ("pdftoppm", "pdftotext", "pdfinfo"))
    filas.append(("Poppler", poppler, False, "se usa" if poppler else "no hace falta: se usa pypdfium2"))
    captura = py.exists() and correr([py, "-c", "import playwright"], capture_output=True).returncode == 0
    filas.append(("Playwright (capturas)", captura, False, "listo" if captura else "opcional: instalar --capturas"))
    return filas


def informar(filas) -> bool:
    ancho = max(len(f[0]) for f in filas)
    for que, esta, falta_si, detalle in filas:
        marca = "sí" if esta else ("NO" if falta_si else "no")
        decir(f"  {que.ljust(ancho)}  {marca.ljust(2)}  {detalle}")
    return all(esta for _, esta, hace_falta, _ in filas if hace_falta)


def prueba() -> bool:
    """Crea una hoja con la plantilla de la skill y la mide: si compila, está todo."""
    decir("Compilando una hoja de prueba…")
    inicio = time.time()
    py = _entorno.python_del_entorno()
    python = str(py) if py.exists() else sys.executable
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp) / "prueba"
        r = correr([python, "-B", AQUI / "nuevo.py", carpeta, "--perfil", "1 hoja"], capture_output=True, text=True)
        if r.returncode != 0:
            decir("nuevo.py falló:\n" + (r.stdout + r.stderr).strip()[-1500:])
            return False
        r = correr([python, "-B", AQUI / "medir.py", carpeta / "prueba.tex", "--paginas", "1"],
                   capture_output=True, text=True)
        if r.returncode != 0 or not (carpeta / "prueba.pdf").exists():
            decir("La hoja de prueba no compiló:\n" + (r.stdout + r.stderr).strip()[-2500:])
            return False
    decir(f"La hoja de prueba compiló y se midió en {round(time.time() - inicio)} s.")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("accion", nargs="?", choices=["verificar", "instalar"], default="verificar")
    ap.add_argument("--capturas", action="store_true", help="también Playwright y Chromium")
    ap.add_argument("--sin-tex", action="store_true")
    ap.add_argument("--sin-python", action="store_true")
    ap.add_argument("--sin-prueba", action="store_true")
    a = ap.parse_args()

    if platform.system() == "Windows":
        decir("En Windows, instalar TeX Live (https://tug.org/texlive/) y, con pip, "
              + " ".join(PAQUETES_PY) + ". La skill funciona mejor dentro de WSL.")
        return 1
    if a.accion == "verificar":
        decir("Lo que necesita la skill dossier:")
        return 0 if informar(estado()) else 1

    ok = True
    if not a.sin_tex:
        ok = instalar_latex() and ok
    if not a.sin_python:
        ok = instalar_python(a.capturas) and ok
    decir()
    decir("Lo que necesita la skill dossier:")
    completo = informar(estado())
    if ok and completo and not a.sin_prueba:
        ok = prueba()
    return 0 if ok and completo else 1


if __name__ == "__main__":
    sys.exit(main())
