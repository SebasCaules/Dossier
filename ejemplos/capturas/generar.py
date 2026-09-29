#!/usr/bin/env python3
"""Rehace las capturas del README: dos páginas de cada ejemplo, una al lado de la otra.

    python3 ejemplos/capturas/generar.py      (desde la raíz del repo; necesita pdftoppm y Pillow)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

AQUI = Path(__file__).resolve().parent
EJEMPLOS = AQUI.parent
DPI = 110
DETALLE = (0.0, 0.17, 0.57, 0.74)  # recorte (x0, y0, x1, y1) que se amplía cuando el ejemplo tiene una sola página

# ejemplo: páginas que se muestran (la hoja muestra su única página y un detalle ampliado)
PAGINAS = {
    "hoja-estructuras-de-datos": [1],
    "breve-https": [1, 2],
    "breve-git-por-dentro": [1, 3],
    "medio-campana-depositos": [1, 2],
}


def pagina(pdf: Path, n: int, dpi: int, carpeta: Path) -> Image.Image:
    salida = carpeta / f"p{n}-{dpi}"
    subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(n), "-l", str(n), "-png", "-singlefile",
                    str(pdf), str(salida)], check=True)
    return Image.open(f"{salida}.png").convert("RGB")


def con_borde(img: Image.Image) -> Image.Image:
    ImageDraw.Draw(img).rectangle([0, 0, img.width - 1, img.height - 1], outline=(208, 215, 222))
    return img


def captura(nombre: str, paginas: list[int]) -> Path:
    pdf = EJEMPLOS / nombre / f"{nombre}.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        piezas = [con_borde(pagina(pdf, n, DPI, tmp)) for n in paginas]
        if len(piezas) == 1:  # una hoja: la página y, al lado, un detalle al doble de resolución
            grande = pagina(pdf, paginas[0], DPI * 2, tmp)
            x0, y0, x1, y1 = DETALLE
            detalle = grande.crop((int(grande.width * x0), int(grande.height * y0),
                                   int(grande.width * x1), int(grande.height * y1)))
            detalle = detalle.resize(piezas[0].size, Image.LANCZOS)
            piezas.append(con_borde(detalle))
        sep = 28
        alto = max(p.height for p in piezas)
        lienzo = Image.new("RGB", (sum(p.width for p in piezas) + sep * (len(piezas) - 1), alto), "white")
        x = 0
        for p in piezas:
            lienzo.paste(p, (x, (alto - p.height) // 2))
            x += p.width + sep
    destino = AQUI / f"{nombre}.png"
    lienzo.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(destino, optimize=True)
    return destino


if __name__ == "__main__":
    for nombre, paginas in PAGINAS.items():
        print(captura(nombre, paginas).relative_to(EJEMPLOS.parent), file=sys.stdout)
