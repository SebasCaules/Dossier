#!/usr/bin/env python3
"""Compila un documento de /dossier y mide lo que fijó su perfil: páginas, texto, piezas
visuales y problemas de maquetación que se ven en el papel.

    python3 medir.py doc.tex [--paginas N] [--paginas-min N] [--paginas-texto M]
                             [--paginas-texto-min m] [--parte-texto F]
                             [--visuales-min V] [--visuales-max W] [--densa 550]
                             [--lector equipo|estudio|entrega|cliente]
                             [--sin-compilar] [--pdf ruta.pdf] [--outdir DIR] [--json]

Los números salen de perfil.py, que los calcula a partir de los parámetros del pedido.

Compila con `latexmk -lualatex` (los auxiliares van a _build/ y el PDF queda junto al
.tex) y después mide, con los \\input y \\include ya reemplazados por su contenido:

  - páginas del PDF, contra --paginas; con menos de --paginas-min (el mínimo del largo),
    avisa;
  - páginas de texto: palabras de prosa del .tex (títulos, párrafos, listas, tablas,
    pies, avisos, repaso, glosario y notas de \\cifra; no el código, ni el texto de
    gráficos y diagramas, ni la matemática destacada; cada fórmula en línea cuenta como
    una palabra, y un \\cod{...}, también) divididas por 800, que es lo que entra en una
    página A4 llena a 10 pt. Contra --paginas-texto, con el desglose por bloque (texto,
    tablas, pies, repaso, glosario, avisos, cifras, portada); si pasa el tope, dice qué
    bloque creció desde la medición anterior, que queda en _build/<doc>.prosa.json;
  - con --parte-texto, qué parte de las páginas reales ocupa esa prosa: si pasa la del
    perfil por más de 8 puntos, el documento quedó más corto con el mismo texto (aviso);
  - piezas visuales del .tex (figuras, capturas y diagramas; no tablas ni cifras, ni el
    mapa del tema: un dibujo con 3 o más \\hyperref es navegación), contra
    --visuales-max; el mínimo (--visuales-min) solo avisa, porque se completa con material
    real o no se completa;
  - imágenes que parecen una página de texto (la foto de una hoja de otro PDF) y páginas
    de otros PDF incluidas como figura: son texto metido como imagen, y no cuentan;
  - un piso de texto (--paginas-texto-min), que solo avisa: es el de «más texto»;
  - palabras por página en la letra del cuerpo (sin monoespaciada, fórmulas, letra menor
    que \\small, encabezado ni pie), y las páginas que pasan de --densa (paredes de texto);
  - blancos: una hoja que usa menos del 85 %, una última página que usa menos del 35 %,
    páginas con más del 40 % en blanco al pie (aviso) o entre 15 y 40 % (nota), huecos de
    más del 20 % en el medio de una página (sin contar la zona de notas al pie) y páginas
    que terminan en «:» (lo anunciado quedó en la siguiente);
  - del log: texto que se sale del margen (más de 1 pt), caracteres que la fuente no
    tiene, referencias y enlaces rotos, fuentes sustituidas;
  - aparte, las palabras dentro de dibujos TikZ (con las listas de \\foreach): no cuentan
    como texto, pero un diagrama con más de 60 palabras, o un nodo con más de 12, es texto
    con cajas;
  - en la prosa, «~» antes de un número (en LaTeX es un espacio duro, no «aproximadamente»);
    con el entorno referencias, las siglas que ningún \\fuente cita; con --lector estudio,
    las secciones sin repaso.

Sale con 0 si todo está en regla, con 1 si hay un límite superado o un problema, y con
2 si el documento no compila (imprime el error con su línea). Los AVISO y las Nota no
cambian la salida.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.dont_write_bytecode = True
import _entorno  # noqa: E402
import _pdf  # noqa: E402

PALABRAS_POR_PAGINA = 800
ALTO_CAJA_CM = 26.5  # caja de texto de dossier.sty: de 16 mm a 281 mm desde arriba

# Comandos cuyo argumento no es prosa: (argumentos obligatorios que se descartan).
# Los opcionales [..] de estos comandos también se descartan. Los que no están acá
# pierden el nombre y conservan el contenido (\textbf{..}, \section{..}, \ojo[..]{..}).
DESCARTAR = {
    "includegraphics": 1, "label": 1, "ref": 1, "pageref": 1, "nameref": 1, "autoref": 1,
    "ver": 1, "hitos": 1, "proceso": 1, "cifra": 2, "fuente": 1, "chip": 0,
    "vspace": 1, "hspace": 1, "vskip": 0, "hskip": 0, "rule": 2, "phantomsection": 0,
    "definecolor": 3, "colorlet": 2, "color": 1, "textcolor": 1, "documento": 3,
    "href": 1, "enlace": 1, "url": 1, "hyperlink": 1, "hypertarget": 1, "hyperref": 0,
    "captionof": 1, "captionsetup": 1, "setlength": 2, "addtolength": 2, "setcounter": 2,
    "fontsize": 2, "raisebox": 1, "scalebox": 1, "resizebox": 2, "parbox": 1,
    "figura": 1, "captura": 1, "input": 1, "include": 1, "thispagestyle": 1,
    "pagestyle": 1, "pdfbookmark": 2, "addcontentsline": 3, "newcommand": 2, "needspace": 1,
    "renewcommand": 2, "tikzset": 1, "usetikzlibrary": 1, "cite": 1, "footnotemark": 0,
    "grupo": 1, "arriba": 2, "carril": 2,
    # código y tablas
    "lstinputlisting": 1, "lstset": 1, "lstdefinestyle": 2, "addlinespace": 0,
    "multicolumn": 2, "multirow": 2, "toprule": 0, "midrule": 0, "bottomrule": 0,
    "specialrule": 3, "rowcolor": 1, "cellcolor": 1, "arrayrulecolor": 1,
}
# Entornos: argumentos obligatorios de \begin{..} que no son prosa.
ARGS_ENTORNO = {
    "tabularx": 2, "tabular": 1, "tabular*": 2, "multicols": 1, "minipage": 1,
    "cifras": 0, "tcbraster": 0, "center": 0, "itemize": 0, "enumerate": 0,
    "glosario": 0, "adjustbox": 1, "columna": 1, "referencias": 0, "longtable": 1,
    "figure": 0, "table": 0, "figure*": 0, "table*": 0, "description": 0,
}
# Entornos que se descartan enteros: dibujos y código, no texto corrido.
SIN_PROSA = ("tikzpicture", "tcbraster", "lstlisting", "codigo", "verbatim", "Verbatim", "minted")
# Matemática destacada: no cuenta (con y sin *).
FORMULA_EN_LINEA = r"(?<!\\)\$.+?(?<!\\)\$|\\\(.*?\\\)"
MATE_DESTACADA = ("equation", "align", "gather", "multline", "flalign", "alignat", "eqnarray",
                  "displaymath")
TABLAS = ("tabularx", "tabular", "tabular*", "longtable")

PALABRA = re.compile(r"[^\W_]+(?:[.,'’/-][^\W_]+)*")
# Letra que no es la del cuerpo, por el nombre de la fuente en el PDF.
MONO = re.compile(r"Menlo|Mono|Courier|Consol|Monaco|Inconsolata|Code", re.I)
FORMULAS = re.compile(r"^(?:CM|LM|MSBM|MSAM|EUFM|EUSM|RSFS|STIX|XITS)|Math", )
SMALL = {10: 9.0, 11: 10.0, 12: 10.95}  # \small según el tamaño de la clase, en pt


def plural(n: int, uno: str, varios: str) -> str:
    """La forma que va con n: plural(1, 'página', 'páginas') es «página»."""
    return uno if n == 1 else varios


def _saltar_grupo(s: str, i: int, abre: str, cierra: str) -> int:
    """Si en s[i:] (tras espacios) empieza un grupo abre..cierra balanceado, devuelve el
    índice siguiente a su cierre; si no, devuelve i."""
    j = i
    while j < len(s) and s[j] in " \t\n":
        j += 1
    if j >= len(s) or s[j] != abre:
        return i
    profundidad = 0
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == abre:
            profundidad += 1
        elif c == cierra:
            profundidad -= 1
            if profundidad == 0:
                return j + 1
        j += 1
    return len(s)


def _saltar_argumentos(s: str, i: int, obligatorios: int, opcionales: bool) -> int:
    while opcionales:
        k = _saltar_grupo(s, i, "[", "]")
        if k == i:
            break
        i = k
    for _ in range(obligatorios):
        k = _saltar_grupo(s, i, "{", "}")
        if k == i:
            break
        i = k
        while opcionales:  # \parbox[t]{..}[..]: opcionales entre obligatorios
            k2 = _saltar_grupo(s, i, "[", "]")
            if k2 == i:
                break
            i = k2
    return i


def _sin_comentarios(tex: str) -> str:
    return "\n".join(re.split(r"(?<!\\)%", ln, maxsplit=1)[0] for ln in tex.splitlines())


def _cuerpo(tex: str) -> str:
    if r"\begin{document}" in tex:
        tex = tex.split(r"\begin{document}", 1)[1]
    return tex.split(r"\end{document}", 1)[0]


ENTRADA = re.compile(r"\\(?:input|include)\s*\{([^{}]+)\}")


def expandir(ruta: Path, base: Path | None = None, profundidad: int = 0) -> list[tuple[str, Path, int]]:
    """Las líneas del .tex sin comentarios, con cada \\input{x} o \\include{x} reemplazado
    por las líneas de x (relativo a la carpeta del .tex principal; .tex si falta). Cada
    línea lleva su archivo y su número, para señalar dónde está lo que se avisa."""
    base = base or ruta.parent
    lineas: list[tuple[str, Path, int]] = []
    texto = ruta.read_text(encoding="utf-8", errors="replace")
    for n, ln in enumerate(texto.splitlines(), 1):
        ln = re.split(r"(?<!\\)%", ln, maxsplit=1)[0]
        desde = 0
        for m in ENTRADA.finditer(ln):
            nombre = m.group(1).strip()
            archivo = base / nombre
            if not archivo.is_file():
                archivo = base / f"{nombre}.tex"
            if profundidad >= 8 or not archivo.is_file():
                continue
            lineas.append((ln[desde:m.start()], ruta, n))
            lineas.extend(expandir(archivo, base, profundidad + 1))
            desde = m.end()
        lineas.append((ln[desde:], ruta, n))
    return lineas


def _preparar(tex: str) -> str:
    """El cuerpo listo para contar: sin comentarios, sin dibujos ni código, sin matemática
    destacada y con cada fórmula en línea reducida a una palabra (cero si está en una tabla)."""
    tex = _cuerpo(_sin_comentarios(tex))
    for entorno in SIN_PROSA + MATE_DESTACADA:
        e = re.escape(entorno)
        tex = re.sub(r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (e, e), " ", tex, flags=re.S)
    # \\ y \\[2pt] antes que la matemática: «\\[» no es el comienzo de una fórmula.
    tex = re.sub(r"\\\\\*?(\[[^\]]*\])?", " ", tex)
    tex = re.sub(r"\$\$.*?\$\$|\\\[.*?\\\]", " ", tex, flags=re.S)
    # En una tabla, la fórmula es el dato de la celda (un formulario), no una palabra de la
    # oración: no cuenta. En la prosa cuenta como una palabra.
    tex = re.sub(r"\\begin\{(tabularx|tabular\*?|longtable)\}.*?\\end\{\1\}",
                 lambda m: re.sub(FORMULA_EN_LINEA, " ", m.group(0), flags=re.S), tex, flags=re.S)
    return re.sub(FORMULA_EN_LINEA, " fórmula ", tex, flags=re.S)


def _texto_prosa(tex: str) -> str:
    """El texto que queda de un fragmento ya preparado, sin comandos ni sus argumentos
    técnicos."""
    salida: list[str] = []
    i = 0
    comando = re.compile(r"\\([A-Za-z@]+)\*?")
    while i < len(tex):
        if tex[i] != "\\":
            salida.append(tex[i])
            i += 1
            continue
        m = comando.match(tex, i)
        if not m:  # símbolo de control: \, \% \& \_ ...
            salida.append(" " if tex[i + 1:i + 2] in (",", ";", ":", "!", " ") else tex[i + 1:i + 2])
            i += 2
            continue
        nombre, i = m.group(1), m.end()
        if nombre in ("begin", "end"):
            fin = _saltar_grupo(tex, i, "{", "}")
            entorno = tex[i:fin].strip(" {}")
            i = fin
            if nombre == "begin" and entorno in ARGS_ENTORNO:
                i = _saltar_argumentos(tex, i, ARGS_ENTORNO[entorno], opcionales=True)
        elif nombre == "cod":  # un identificador es una palabra, tenga los _ que tenga
            i = _saltar_argumentos(tex, i, 1, opcionales=True)
            salida.append(" código ")
        elif nombre in ("verb", "lstinline"):
            k = _saltar_argumentos(tex, i, 0, opcionales=True)
            if k < len(tex) and tex[k] == "{":
                i = _saltar_grupo(tex, k, "{", "}")
            elif k < len(tex):
                cierre = tex.find(tex[k], k + 1)
                i = len(tex) if cierre < 0 else cierre + 1
            salida.append(" código ")
        elif nombre == "cmidrule":  # \cmidrule[..](lr){2-3}
            i = _saltar_argumentos(tex, i, 0, opcionales=True)
            i = _saltar_grupo(tex, i, "(", ")")
            i = _saltar_argumentos(tex, i, 1, opcionales=False)
        elif nombre in DESCARTAR:
            i = _saltar_argumentos(tex, i, DESCARTAR[nombre], opcionales=True)
        else:  # \hyphenpenalty=10000 no es una palabra
            asignacion = re.match(r"\s*=\s*-?[\d.]+\s*(?:pt|cm|mm|em|ex|bp|sp|in)?", tex[i:])
            if asignacion:
                i += asignacion.end()
        salida.append(" ")
    return re.sub(r"[{}&~]", " ", "".join(salida))


def _contar(preparado: str) -> int:
    return len(PALABRA.findall(_texto_prosa(preparado)))


def palabras_prosa(tex: str) -> int:
    """Estimación de las palabras que el lector lee como texto corrido."""
    return _contar(_preparar(tex))


def _tramos_entorno(s: str, entornos: tuple[str, ...]) -> list[tuple[int, int]]:
    tramos = []
    for e in entornos:
        tramos += [m.span() for m in re.finditer(r"\\begin\{%s\}.*?\\end\{%s\}" % (re.escape(e), re.escape(e)), s, re.S)]
    return tramos


def _tramos_comando(s: str, nombres: tuple[str, ...], obligatorios: int) -> list[tuple[int, int]]:
    tramos = []
    for m in re.finditer(r"\\(%s)\b(\*?)" % "|".join(nombres), s):
        n = obligatorios - 1 if (m.group(1) == "portada" and m.group(2)) else obligatorios
        tramos.append((m.start(), _saltar_argumentos(s, m.end(), n, opcionales=True)))
    return tramos


BLOQUES = ("texto", "tablas", "pies", "repaso", "glosario", "avisos", "cifras", "portada")


def desglose_prosa(tex: str) -> dict[str, int]:
    """Las palabras de prosa por bloque. Suman el total que se compara con el tope."""
    s = _preparar(tex)
    cuenta = dict.fromkeys(BLOQUES, 0)

    def sacar(bloque: str, tramos: list[tuple[int, int]]) -> None:
        nonlocal s
        elegidos: list[tuple[int, int]] = []
        for ini, fin in sorted(tramos):  # uno dentro de otro ya cuenta con el de afuera
            if not elegidos or ini >= elegidos[-1][1]:
                elegidos.append((ini, fin))
        for ini, fin in reversed(elegidos):
            cuenta[bloque] += _contar(s[ini:fin])
            s = s[:ini] + " " + s[fin:]

    sacar("repaso", _tramos_entorno(s, ("repaso",)))
    sacar("glosario", _tramos_entorno(s, ("glosario",)))
    sacar("avisos", _tramos_comando(s, ("ojo", "nota"), 1))
    sacar("tablas", _tramos_entorno(s, TABLAS))
    sacar("pies", _tramos_comando(s, ("figura", "captura"), 2))
    sacar("pies", _tramos_comando(s, ("captionof",), 2))
    sacar("pies", _tramos_comando(s, ("caption",), 1))
    sacar("pies", [(m.end(), _saltar_grupo(s, m.end(), "[", "]"))
                   for m in re.finditer(r"\\begin\{bloque\}", s)])
    sacar("cifras", _tramos_comando(s, ("cifra",), 3))
    sacar("portada", _tramos_comando(s, ("portada",), 4) + _tramos_comando(s, ("datosentrega",), 4))
    cuenta["texto"] = _contar(s)
    return cuenta


def _textos_de_nodos(dibujo: str) -> list[tuple[int, str]]:
    """El texto {..} de cada nodo de un dibujo TikZ, con su posición."""
    textos = []
    for m in re.finditer(r"\bnode\b", dibujo):
        i = m.end()
        while True:  # saltar opciones [..], nombre (..) y «at (..)» hasta el texto {..}
            j = i
            while j < len(dibujo) and dibujo[j] in " \t\n":
                j += 1
            if j < len(dibujo) and dibujo[j] in "[(":
                i = _saltar_grupo(dibujo, j, dibujo[j], "]" if dibujo[j] == "[" else ")")
                continue
            if dibujo.startswith("at", j) and not dibujo[j + 2:j + 3].isalpha():
                i = j + 2
                continue
            break
        if j < len(dibujo) and dibujo[j] == "{":
            fin = _saltar_grupo(dibujo, j, "{", "}")
            textos.append((j, dibujo[j + 1:fin - 1]))
    return textos


def _partir(lista: str, separador: str) -> list[str]:
    """Parte una lista de \\foreach por un separador que esté fuera de llaves."""
    partes, actual, profundidad = [], [], 0
    for c in lista:
        if c == "{":
            profundidad += 1
        elif c == "}":
            profundidad -= 1
        if c == separador and profundidad == 0:
            partes.append("".join(actual))
            actual = []
        else:
            actual.append(c)
    partes.append("".join(actual))
    return partes


FOREACH = re.compile(r"\\foreach\s*((?:\\[A-Za-z@]+\s*/?\s*)+)(?:\[[^\]]*\]\s*)?in\s*\{")


def _cuerpo_foreach(s: str, i: int) -> int:
    """Fin del cuerpo de un \\foreach que empieza en s[i:]: un grupo {..}, otro \\foreach
    o una instrucción hasta el «;»."""
    while i < len(s) and s[i] in " \t\n":
        i += 1
    if i < len(s) and s[i] == "{":
        return _saltar_grupo(s, i, "{", "}")
    m = FOREACH.match(s, i)
    if m:
        return _cuerpo_foreach(s, _saltar_grupo(s, m.end() - 1, "{", "}"))
    profundidad = 0
    for k in range(i, len(s)):
        if s[k] in "{[":
            profundidad += 1
        elif s[k] in "}]":
            profundidad -= 1
        elif s[k] == ";" and profundidad <= 0:
            return k + 1
    return len(s)


def _listas_foreach(dibujo: str) -> list[dict]:
    """Por cada \\foreach del dibujo: palabras de cada entrada de su lista (solo en las
    posiciones que el cuerpo escribe en un nodo; sin números sueltos ni nombres de una
    letra), cuántas entradas tiene y cuántos \\hyperref lleva el cuerpo."""
    listas = []
    for m in FOREACH.finditer(dibujo):
        variables = re.findall(r"\\([A-Za-z@]+)", m.group(1))
        fin_lista = _saltar_grupo(dibujo, m.end() - 1, "{", "}")
        lista = dibujo[m.end():fin_lista - 1]
        cuerpo = dibujo[fin_lista:_cuerpo_foreach(dibujo, fin_lista)]
        usadas = set()
        for _, texto in _textos_de_nodos(cuerpo):
            for k, v in enumerate(variables):  # la variable sobrevive si es texto del nodo
                marca = f"qqvar{chr(97 + k)}qq"
                marcado = re.sub(r"\\%s(?![A-Za-z@])" % re.escape(v), marca, texto)
                if marca in _texto_prosa(_preparar(marcado)):
                    usadas.add(k)
        entradas = [e for e in _partir(lista, ",") if e.strip()]
        por_entrada = []
        for entrada in entradas:
            total = 0
            for k, item in enumerate(_partir(entrada, "/")):
                item = item.strip()
                if item.startswith("{") and item.endswith("}"):
                    item = item[1:-1].strip()
                if min(k, len(variables) - 1) not in usadas:
                    continue
                if re.fullmatch(r"-?[\d.,]+|[A-Za-z]", item):
                    continue
                total += palabras_prosa(item)
            por_entrada.append(total)
        listas.append({"pos": m.start(), "entradas": por_entrada,
                       "enlaces": len(re.findall(r"\\hyper(?:ref|link)\b", cuerpo)), "n": len(entradas)})
    return listas


def diagramas(tex: str) -> list[dict]:
    """Por cada tikzpicture del cuerpo: dónde empieza, palabras en total (nodos y listas de
    \\foreach), palabras de cada nodo que no es \\grupo ni \\fichas, y si es el mapa del
    tema (3 o más \\hyperref)."""
    tex = _sin_comentarios(tex)
    inicio = tex.find(r"\begin{document}")
    resultado = []
    for m in re.finditer(r"\\begin\{tikzpicture\}(.*?)\\end\{tikzpicture\}", tex, flags=re.S):
        if m.start() < inicio:
            continue
        dibujo = m.group(1)
        nodos = []
        for pos, texto in _textos_de_nodos(dibujo):
            nodos.append({"pos": m.start(1) + pos, "palabras": palabras_prosa(texto),
                          "contenedor": bool(re.search(r"\\(?:grupo|fichas)\b", texto)), "foreach": False})
        enlaces = len(re.findall(r"\\hyper(?:ref|link)\b", dibujo))
        for lista in _listas_foreach(dibujo):
            nodos += [{"pos": m.start(1) + lista["pos"], "palabras": w, "contenedor": False, "foreach": True}
                      for w in lista["entradas"]]
            enlaces += lista["enlaces"] * max(0, lista["n"] - 1)
        resultado.append({"pos": m.start(), "palabras": sum(n["palabras"] for n in nodos),
                          "nodos": nodos, "mapa": enlaces >= 3})
    return resultado


def palabras_diagramas(tex: str) -> list[int]:
    """Palabras en los nodos de cada tikzpicture (rótulos y cajas), una cifra por diagrama."""
    return [d["palabras"] for d in diagramas(tex)]


def piezas_visuales(tex: str, mapas: int = 0) -> dict[str, int]:
    """Cuenta en el cuerpo del .tex las piezas visuales y, aparte, tablas y filas de cifras.
    Los mapas del tema no son piezas: se descuentan de los diagramas."""
    tex = _cuerpo(_sin_comentarios(tex))
    cuenta = lambda patron: len(re.findall(patron, tex))  # noqa: E731
    figuras = cuenta(r"\\(?:figura|captura)\b")
    sueltas = cuenta(r"\\includegraphics\b")
    diagramas_ = cuenta(r"\\begin\{tikzpicture\}") - mapas + cuenta(r"\\(?:proceso|hitos)\b")
    return {"visuales": figuras + sueltas + diagramas_, "figuras": figuras + sueltas,
            "diagramas": diagramas_, "mapas": mapas, "tablas": cuenta(r"\\begin\{tabularx?\*?\}"),
            "cifras": cuenta(r"\\begin\{cifras\}")}


ARCHIVO_GRAFICO = re.compile(r"\\(?:figura|captura|includegraphics)\*?(?:\[[^\]]*\])?\{([^}]+)\}")


def paginas_de_texto(tex: str, carpeta: Path) -> list[str]:
    """Imágenes incluidas que son páginas de texto de otro documento.

    Dos señales: un PDF incluido que no está en fig/ (fig/ es de graficos.py), y una imagen
    con proporción de hoja vertical (A4 o carta: alto/ancho entre 1,25 y 1,5) cuya tinta
    se reparte en muchas franjas horizontales finas, que es como se ve un renglón tras otro.
    """
    try:
        from PIL import Image
    except ImportError:
        Image = None
    tex = _sin_comentarios(tex)
    halladas: list[str] = []
    for nombre in dict.fromkeys(ARCHIVO_GRAFICO.findall(tex)):
        ruta = carpeta / nombre
        if ruta.suffix.lower() == ".pdf":
            # Un gráfico vectorial tiene el tamaño de su dibujo; una página, el de la hoja.
            try:
                from pypdf import PdfReader
                caja = PdfReader(str(ruta)).pages[0].mediabox
                lados = sorted((float(caja.width), float(caja.height)))
            except Exception:
                continue
            for hoja in ((595.3, 841.9), (612.0, 792.0)):  # A4 y carta, en puntos
                if all(abs(x - h) / h < 0.03 for x, h in zip(lados, hoja)):
                    halladas.append(f"{nombre}: es una página entera de otro PDF")
                    break
            continue
        if Image is None or not ruta.exists():
            continue
        try:
            im = Image.open(ruta).convert("L")
        except Exception:
            continue
        ancho, alto = im.size
        if not 1.25 <= alto / ancho <= 1.5:
            continue
        chica = im.resize((300, max(1, round(300 * alto / ancho))))
        filas = []
        for y in range(chica.size[1]):
            fila = chica.crop((0, y, 300, y + 1)).point(lambda v: 255 if v < 160 else 0)
            filas.append(sum(1 for v in fila.getdata() if v) / 300)
        franjas, dentro = 0, False
        for f in filas:
            if f > 0.02 and not dentro:
                franjas, dentro = franjas + 1, True
            elif f <= 0.02:
                dentro = False
        if franjas >= 12:
            halladas.append(f"{nombre}: parece una página de texto ({franjas} renglones)")
    return halladas


def compilar(tex: Path, outdir: Path) -> tuple[bool, str]:
    cmd = ["latexmk", "-lualatex", "-interaction=nonstopmode", "-halt-on-error",
           "-file-line-error", f"-outdir={outdir}", tex.name]
    r = subprocess.run(cmd, cwd=tex.parent, capture_output=True)
    # pdflatex y lualatex escriben en la codificación que les toca: nunca decodificar estricto
    salida = (r.stdout + r.stderr).decode("utf-8", errors="replace")
    return r.returncode == 0, salida


def errores_de_compilacion(log: str) -> list[str]:
    lineas = log.splitlines()
    errores = []
    for n, ln in enumerate(lineas):
        if re.match(r"^(\S+\.(tex|sty)):\d+: ", ln) or ln.startswith("! "):
            errores.append("\n".join(lineas[n:n + 3]).strip())
    return errores[:8]


def paginas_pdf(pdf: Path) -> int:
    return _pdf.paginas(pdf)


def palabras_crudas(pdf: Path) -> list[int]:
    """Todas las palabras de cada página (pdftotext, o pypdfium2 sin poppler)."""
    return [len(PALABRA.findall(p)) for p in _pdf.textos(pdf)]


def lectura_del_pdf(pdf: Path, clase_pt: int) -> list[dict] | None:
    """Por página, con pdfplumber: palabras en la letra del cuerpo (sin monoespaciada,
    fórmulas, letra menor que \\small, encabezado ni pie), dónde empieza la zona de notas
    al pie (fracción de la caja de texto) y el último renglón del cuerpo. None si falta
    pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        return None
    umbral = SMALL.get(clase_pt, 9.0) * 72 / 72.27 - 0.3
    paginas = []
    with pdfplumber.open(str(pdf)) as doc:
        for pagina in doc.pages:
            alto, ancho = float(pagina.height), float(pagina.width)
            arriba, abajo = alto * 16 / 297, alto * 281 / 297
            try:  # el espacio entre palabras escala con la letra
                palabras = pagina.extract_words(x_tolerance_ratio=0.15, extra_attrs=["fontname", "size"])
            except TypeError:  # pdfplumber anterior a 0.11
                palabras = pagina.extract_words(x_tolerance=1.5, extra_attrs=["fontname", "size"])
            # Zona de notas: un filete corto a la izquierda con solo letra chica debajo.
            notas = None
            filetes = [(float(o["top"]), float(o["x0"]), float(o["width"]))
                       for o in pagina.lines + pagina.rects if float(o["bottom"]) - float(o["top"]) < 1.5]
            for top, x0, largo in sorted(filetes):
                if not (20 < largo < 0.6 * ancho and x0 < 0.2 * ancho and alto * 0.3 < top < abajo):
                    continue
                debajo = [w for w in palabras if float(w["top"]) > top and float(w["top"]) < abajo]
                if debajo and all(float(w["size"]) < umbral for w in debajo):
                    notas = top
                    break
            fin = notas if notas is not None else abajo
            cuerpo = [w for w in palabras
                      if float(w["bottom"]) > arriba and float(w["top"]) < fin
                      and float(w["size"]) >= umbral
                      and not MONO.search(re.sub(r"^[A-Z]{6}\+", "", w["fontname"]))
                      and not FORMULAS.search(re.sub(r"^[A-Z]{6}\+", "", w["fontname"]))]
            ultimo, fondo = "", None
            if cuerpo:
                fondo = max(float(w["bottom"]) for w in cuerpo)
                renglon = sorted((w for w in palabras if abs(float(w["bottom"]) - fondo) < 2.5
                                  and float(w["top"]) < fin), key=lambda w: float(w["x0"]))
                ultimo = " ".join(w["text"] for w in renglon)
            paginas.append({
                "cuerpo": sum(len(PALABRA.findall(w["text"])) for w in cuerpo),
                "notas": None if notas is None else (notas - arriba) / (abajo - arriba),
                "ultimo_renglon": ultimo,
                "fondo_renglon": None if fondo is None else (fondo - arriba) / (abajo - arriba),
            })
    return paginas


