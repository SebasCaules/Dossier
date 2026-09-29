"""Leer y dibujar las páginas de un PDF: con poppler (pdfinfo, pdftotext, pdftoppm) si
está instalado y, si no, con pypdfium2, que dependencias.py deja en el entorno de la skill.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def _hay(programa: str) -> bool:
    return shutil.which(programa) is not None


def paginas(pdf: Path) -> int:
    try:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf)).pages)
    except Exception:
        pass
    if _hay("pdfinfo"):
        r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True)
        m = re.search(r"^Pages:\s+(\d+)", r.stdout.decode("utf-8", "replace"), re.M)
        if m:
            return int(m.group(1))
    try:
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(pdf))
        try:
            return len(doc)
        finally:
            doc.close()
    except Exception:
        return 0


def textos(pdf: Path) -> list[str]:
    """El texto de cada página, en orden. Vacía si no hay con qué leerlo."""
    if _hay("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True)
        hojas = r.stdout.decode("utf-8", "replace").split("\f")
        if hojas and not hojas[-1].strip():
            hojas = hojas[:-1]
        return hojas
    try:
        import pypdfium2 as pdfium
    except ImportError:
        return []
    doc = pdfium.PdfDocument(str(pdf))
    try:
        salida = []
        for i in range(len(doc)):
            texto = doc[i].get_textpage()
            salida.append(texto.get_text_range())
            texto.close()
        return salida
    finally:
        doc.close()


def imagenes(pdf: Path, dpi: int, primera: int = 1, ultima: int | None = None, gris: bool = False) -> list:
    """Las páginas de primera a ultima (desde 1, inclusive) como imágenes de Pillow."""
    from PIL import Image

    ultima = ultima or paginas(pdf)
    if _hay("pdftoppm"):
        with tempfile.TemporaryDirectory() as tmp:
            cmd = ["pdftoppm", "-r", str(dpi), "-f", str(primera), "-l", str(ultima)]
            cmd += ["-gray"] if gris else ["-png"]
            subprocess.run(cmd + [str(pdf), f"{tmp}/p"], check=True, capture_output=True)
            archivos = sorted(Path(tmp).glob("p-*"), key=lambda q: int(q.stem.split("-")[-1]))
            salida = []
            for archivo in archivos:
                with Image.open(archivo) as im:
                    salida.append(im.copy())
            return salida
    import pypdfium2 as pdfium

    doc = pdfium.PdfDocument(str(pdf))
    try:
        salida = []
        for i in range(primera - 1, ultima):
            im = doc[i].render(scale=dpi / 72, grayscale=gris).to_pil()
            salida.append(im.convert("L" if gris else "RGB"))
        return salida
    finally:
        doc.close()


def guardar_png(pdf: Path, dpi: int, pagina: int, destino: Path) -> Path:
    """Una página como PNG en destino (con extensión .png)."""
    destino = destino.with_suffix(".png")
    if _hay("pdftoppm"):
        subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile", "-f", str(pagina), "-l",
                        str(pagina), str(pdf), str(destino.with_suffix(""))], check=True)
    else:
        imagenes(pdf, dpi, pagina, pagina)[0].save(destino)
    return destino
