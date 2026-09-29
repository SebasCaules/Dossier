"""Dónde van los documentos y sus PDF.

Todos los documentos viven en dossiers/, en la raíz del proyecto: cada uno en
dossiers/<nombre>/ y su PDF compilado en dossiers/pdfs/<nombre>.pdf, junto a los de los
demás. Un .tex que no está en una carpeta de dossiers/ (uno de una versión anterior de la
skill, un ejemplo) deja el PDF a su lado, como antes. Solo usa la biblioteca estándar.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

DOSSIERS = "dossiers"
PDFS = "pdfs"


def carpeta_dossiers(raiz: str | Path | None = None) -> Path:
    """La carpeta dossiers/ que toca. Si la carpeta de partida (--raiz o, sin ella, la
    actual) ya está dentro de un dossiers/ con pdfs/, ese; si no, el de --raiz o, sin
    --raiz, el de la raíz del repositorio git (o de la carpeta actual si no hay)."""
    desde = Path(raiz).expanduser().resolve() if raiz else Path.cwd().resolve()
    for carpeta in (desde, *desde.parents):
        if carpeta.name == DOSSIERS and (carpeta / PDFS).is_dir():
            return carpeta
    if raiz is None:
        try:
            r = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=desde,
                               capture_output=True, text=True)
            if r.returncode == 0 and r.stdout.strip():
                desde = Path(r.stdout.strip())
        except OSError:  # sin git
            pass
    return desde / DOSSIERS


def pdf_de(tex: Path) -> Path:
    """El PDF de un .tex: dossiers/pdfs/<nombre>.pdf si el .tex está en dossiers/<carpeta>/;
    si no, a su lado."""
    if tex.parent.parent.name == DOSSIERS:
        return tex.parent.parent / PDFS / f"{tex.stem}.pdf"
    return tex.with_suffix(".pdf")


def carpeta_de(pdf: Path) -> Path:
    """La carpeta del documento de un PDF: dossiers/<nombre>/ para uno de dossiers/pdfs/, y
    si no, la del propio PDF."""
    if pdf.parent.name == PDFS and pdf.parent.parent.name == DOSSIERS:
        carpeta = pdf.parent.parent / pdf.stem
        if carpeta.is_dir():
            return carpeta
    return pdf.parent