def llenado_por_pagina(pdf: Path, cortes: list[float | None] | None = None) -> list[tuple[float, float]]:
    """Por página: hasta dónde llega la tinta y el mayor hueco entre dos zonas con tinta,
    como fracciones de la caja de texto de dossier.sty (de 16 mm a 281 mm desde arriba; el
    encabezado queda afuera). Si la página tiene notas al pie, se mide hasta su filete."""
    try:
        imagenes = _pdf.imagenes(pdf, 30, gris=True)
    except (ImportError, OSError, subprocess.CalledProcessError):  # sin Pillow o sin con qué dibujar
        return []
    llenado = []
    for n, im in enumerate(imagenes):
        ancho, alto = im.size
        arriba, abajo = int(alto * 0.054), int(alto * 0.947)
        zona = im.crop((0, arriba, ancho, abajo)).point(lambda v: 255 if v < 200 else 0)
        filas = [zona.crop((0, y, ancho, y + 1)).getbbox() is not None for y in range(zona.size[1])]
        corte = cortes[n] if cortes and n < len(cortes) else None
        if corte is not None:  # la zona de notas no es ni hueco ni texto de la página
            filas = filas[:max(0, int(corte * len(filas)) - 1)]
        con_tinta = [y for y, hay in enumerate(filas) if hay]
        if not con_tinta:
            llenado.append((0.0, 0.0))
            continue
        hueco = actual = 0
        for y in range(con_tinta[0], con_tinta[-1] + 1):
            actual = 0 if filas[y] else actual + 1
            hueco = max(hueco, actual)
        llenado.append(((con_tinta[-1] + 1) / (abajo - arriba), hueco / (abajo - arriba)))
    return llenado


