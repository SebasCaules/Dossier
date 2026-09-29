#!/usr/bin/env python3
"""Rehace las capturas del README: dos páginas de cada ejemplo, una al lado de la otra, y
la portada (las primeras páginas en abanico), en una versión para el tema claro de GitHub y
otra para el oscuro.

    python3 ejemplos/capturas/generar.py      (desde la raíz del repo; necesita pdftoppm y Pillow)
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter

AQUI = Path(__file__).resolve().parent
EJEMPLOS = AQUI.parent
DPI = 110
DETALLE = (0.0, 0.17, 0.57, 0.74)  # recorte (x0, y0, x1, y1) que se amplía cuando el ejemplo tiene una sola página

# Portada: la primera página de cada ejemplo, de izquierda a derecha (la última queda arriba).
ABANICO = ["hoja-estructuras-de-datos", "breve-git-por-dentro", "medio-campana-depositos", "breve-https"]
GIROS = [-7, -2.5, 2.5, 7]  # grados, en el sentido de las agujas del reloj

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


def portada(tema: str) -> Path:
    """Las primeras páginas en abanico sobre fondo transparente, fundidas hacia el pie. En
    el tema oscuro, las páginas van un poco más apagadas y sin sombra (no se vería)."""
    ancho, alto, paso, margen = 1800, 760, 360, 40
    lienzo = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    with tempfile.TemporaryDirectory() as tmp:
        paginas = [pagina(EJEMPLOS / n / f"{n}.pdf", 1, 72, Path(tmp)) for n in ABANICO]
    for i, (hoja, giro) in enumerate(zip(paginas, GIROS)):
        if tema == "oscura":
            hoja = ImageEnhance.Brightness(hoja).enhance(0.88)
        borde = (208, 215, 222) if tema == "clara" else (61, 68, 77)
        ImageDraw.Draw(hoja).rectangle([0, 0, hoja.width - 1, hoja.height - 1], outline=borde, width=2)
        capa = Image.new("RGBA", (hoja.width + 2 * margen, hoja.height + 2 * margen), (0, 0, 0, 0))
        if tema == "clara":
            sombra = Image.new("RGBA", capa.size, (0, 0, 0, 0))
            ImageDraw.Draw(sombra).rectangle([margen, margen + 8, margen + hoja.width, margen + hoja.height + 8],
                                             fill=(22, 35, 58, 70))
            capa = Image.alpha_composite(capa, sombra.filter(ImageFilter.GaussianBlur(16)))
        capa.paste(hoja, (margen, margen))
        capa = capa.rotate(-giro, resample=Image.BICUBIC, expand=True)
        centro = ancho // 2 + int((i - 1.5) * paso)
        arriba = 30 + int(abs(i - 1.5) * 26)  # las de los costados, más abajo
        lienzo.alpha_composite(capa, (centro - capa.width // 2, arriba - margen))
    desde = int(alto * 0.55)  # el fundido empieza pasada la mitad
    fundido = Image.new("L", (1, alto), 255)
    for y in range(desde, alto):
        fundido.putpixel((0, y), int(255 * (1 - (y - desde) / (alto - desde)) ** 1.6))
    lienzo.putalpha(ImageChops.multiply(lienzo.getchannel("A"), fundido.resize((ancho, alto))))
    # WebP y no PNG: con 256 colores el fundido sale en franjas, y sin reducirlos pesa 700 KB.
    destino = AQUI / f"portada-{tema}.webp"
    lienzo.resize((1500, round(alto * 1500 / ancho)), Image.LANCZOS).save(destino, quality=88, method=6)
    return destino


if __name__ == "__main__":
    for nombre, paginas in PAGINAS.items():
        print(captura(nombre, paginas).relative_to(EJEMPLOS.parent), file=sys.stdout)
    for tema in ("clara", "oscura"):
        print(portada(tema).relative_to(EJEMPLOS.parent), file=sys.stdout)
