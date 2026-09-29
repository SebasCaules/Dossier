#!/usr/bin/env python3
"""Captura una página web o un HTML local para usarla como imagen del documento.

    python3 capturar.py <url|archivo.html> <salida.png> [--ancho 1440] [--alto 900]
        [--escala 2] [--selector CSS] [--esperar 800] [--completa]

--selector recorta la captura a un elemento (una vista, un gráfico, una tabla), que
casi siempre se lee mejor que la pantalla entera. --escala 2 da nitidez de impresión.
Necesita Playwright con Chromium (pip install playwright && playwright install chromium).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("origen")
    ap.add_argument("salida")
    ap.add_argument("--ancho", type=int, default=1440)
    ap.add_argument("--alto", type=int, default=900)
    ap.add_argument("--escala", type=float, default=2)
    ap.add_argument("--selector")
    ap.add_argument("--esperar", type=int, default=800, help="milisegundos después de cargar")
    ap.add_argument("--completa", action="store_true", help="toda la página, no solo la ventana")
    a = ap.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _entorno
    _entorno.usar()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Falta Playwright: pip install playwright && playwright install chromium", file=sys.stderr)
        return 2

    origen = a.origen
    if not origen.startswith(("http://", "https://", "file://")):
        origen = Path(origen).expanduser().resolve().as_uri()
    salida = Path(a.salida).expanduser().resolve()
    salida.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        navegador = pw.chromium.launch()
        pagina = navegador.new_page(viewport={"width": a.ancho, "height": a.alto},
                                    device_scale_factor=a.escala)
        pagina.goto(origen, wait_until="networkidle")
        pagina.wait_for_timeout(a.esperar)
        if a.selector:
            pagina.locator(a.selector).first.screenshot(path=str(salida))
        else:
            pagina.screenshot(path=str(salida), full_page=a.completa)
        navegador.close()
    print(salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