def problemas_del_log(log: str) -> list[str]:
    problemas: list[str] = []
    for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*?(?:lines? ([\d-]+)|$)", log, re.M):
        pt = float(m.group(1))
        if pt > 1.0:
            donde = (f" (líneas {m.group(2)} del .tex; si esas líneas cierran un bloque, una figura "
                     "o un \\proceso, lo que desborda está dentro de esa pieza)") if m.group(2) else ""
            problemas.append(f"texto que se sale del margen: {pt:.1f} pt{donde}".replace(".", ",", 1))
    for m in re.finditer(r"Overfull \\vbox \(([\d.]+)pt too high\)[^\n]*", log):
        if float(m.group(1)) > 1.0:
            problemas.append(f"bloque más alto que el espacio disponible: {m.group(1)} pt")
    faltan = sorted(set(re.findall(r"Missing character: There is no (\S+) \((U\+[0-9A-F]+)\) in font ([^!\n]+)", log)))
    for car, cod, fuente in faltan:
        problemas.append(f"carácter que la fuente no tiene: {car} ({cod}) en {fuente.strip()}")
    for etiqueta in sorted(set(re.findall(r"Reference `([^']+)' on page \d+ undefined", log))):
        problemas.append(f"referencia rota: {etiqueta}")
    for destino in sorted(set(re.findall(r"name\{([^}]+)\} has been referenced but does not exist", log))):
        problemas.append(f"enlace interno a un destino que no existe: {destino}")
    for forma in sorted(set(re.findall(r"Font shape `([^']+)' undefined", log))):
        problemas.append(f"fuente sustituida: {forma}")
    # El log corta las líneas largas a 79 columnas sin tocar los espacios: se junta hasta
    # «on input line N.» quitando solo los saltos.
    for texto, linea in sorted(set(re.findall(r"Package dossier Warning: (.+?) on input line (\d+)\.", log, re.S))):
        texto = texto.replace("\n", "")
        problemas.append(f"{texto} (línea {linea} del .tex)")
    return problemas


