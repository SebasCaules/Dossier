#!/usr/bin/env python3
"""Crea la carpeta de un documento de /dossier a partir de la plantilla de la skill.

    python3 nuevo.py <carpeta> [--perfil "medio +imagenes -texto temas=6"]
                     [--titulo "Título completo"] [--corto "Título corto"] [--autor "Autor"]

Deja en <carpeta>: <nombre>.tex (nombre = el de la carpeta), dossier.sty,
estilo_graficos.py, graficos.py (sin gráficos activos), README.md y las subcarpetas fig/
y capturas/. En fig/ quedan las figuras de ejemplo que cita la plantilla, así la carpeta
compila desde el primer momento; se reemplazan con las del documento.

--perfil lleva los mismos parámetros que /dossier (ver perfil.py). Con ellos elige la
plantilla (una hoja, una hoja de consulta si es hoja con items=N, o un documento de
varias páginas), el índice que conviene al largo y la opción de impresión, y deja
escritos en el .tex y en el README el perfil con sus ajustes (temas=, items=, paginas=),
el pedido tal como llegó y la línea exacta de medir.py. Nunca pisa un archivo que ya
existe: si la carpeta ya tiene un documento, lo informa y sale con 1.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PLANTILLA = AQUI.parent / "plantilla"
sys.path.insert(0, str(AQUI))
sys.dont_write_bytecode = True
from perfil import calcular, parsear  # noqa: E402

NOMBRES = {"mas": "más", "menos": "menos", "normal": "normal"}
# Figuras de ejemplo que citan las plantillas, con la función de graficos.py que las dibuja.
EJEMPLOS = {"fig/f1_ejemplo.pdf": "ejemplo", "fig/f2_categorias.pdf": "ejemplo_categorias"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("--perfil", default="", help="parámetros de /dossier, entre comillas")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--corto", default="")
    ap.add_argument("--autor", default="")
    # «--perfil -imagenes» confunde a argparse (toma el valor por una opción): se separa antes.
    argv, perfil_txt = [], ""
    resto = sys.argv[1:]
    while resto:
        arg = resto.pop(0)
        if arg == "--perfil" and resto:
            perfil_txt = resto.pop(0)
        elif arg.startswith("--perfil="):
            perfil_txt = arg.split("=", 1)[1]
        else:
            argv.append(arg)
    a = ap.parse_args(argv)

    parametros, avisos, _, dudas = parsear(perfil_txt.split())
    if dudas:
        # No se crea nada con un parámetro dudoso: primero hay que preguntar.
        print(json.dumps({"ok": False, "error": "parámetros dudosos",
                          "dudas": [{"escrito": c, "opciones": o} for c, o in dudas]},
                         ensure_ascii=False))
        return 1
    perfil = calcular(parametros)

    carpeta = Path(a.carpeta).expanduser().resolve()
    nombre = re.sub(r"[^\w-]+", "-", carpeta.name).strip("-").lower() or "documento"
    tex = carpeta / f"{nombre}.tex"
    p = perfil["parametros"]
    if perfil["paginas"] == 1:  # con items=N, la hoja es de consulta: una fila por ítem
        modelo = "consulta.tex" if p["items"] else "hoja.tex"
    else:
        modelo = "doc.tex"
    copias = {
        PLANTILLA / modelo: tex,
        PLANTILLA / "dossier.sty": carpeta / "dossier.sty",
        PLANTILLA / "estilo_graficos.py": carpeta / "estilo_graficos.py",
        PLANTILLA / "graficos.py": carpeta / "graficos.py",
        PLANTILLA / "README.md": carpeta / "README.md",
    }
    existentes = [str(d) for d in copias.values() if d.exists()]
    if existentes:
        print(json.dumps({"ok": False, "error": "ya existen", "archivos": existentes}, ensure_ascii=False))
        return 1

    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "fig").mkdir(exist_ok=True)
    (carpeta / "capturas").mkdir(exist_ok=True)
    for origen, destino in copias.items():
        shutil.copyfile(origen, destino)

    ajustes = [f"{k}={p[k]}" for k in ("temas", "items", "paginas") if p[k]]
    resumen = (f"{p['largo']} — texto {NOMBRES[p['texto']]} — imágenes {NOMBRES[p['imagenes']]}"
               f" — lector {p['lector'] or 'según el pedido'} — "
               f"formato {'impresión' if p['salida'] == 'impresion' else 'digital'}"
               + "".join(f" — {x}" for x in ajustes))
    pedido = f"«{' '.join(perfil_txt.split())}»" if perfil_txt.strip() else "sin parámetros"
    medir = perfil["medir_linea"].replace("<doc>", nombre)

    texto = tex.read_text(encoding="utf-8")
    primera, _, cuerpo = texto.partition("\n")
    if a.titulo:
        primera = primera.replace("TÍTULO", a.titulo, 1)
    texto = f"{primera}\n% Perfil: {resumen}\n% Pedido: {pedido}\n% Medir:  {medir}\n{cuerpo}"
    texto = re.sub(r"latexmk -lualatex \S+\.tex", f"latexmk -lualatex {nombre}.tex", texto)
    if a.titulo or a.corto or a.autor:
        texto = texto.replace(
            r"\documento{Proyecto · Título corto}{Título completo del documento}{Autor o equipo}",
            r"\documento{%s}{%s}{%s}" % (a.corto or a.titulo or "Título corto",
                                        a.titulo or "Título completo", a.autor or "Autor"),
        )
    if p["salida"] == "impresion":
        texto = texto.replace(r"\usepackage{dossier}", r"\usepackage[impresion]{dossier}")
    if perfil["indice"] == r"\indicelista":
        texto = re.sub(r"\\indice\b", r"\\indicelista", texto)
    elif perfil["indice"] is None and perfil["paginas"] > 1:
        texto = re.sub(r"^\\indice\b", lambda _: "% \\indice: con lector=estudio en breve, el mapa del tema "
                       "lo reemplaza (componentes.md, «Mapa del tema»)", texto, flags=re.M)
    tex.write_text(texto, encoding="utf-8")

    # Las figuras de ejemplo, una sola vez: graficos.py queda sin llamadas activas.
    funciones = [f for ruta, f in EJEMPLOS.items() if ruta in texto]
    if funciones:
        r = subprocess.run([sys.executable, "-B", "-c", "import graficos as g; "
                            + "; ".join(f"g.{f}()" for f in funciones)],
                           cwd=carpeta, capture_output=True, text=True,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if r.returncode:
            error = (r.stderr.strip().splitlines() or ["sin detalle"])[-1]
            avisos.append(f"no se pudieron dibujar las figuras de ejemplo ({error}): el .tex no "
                          "compila hasta reemplazar sus \\figura.")

    readme = carpeta / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8")
        .replace("NOMBRE", nombre)
        .replace("FECHA", date.today().strftime("%d/%m/%Y"))
        .replace("PERFIL", f"{resumen} (pedido: {pedido})")
        .replace("MEDIR", medir),
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "carpeta": str(carpeta), "tex": str(tex), "plantilla": modelo,
                      "pdf": str(tex.with_suffix(".pdf")), "perfil": resumen, "pedido": pedido,
                      "paginas": perfil["paginas"], "medir": medir, "avisos": avisos + perfil["avisos"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
