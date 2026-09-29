#!/usr/bin/env python3
"""Renderiza cada página del PDF para mirarla antes de entregar.

    python3 revisar.py dossiers/pdfs/doc.pdf [--dpi 100] [--hoja-dpi 40] [--paginas 2,5-7]
                                            [--lector equipo|estudio|entrega|cliente]

También acepta el .tex (revisa su PDF). Escribe en _build/revision/ de la carpeta del
documento (para un PDF de dossiers/pdfs/, la de dossiers/<nombre>/; si no, la del PDF):
  - pagina-NN.png, una por página, a una resolución que se lee (para Read);
  - hoja.png, todas las páginas juntas, para ver de un vistazo el ritmo, los blancos
    grandes y las páginas que son pared de texto.
Imprime las rutas y la lista de lo que hay que buscar en cada página; con --lector, suma
lo que ese lector necesita.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import _carpetas  # noqa: E402
import _entorno  # noqa: E402
import _pdf  # noqa: E402

QUE_MIRAR = """Qué buscar en cada página:
  - tablas, listas o párrafos cortados entre dos páginas; títulos solos al pie;
  - etiquetas de gráficos que se pisan, texto que se sale de una caja o del margen;
  - cajas y avisos pegados al texto; blancos grandes sin motivo (medir.py avisa desde el 40 %
    y anota desde el 15 %);
  - capturas ilegibles al tamaño impreso; figuras sin pie o con un pie que no dice nada;
  - enlaces que no se distinguen del texto; cifras sin su fuente;
  - ¿cada destacado está explicado en el pie?
  - ¿las cifras del pie coinciden con la figura?
  - ¿el pie de cada diagrama dice su mensaje, no solo cómo está dispuesto?
  - ¿algún diagrama es una lista en cajas?
  - ¿la última página tiene sentido sola?"""
POR_LECTOR = {
    "cliente": ["¿cada término se entiende sin la fuente?",
                "¿el mismo término significa siempre lo mismo?",
                "¿está todo lo que la fuente le pide al cliente?"],
    "estudio": ["¿cada pregunta que muestra la portada se responde?"],
}


def plural(n: int, uno: str, varios: str) -> str:
    """La forma que va con n: plural(1, 'página', 'páginas') es «página»."""
    return uno if n == 1 else varios


def rango(texto: str, total: int) -> list[int]:
    if not texto:
        return list(range(1, total + 1))
    paginas: set[int] = set()
    for parte in texto.split(","):
        if "-" in parte:
            a, b = parte.split("-", 1)
            paginas.update(range(int(a), int(b) + 1))
        elif parte.strip():
            paginas.add(int(parte))
    return sorted(p for p in paginas if 1 <= p <= total)


def total_paginas(pdf: Path) -> int:
    return _pdf.paginas(pdf)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="el PDF o el .tex del documento")
    ap.add_argument("--dpi", type=int, default=100)
    ap.add_argument("--hoja-dpi", type=int, default=40)
    ap.add_argument("--paginas", default="", help="por ejemplo 2,5-7 (por defecto, todas)")
    ap.add_argument("--lector", choices=["equipo", "estudio", "entrega", "cliente"],
                    help="suma a la lista lo que ese lector necesita")
    a = ap.parse_args()
    _entorno.usar()

    pdf = Path(a.pdf).expanduser().resolve()
    if pdf.suffix.lower() == ".tex":
        carpeta, pdf = pdf.parent, _carpetas.pdf_de(pdf)
    else:
        carpeta = _carpetas.carpeta_de(pdf)
    if not pdf.exists():
        print(f"No existe {pdf}", file=sys.stderr)
        return 2
    salida = carpeta / "_build" / "revision"
    salida.mkdir(parents=True, exist_ok=True)
    total = total_paginas(pdf)
    elegidas = rango(a.paginas, total)
    # Con --paginas solo se rehacen esas: las demás quedan de la pasada anterior.
    viejas = salida.glob("*.png") if not a.paginas else [salida / f"pagina-{n:02d}.png" for n in elegidas]
    for viejo in viejas:
        if viejo.exists():
            viejo.unlink()
    rutas = []
    for n in elegidas:
        rutas.append(_pdf.guardar_png(pdf, a.dpi, n, salida / f"pagina-{n:02d}"))

    try:
        from PIL import Image

        imagenes = _pdf.imagenes(pdf, a.hoja_dpi)
        ancho, alto = imagenes[0].size
        columnas = min(5, len(imagenes))
        filas = (len(imagenes) + columnas - 1) // columnas
        margen = 8
        hoja = Image.new("RGB", (columnas * (ancho + margen) + margen, filas * (alto + margen) + margen), "#9aa0a6")
        for k, im in enumerate(imagenes):
            hoja.paste(im, (margen + (k % columnas) * (ancho + margen), margen + (k // columnas) * (alto + margen)))
        hoja.save(salida / "hoja.png")
        print(f"Hoja con {plural(len(imagenes), 'la única página', f'las {len(imagenes)} páginas')}: {salida / 'hoja.png'}")
    except ImportError:
        print("Sin Pillow no hay hoja de contacto (python3 dependencias.py instalar lo trae).")
    print("Páginas para leer una por una:")
    for r in rutas:
        print(f"  {r}")
    print(QUE_MIRAR)
    if a.lector in POR_LECTOR:
        print(f"Con lector={a.lector}:")
        for pregunta in POR_LECTOR[a.lector]:
            print(f"  - {pregunta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