def _blanquear(texto: str, patron: str, flags: int = re.S) -> str:
    """Reemplaza lo que coincide por espacios, sin tocar los saltos de línea."""
    return re.sub(patron, lambda m: re.sub(r"[^\n]", " ", m.group(0)), texto, flags=flags)


def tildes_de_aproximado(texto: str) -> list[tuple[int, str]]:
    """«~» seguido de un dígito, precedido de espacio o «(», en la prosa del cuerpo
    (p.~3 y art.~974 son espacios duros bien puestos)."""
    inicio = texto.find(r"\begin{document}")
    original = texto  # blanquear no mueve las posiciones: lo de antes del «~» se lee aquí
    for entorno in SIN_PROSA + MATE_DESTACADA:
        e = re.escape(entorno)
        texto = _blanquear(texto, r"\\begin\{%s\*?\}.*?\\end\{%s\*?\}" % (e, e))
    texto = _blanquear(texto, r"\$\$.*?\$\$|\\\[.*?\\\]|(?<!\\)\$.+?(?<!\\)\$")
    return [(m.start(), original[m.start():m.start() + 12].split("\n")[0].strip())
            for m in re.finditer(r"~(?=\d)", texto)
            if m.start() > inicio and (original[m.start() - 1] if m.start() else "\n") in " \t\n("]


def referencias_sin_citar(tex: str) -> list[str]:
    """Siglas del entorno referencias que no aparecen en ningún \\fuente{..} del cuerpo."""
    cuerpo = _cuerpo(tex)
    m = re.search(r"\\begin\{referencias\}(.*?)\\end\{referencias\}", cuerpo, re.S)
    if not m:
        return []
    siglas = [s.strip() for s in re.findall(r"\\referencia\s*\{([^{}]*)\}", m.group(1))]
    resto = cuerpo[:m.start()] + cuerpo[m.end():]
    citas = []
    for f in re.finditer(r"\\fuente\s*", resto):
        fin = _saltar_grupo(resto, f.end(), "{", "}")
        if fin > f.end():
            citas.append(resto[f.end():fin])
    return [s for s in siglas if s and not any(re.search(r"(?<!\w)%s(?!\w)" % re.escape(s), c) for c in citas)]


def secciones_sin_repaso(tex: str) -> list[str]:
    """Títulos de las \\section sin entorno repaso (ni subsección «Para repasar»), si hay más
    de una. \\anexo cierra la sección anterior y no cuenta."""
    cuerpo = _cuerpo(tex)
    marcas = [(m.start(), m.group(1), m.end()) for m in re.finditer(r"\\(section|anexo)\b\*?", cuerpo)]
    secciones = []
    for k, (ini, tipo, fin_nombre) in enumerate(marcas):
        if tipo != "section":
            continue
        k_titulo = _saltar_argumentos(cuerpo, fin_nombre, 0, opcionales=True)
        fin_titulo = _saltar_grupo(cuerpo, k_titulo, "{", "}")
        titulo = re.sub(r"\s+", " ", _texto_prosa(cuerpo[k_titulo:fin_titulo])).strip()
        hasta = marcas[k + 1][0] if k + 1 < len(marcas) else len(cuerpo)
        tramo = cuerpo[ini:hasta]
        tiene = bool(re.search(r"\\begin\{repaso\}|\\subsection\*?\s*\{[^}]*[Rr]epas", tramo))
        secciones.append((titulo, tiene))
    if len(secciones) < 2:
        return []
    return [t for t, tiene in secciones if not tiene]


def coma(x: float, dec: int = 1) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def lista(numeros: list[int]) -> str:
    return ", ".join(map(str, numeros))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex")
    ap.add_argument("--paginas", type=int, help="máximo de páginas del PDF")
    ap.add_argument("--paginas-min", type=int, help="mínimo de páginas del largo (solo avisa)")
    ap.add_argument("--paginas-texto", type=float, help="máximo de páginas de texto (800 palabras c/u)")
    ap.add_argument("--paginas-texto-min", type=float, help="piso de páginas de texto (solo avisa)")
    ap.add_argument("--parte-texto", type=float, help="parte de las páginas que es prosa según el perfil (solo avisa)")
    ap.add_argument("--visuales-min", type=int, help="mínimo de piezas visuales")
    ap.add_argument("--visuales-max", type=int, help="máximo de piezas visuales")
    ap.add_argument("--densa", type=int, default=550, help="palabras a partir de las que una página es pared de texto")
    ap.add_argument("--lector", choices=["equipo", "estudio", "entrega", "cliente"], help="lector del perfil")
    ap.add_argument("--sin-compilar", action="store_true", help="medir el PDF que ya existe")
    ap.add_argument("--pdf", help="PDF a medir (por defecto, el del .tex)")
    ap.add_argument("--outdir", default="_build", help="carpeta de auxiliares, relativa al .tex")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    _entorno.usar()

    tex = Path(a.tex).expanduser().resolve()
    if not tex.exists():
        print(f"No existe {tex}", file=sys.stderr)
        return 2
    outdir = Path(a.outdir) if Path(a.outdir).is_absolute() else tex.parent / a.outdir
    pdf = Path(a.pdf).expanduser().resolve() if a.pdf else tex.with_suffix(".pdf")

    if not a.sin_compilar:
        ok, salida = compilar(tex, outdir)
        log_path = outdir / f"{tex.stem}.log"
        log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else salida
        if not ok:
            print(f"No compila: {tex.name}")
            for e in errores_de_compilacion(log) or salida.strip().splitlines()[-12:]:
                print("  " + e.replace("\n", "\n  "))
            return 2
        compilado = outdir / f"{tex.stem}.pdf"
        if a.pdf is None and a.outdir == "_build":
            shutil.copyfile(compilado, pdf)
        elif a.pdf is None:
            pdf = compilado
    else:
        log_path = outdir / f"{tex.stem}.log"
        log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""

    if not pdf.exists():
        print(f"No existe el PDF {pdf}", file=sys.stderr)
        return 2

    lineas = expandir(tex)
    fuente_tex = "\n".join(t for t, _, _ in lineas)

    def donde(pos: int) -> str:
        archivo, n = lineas[min(fuente_tex.count("\n", 0, pos), len(lineas) - 1)][1:]
        if archivo == tex:
            return f"línea {n} del .tex"
        try:
            return f"línea {n} de {archivo.relative_to(tex.parent)}"
        except ValueError:
            return f"línea {n} de {archivo.name}"

    paginas = paginas_pdf(pdf)
    clase = re.search(r"\\documentclass\s*\[([^\]]*)\]", fuente_tex)
    tam = re.search(r"\b(1[012])pt\b", clase.group(1)) if clase else None
    lectura = lectura_del_pdf(pdf, int(tam.group(1)) if tam else 10)
    crudas = palabras_crudas(pdf)
    por_pagina = [p["cuerpo"] for p in lectura] if lectura else crudas
    bloques = desglose_prosa(fuente_tex)
    prosa = sum(bloques.values())
    dibujos = diagramas(fuente_tex)
    en_diagramas = [d["palabras"] for d in dibujos]
    mapas = sum(d["mapa"] for d in dibujos)
    paginas_texto = prosa / PALABRAS_POR_PAGINA
    tope = round(a.paginas_texto * PALABRAS_POR_PAGINA) if a.paginas_texto is not None else None
    piso = round(a.paginas_texto_min * PALABRAS_POR_PAGINA) if a.paginas_texto_min is not None else None
    piezas = piezas_visuales(fuente_tex, mapas)
    problemas = problemas_del_log(log)

    # El desglose de la medición anterior dice qué bloque creció.
    registro = outdir / f"{tex.stem}.prosa.json"
    try:
        anterior = json.loads(registro.read_text(encoding="utf-8"))
    except Exception:
        anterior = None
    try:
        outdir.mkdir(parents=True, exist_ok=True)
        registro.write_text(json.dumps(bloques, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass

    fuera: list[str] = []
    if a.paginas is not None and paginas > a.paginas:
        fuera.append(f"{paginas} {plural(paginas, 'página', 'páginas')}: el límite es {a.paginas}")
    if tope is not None and prosa > tope:
        crecidos = sorted(((b, v - anterior.get(b, 0)) for b, v in bloques.items()
                           if anterior and v > anterior.get(b, 0)), key=lambda x: -x[1])
        if crecidos:
            causa = "Creció desde la medición anterior: " + ", ".join(f"{b} +{miles(d)}" for b, d in crecidos) + "."
        else:
            mayores = sorted(((b, v) for b, v in bloques.items() if b != "texto" and v), key=lambda x: -x[1])[:2]
            causa = ("Además del texto, los bloques más grandes: "
                     + ", ".join(f"{b} {miles(v)}" for b, v in mayores) + ".") if mayores else ""
        fuera.append(f"{miles(prosa)} palabras de prosa ({coma(paginas_texto, 2)} páginas de texto): "
                     f"el tope es {miles(tope)} ({coma(a.paginas_texto)} páginas). Sobran {miles(prosa - tope)}."
                     + (f" {causa}" if causa else ""))
    de_texto = paginas_de_texto(fuente_tex, tex.parent)
    piezas["visuales"] -= len(de_texto)  # una página de texto no es una pieza visual
    piezas["figuras"] -= len(de_texto)
    faltan_visuales = (a.visuales_min - piezas["visuales"]
                       if a.visuales_min is not None and piezas["visuales"] < a.visuales_min else 0)
    problemas.extend(f"imagen de texto: {h}. No cuenta como pieza visual: quitarla; si no hay "
                     "otro material, el lugar queda para texto propio o se achica el documento"
                     for h in de_texto)
    if a.visuales_max is not None and piezas["visuales"] > a.visuales_max:
        fuera.append(f"{piezas['visuales']} piezas visuales: el máximo es {a.visuales_max}")
    corto = piso is not None and prosa < piso
    densas = [n + 1 for n, w in enumerate(por_pagina) if w > a.densa]
    cortes = [p["notas"] for p in lectura] if lectura else None
    llenado = llenado_por_pagina(pdf, cortes)
    vacias = [n + 1 for n, (f, _) in enumerate(llenado[:-1]) if f < 0.6]
    a_medias = [(n + 1, f) for n, (f, _) in enumerate(llenado[:-1]) if 0.6 <= f < 0.85]
    huecos = [(n + 1, h) for n, (_, h) in enumerate(llenado) if h > 0.2]

    avisos: list[str] = []
    notas: list[str] = []
    if a.paginas_min is not None and paginas < a.paginas_min:
        avisos.append(f"{paginas} {plural(paginas, 'página', 'páginas')}, menos que el mínimo del largo "
                      f"({a.paginas_min}). Sumar lo que las fuentes traen y quedó afuera; si no hay más, "
                      "decir en el reporte qué quedó afuera y por qué.")
    parte_real = prosa / (paginas * PALABRAS_POR_PAGINA) if paginas else 0.0
    if a.parte_texto is not None and parte_real > a.parte_texto + 0.08 and not (tope is not None and prosa > tope):
        avisos.append(f"la prosa ocupa el {coma(parte_real * 100)} % de {plural(paginas, 'la página', f'las {paginas} páginas')}; "
                      f"el perfil pide {coma(a.parte_texto * 100, 0)} %. El documento quedó más corto con el "
                      "mismo texto: sumar piezas visuales con material real o recortar texto.")
    if faltan_visuales:
        avisos.append(f"{piezas['visuales']} {plural(piezas['visuales'], 'pieza visual', 'piezas visuales')}, "
                      f"{faltan_visuales} menos que el mínimo del "
                      f"perfil ({a.visuales_min}). Sumar solo con material real (gráficos de los datos, "
                      "diagramas que muestren una relación, capturas de una interfaz); si no hay, "
                      "dejarlo así y decirlo en el reporte. Nunca la foto de una página de texto.")
    if corto:
        avisos.append(f"{miles(prosa)} palabras de prosa, por debajo del piso de {miles(piso)} "
                      "que fija «más texto». Explicar más donde el lector lo necesita (porqués, "
                      "ejemplos), no rellenar.")
    if vacias:
        avisos.append(f"más del 40 % en blanco al pie en {plural(len(vacias), 'la página', 'las páginas')} "
                      f"{lista(vacias)}. Que la sección siguiente siga en esa página (sin \\newpage), o sumar "
                      "la pieza visual que falta; si el blanco es a propósito, decirlo en el reporte.")
    if llenado and paginas == 1 and llenado[0][0] < 0.85:
        avisos.append(f"la hoja usa el {int(llenado[0][0] * 100)} % de la página "
                      f"({coma((1 - llenado[0][0]) * ALTO_CAJA_CM)} cm libres al pie): sumar la pieza al pie "
                      "o agrandar la principal.")
    if llenado and paginas > 1 and llenado[-1][0] < 0.35:
        avisos.append(f"la última página usa el {int(llenado[-1][0] * 100)} % de su alto. Que entre en la "
                      "anterior: quitar lo que no se cita, achicar una pieza.")
    for pagina, h in huecos:
        avisos.append(f"hueco de {round(h * 100)} % de la altura en el medio de la página {pagina}. "
                      "Casi siempre es un \\vfill que empuja una pieza al pie: quitarlo, o sumar "
                      "contenido arriba.")
    if lectura and llenado:
        for n, p in enumerate(lectura[:-1]):
            fin_tinta = llenado[n][0] if n < len(llenado) else 1.0
            if (p["ultimo_renglon"].rstrip().endswith(":") and p["fondo_renglon"] is not None
                    and fin_tinta - p["fondo_renglon"] < 0.03):
                frase = p["ultimo_renglon"].strip()
                frase = frase if len(frase) <= 60 else "…" + frase[-59:]
                avisos.append(f"la página {n + 1} termina en «:» («{frase}»): lo que anuncia quedó en la "
                              f"página {n + 2}. Poner la frase como pie de un bloque con lo que presenta, o "
                              "\\needspace antes del párrafo.")
    cargados = [n + 1 for n, d in enumerate(dibujos) if d["palabras"] > 60 and not d["mapa"]]
    for n, d in enumerate(dibujos):
        for nodo in ([] if d["mapa"] else d["nodos"]):  # el mapa del tema es navegación
            if nodo["palabras"] > 12 and not nodo["contenedor"]:
                en = "en la lista de un \\foreach, " if nodo["foreach"] else ""
                avisos.append(f"el diagrama {n + 1} tiene un nodo con {nodo['palabras']} palabras "
                              f"({en}{donde(nodo['pos'])}): texto en una caja. Dejar en el nodo "
                              "unas pocas palabras y pasar el resto al texto o al pie.")
    for pos, trozo in tildes_de_aproximado(fuente_tex):
        avisos.append(f"«~» antes de un número ({donde(pos)}: «{trozo}»): en LaTeX es un espacio "
                      "duro y no se ve. Para «aproximadamente», escribir «unos», «cerca de» o \\textasciitilde.")
    for sigla in referencias_sin_citar(fuente_tex):
        avisos.append(f"la referencia [{sigla}] no se cita en ningún \\fuente{{…}} del cuerpo: citarla donde se "
                      "usa o quitarla de la lista.")
    if a.lector == "estudio":
        for titulo in secciones_sin_repaso(fuente_tex):
            avisos.append(f"la sección «{titulo}» no tiene repaso: con lector=estudio, 3 a 5 preguntas al "
                          "cierre de cada sección (entorno repaso).")
    if a_medias:
        notas.append("blanco al pie de 15 a 40 % en "
                     + "; ".join(f"la página {p} ({coma((1 - f) * ALTO_CAJA_CM)} cm libres)" for p, f in a_medias)
                     + ". Se acepta, o se mueve un párrafo o se achica una pieza para cerrarlo.")
    if lectura is None:
        notas.append("sin pdfplumber, las palabras por página son todas las del PDF, "
                     "no solo las de la letra del cuerpo.")

    if a.json:
        print(json.dumps({
            "pdf": str(pdf), "paginas": paginas, "paginas_min": a.paginas_min, "palabras_prosa": prosa,
            "desglose_prosa": bloques, "tope_prosa": tope,
            "palabras_en_diagramas": en_diagramas, "mapas_del_tema": mapas, "piso_prosa": piso, "piezas": piezas,
            "faltan_visuales": faltan_visuales, "imagenes_de_texto": de_texto,
            "paginas_texto": round(paginas_texto, 2), "parte_texto_real": round(parte_real, 3),
            "palabras_por_pagina": por_pagina, "palabras_por_pagina_crudas": crudas,
            "paginas_densas": densas, "llenado": [round(f, 2) for f, _ in llenado],
            "huecos": [round(h, 2) for _, h in llenado],
            "paginas_con_blanco": vacias, "limites_superados": fuera, "problemas": problemas,
            "avisos": avisos, "notas": notas,
        }, ensure_ascii=False, indent=1))
    else:
        lim_p = f" (límite {a.paginas})" if a.paginas is not None else ""
        lim_t = f"; tope {miles(tope)}" if tope is not None else ""
        print(f"{pdf.name} · {paginas} {plural(paginas, 'página', 'páginas')}{lim_p} · texto ≈ "
              f"{coma(paginas_texto)} páginas ({miles(prosa)} {plural(prosa, 'palabra', 'palabras')} de prosa{lim_t})")
        print(f"Prosa: {miles(prosa)} = " + " · ".join(
            f"{b} {miles(v)}" for b, v in bloques.items() if v or b == "texto"))
        if sum(en_diagramas):
            nota = (f" Con más de 60 (texto con cajas): el {', el '.join(map(str, cargados))}."
                    if cargados else "")
            print(f"Palabras dentro de diagramas: {miles(sum(en_diagramas))} en {len(en_diagramas)} "
                  f"{plural(len(en_diagramas), 'dibujo TikZ', 'dibujos TikZ')}, que no cuentan como texto.{nota}")
        lim_v = ""
        if a.visuales_min is not None or a.visuales_max is not None:
            partes = ([f"mínimo {a.visuales_min}"] if a.visuales_min is not None else []) + \
                     ([f"máximo {a.visuales_max}"] if a.visuales_max is not None else [])
            lim_v = f"; {', '.join(partes)}"
        mapa = f" · mapa del tema: {mapas}" if mapas else ""
        print(f"Piezas visuales: {piezas['visuales']} (figuras o capturas: {piezas['figuras']}; "
              f"diagramas: {piezas['diagramas']}{lim_v}){mapa} · tablas: {piezas['tablas']} · "
              f"filas de cifras: {piezas['cifras']}")
        etiqueta = " (letra del cuerpo)" if lectura else ""
        print(f"Palabras por página{etiqueta}: " + "  ".join(f"{n + 1}:{w}" for n, w in enumerate(por_pagina)))
        for f in fuera:
            print(f"FUERA DE LÍMITE: {f}")
        if densas:
            cuales = "de texto en la letra del cuerpo" if lectura else "en el PDF"
            print(f"Páginas densas (más de {a.densa} palabras {cuales}): "
                  f"{lista(densas)}. Pasar parte a una tabla o un gráfico, o recortar.")
        for x in avisos:
            print(f"AVISO: {x}")
        for x in notas:
            print(f"Nota: {x}")
        for p in problemas:
            print(f"PROBLEMA: {p}")
        if not (fuera or problemas):
            print("Límites y log en regla. Falta mirar cada página (revisar.py).")
    return 1 if (fuera or problemas) else 0


if __name__ == "__main__":
    sys.exit(main())
