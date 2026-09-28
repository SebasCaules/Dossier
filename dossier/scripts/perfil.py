#!/usr/bin/env python3
"""Traduce los parámetros de /dossier a números concretos: páginas, tope de texto, piezas
visuales, estructura según el lector y la línea exacta de medir.py.

    python3 perfil.py [hoja|breve|medio|largo] [+texto|-texto] [+imagenes|-imagenes]
                      [equipo|estudio|entrega|cliente] [impresion|digital]
                      [temas=N] [items=N] [paginas=N] [--json]

Los parámetros van sueltos o entre comillas, en cualquier orden. temas=N son las
secciones del documento; items=N, las unidades que hay que cubrir una por una (19 leyes,
30 conceptos): con muchos ítems el largo necesita más páginas que las de sus temas. Si
los temas o los ítems no entran en el largo, avisa; en una hoja, items=N pide la hoja de
consulta (una fila por ítem) y, sin ítems, da un reparto orientativo del tope.

Las páginas son un tope: menos que el mínimo del largo es un aviso de medir.py. La línea
de medir lleva --paginas-min (salvo en una hoja), --parte-texto y, con lector, --lector.

También acepta clave=valor para todo (largo=medio, texto=mas, imagenes=menos,
lector=estudio, formato=impresion) y sinónimos en inglés (short, medium, long; more,
less; print). El lector y el formato también van sueltos (estudio, impresion, digital).
Sin parámetros: breve, texto e imágenes normales, formato digital.

Mayúsculas y acentos no importan. Un error de tipeo se corrige si hay un solo parámetro
parecido («imprecion» es impresion) y se informa como «Interpreté»; si hay más de uno, o
el parecido es flojo, se informa como DUDA y hay que preguntarle al usuario. Lo que no reconoce lo
devuelve aparte («resto»): es el tema del documento.
"""
from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

PALABRAS_POR_PAGINA = 800
MEDIR = Path(__file__).resolve().parent / "medir.py"

LARGOS = {
    # páginas mín. y máx., páginas por tema (además de la portada) e índice que conviene
    "hoja": {"min": 1, "max": 1, "por_tema": 0.0, "por_item": 0.0, "defecto": 1, "indice": None},
    "breve": {"min": 2, "max": 6, "por_tema": 1.0, "por_item": 0.25, "defecto": 4, "indice": r"\indice"},
    "medio": {"min": 7, "max": 12, "por_tema": 1.5, "por_item": 0.4, "defecto": 9, "indice": r"\indicelista"},
    "largo": {"min": 13, "max": 24, "por_tema": 2.5, "por_item": 0.75, "defecto": 16, "indice": r"\indicelista"},
}
TEXTO = {
    # parte de las páginas que es prosa, piso (solo en «más») y umbral de página densa
    "menos": {"parte": 0.25, "piso": None, "densa": 400},
    "normal": {"parte": 0.40, "piso": None, "densa": 550},
    "mas": {"parte": 0.60, "piso": 0.40, "densa": 700},
}
# Una hoja es toda portada: su texto se mide distinto.
TEXTO_HOJA = {"menos": 0.30, "normal": 0.45, "mas": 0.60}
# Las piezas visuales ocupan lugar: con menos, el texto tiene más espacio, y al revés.
AJUSTE_POR_IMAGENES = {"menos": 0.10, "normal": 0.0, "mas": -0.10}
LECTORES = {
    "equipo": [
        "portada con cifras, resumen y lo urgente",
        "una sección por tema",
        "próximos pasos: qué, quién y para cuándo",
        "cifras para tener a mano; glosario si hay términos propios",
    ],
    "estudio": [
        "portada con el mapa del tema, que en breve reemplaza al índice (sus cajas son los enlaces)",
        "por familia de conceptos, la tríada (definición copiada de la fuente, ejemplo, confusión "
        "típica: un error que la fuente señala) en los 2 a 4 conceptos centrales, el resto en una "
        "línea o en el glosario",
        "si la evaluación es por casos o ejercicios y la fuente trae uno resuelto, una sección que "
        "lo resuelve de punta a punta",
        "cada condición de uso con el umbral que da la fuente",
        "repaso de 3 a 5 preguntas al cierre de cada sección (en hoja, al final)",
        "glosario solo con los términos que el texto usa sin definir (si no hay, no va)",
    ],
    "entrega": [
        "portada formal con \\datosentrega (materia, integrantes y docentes con nombre completo, "
        "fecha); lo que las fuentes no traen se pregunta en la pregunta del plan o queda en "
        "renglones y se avisa",
        "resumen ejecutivo y un \\ojo con la tesis",
        "secciones numeradas; una cita por párrafo, no por oración",
        "referencias que la cátedra puede consultar (la trazabilidad a archivos internos, "
        "transcripciones y apuntes va al README)",
        "sin notas de trabajo, rótulos internos ni «hoy»",
    ],
    "cliente": [
        "portada con quién propone, a quién y la fecha",
        "la recomendación primero",
        "cifras de negocio y, si la fuente no las tiene, metas del servicio rotuladas como "
        "propuesta (nunca estimaciones propias)",
        "una sección por decisión (en hoja, una fila por decisión en una tabla: qué gana y qué cuesta)",
        "qué se necesita de su lado, siempre",
        "próximos pasos con fecha solo si la fuente los trae",
        "sin jerga ni rótulos internos: cada término se entiende sin la fuente",
    ],
}
# Hoja: cómo se reparte el tope de palabras entre las piezas (orientativo).
REPARTO_HOJA = (("portada y resumen", 0.40), ("tabla", 0.35), ("avisos y pies", 0.25))

SINONIMOS = {
    "largo": {
        "hoja": "hoja", "1hoja": "hoja", "unahoja": "hoja", "unapagina": "hoja", "onepage": "hoja",
        "onepager": "hoja", "breve": "breve", "corto": "breve", "short": "breve",
        "brief": "breve", "medio": "medio", "mediano": "medio", "medium": "medio",
        "largo": "largo", "extenso": "largo", "long": "largo", "large": "largo",
    },
    "nivel": {
        "mas": "mas", "more": "mas", "+": "mas", "alto": "mas", "menos": "menos",
        "less": "menos", "-": "menos", "bajo": "menos", "normal": "normal", "=": "normal",
    },
    "lector": {
        "equipo": "equipo", "team": "equipo", "companeros": "equipo", "estudio": "estudio",
        "estudiar": "estudio", "study": "estudio", "repaso": "estudio", "entrega": "entrega",
        "catedra": "entrega", "formal": "entrega", "tp": "entrega", "cliente": "cliente",
        "client": "cliente", "directorio": "cliente", "ejecutivo": "cliente",
    },
    "salida": {
        "pantalla": "pantalla", "digital": "pantalla", "screen": "pantalla", "impresion": "impresion",
        "imprimir": "impresion", "papel": "impresion", "print": "impresion",
    },
}
CLAVES = {
    "largo": "largo", "tamano": "largo", "size": "largo", "extension": "largo",
    "texto": "texto", "text": "texto", "txt": "texto",
    "imagenes": "imagenes", "imagen": "imagenes", "img": "imagenes", "visual": "imagenes",
    "visuales": "imagenes", "images": "imagenes",
    "lector": "lector", "para": "lector", "publico": "lector", "audiencia": "lector",
    "salida": "salida", "formato": "salida",
    "paginas": "paginas", "pages": "paginas", "temas": "temas", "topics": "temas",
    "items": "items", "unidades": "items", "conceptos": "items",
}


def _llano(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn").replace(" ", "")


# Lo que puede ir suelto: palabra → (parámetro, valor).
SUELTAS = {
    **{k: ("largo", v) for k, v in SINONIMOS["largo"].items()},
    **{k: ("salida", v) for k, v in SINONIMOS["salida"].items()},
    **{k: ("lector", k) for k in ("equipo", "estudio", "entrega", "cliente")},
}
# Lo que va después de + o -: palabra → parámetro.
PERILLAS = {k: v for k, v in CLAVES.items() if v in ("texto", "imagenes")}
def _resolver(palabra: str, opciones: dict, umbral_duda: float = 0.66):
    """Busca `palabra` en `opciones` (palabra → destino) y devuelve (estado, destino, candidatos).

    exacto: está tal cual. corregido: se parece a un solo destino (≥ 0,8), sin rivales a
    menos de 0,08. duda: se parece a más de un destino, o entre `umbral_duda` y 0,8.
    nada: no se parece a ninguno, o tiene menos de 4 letras.
    """
    if palabra in opciones:
        return "exacto", opciones[palabra], []
    if len(palabra) < 4:
        return "nada", None, []
    puntajes = sorted(((SequenceMatcher(None, palabra, o).ratio(), o) for o in opciones), reverse=True)
    mejor, cerca = puntajes[0]
    if mejor < umbral_duda:
        return "nada", None, []
    rivales = {opciones[o] for s, o in puntajes if s >= mejor - 0.08} - {opciones[cerca]}
    if mejor >= 0.8 and not rivales:
        return "corregido", opciones[cerca], []
    candidatos: list[str] = []
    for s, o in puntajes:
        if s >= umbral_duda and o not in candidatos:
            candidatos.append(o)
    return "duda", None, candidatos[:3]


def _mostrar(parametro: str, valor: str) -> str:
    """Cómo se escribe un parámetro ya resuelto, para los avisos."""
    if parametro == "salida":
        return "digital" if valor == "pantalla" else valor
    return valor


def parsear(tokens: list[str]) -> tuple[dict, list[str], list[str], list]:
    """Devuelve (parámetros, avisos, resto no reconocido, dudas). Los errores de tipeo que
    se corrigieron van en avisos, como «Interpreté»; los que no, en dudas."""
    p = {"largo": "breve", "texto": "normal", "imagenes": "normal", "lector": None,
         "salida": "pantalla", "paginas": None, "temas": None, "items": None}
    avisos, resto, interpretados, dudas = [], [], [], []
    unidos: list[str] = []
    for token in tokens:  # «1 hoja» y «una hoja» son un solo parámetro
        if unidos and _llano(unidos[-1]) in ("1", "una") and _llano(token) in ("hoja", "pagina"):
            unidos[-1] += token
        else:
            unidos.append(token)
    for token in unidos:
        crudo = token.strip()
        t = _llano(crudo)
        if not t:
            continue
        m = re.fullmatch(r"([+-])(\w+)", t) or re.fullmatch(r"(mas|menos|more|less)[-_]?(\w+)", t)
        if m:
            estado, perilla, candidatos = _resolver(m.group(2), PERILLAS)
            signo = "+" if m.group(1) in ("+", "mas", "more") else "-"
            if perilla in ("texto", "imagenes"):
                p[perilla] = "mas" if signo == "+" else "menos"
                if estado == "corregido":
                    interpretados.append((crudo, f"{signo}{perilla}"))
            elif estado == "duda":
                dudas.append((crudo, [f"{signo}{c}" for c in candidatos]))
            else:
                resto.append(crudo)
            continue
        if "=" in t:
            clave_txt, valor = t.split("=", 1)
            estado_c, clave, candidatos = _resolver(clave_txt, CLAVES)
            if estado_c == "duda":
                dudas.append((crudo, [f"{c}=" for c in candidatos]))
                continue
            if clave in ("paginas", "temas", "items"):
                if valor.isdigit() and int(valor) > 0:
                    p[clave] = int(valor)
                    if estado_c == "corregido":
                        interpretados.append((crudo, f"{clave}={valor}"))
                else:
                    avisos.append(f"{crudo}: se esperaba un número entero positivo")
                continue
            tabla = {"largo": "largo", "texto": "nivel", "imagenes": "nivel",
                     "lector": "lector", "salida": "salida"}.get(clave)
            if not tabla:
                resto.append(crudo)
                continue
            estado_v, valor_final, candidatos = _resolver(valor, SINONIMOS[tabla])
            if estado_v == "duda":
                dudas.append((crudo, [f"{clave}={c}" for c in candidatos]))
            elif valor_final is None:
                avisos.append(f"{crudo}: valor desconocido; se deja {p[clave] or 'sin fijar'}")
            else:
                p[clave] = valor_final
                if "corregido" in (estado_c, estado_v):
                    nombre = "formato" if clave == "salida" else clave
                    interpretados.append((crudo, f"{nombre}={_mostrar(clave, valor_final)}"))
            continue
        # Suelta: un umbral de duda más alto, porque acá también podría caer una palabra
        # del tema («mercado» no tiene que preguntar si es «medio»).
        estado, destino, candidatos = _resolver(t, SUELTAS, umbral_duda=0.72)
        if estado == "duda":
            dudas.append((crudo, candidatos))
        elif destino is None:
            resto.append(crudo)
        else:
            p[destino[0]] = destino[1]
            if estado == "corregido":
                interpretados.append((crudo, _mostrar(destino[0], destino[1])))
    avisos = [f"Interpreté «{c}» como {o}." for c, o in interpretados] + avisos
    return p, avisos, resto, dudas


def plural(n: int, uno: str, varios: str) -> str:
    """La forma que va con n: plural(1, 'página', 'páginas') es «página»."""
    return uno if n == 1 else varios


def calcular(p: dict) -> dict:
    L = LARGOS[p["largo"]]
    avisos: list[str] = []
    if p["paginas"]:
        paginas = p["paginas"]
        if not L["min"] <= paginas <= L["max"]:
            otro = next((k for k, v in LARGOS.items() if v["min"] <= paginas <= v["max"]), "largo")
            avisos.append(f"paginas={paginas} no entra en «{p['largo']}» ({L['min']} a {L['max']}): "
                          f"corresponde a «{otro}». Se respeta el número pedido.")
        origen = "fijadas en el pedido"
    elif (p["temas"] or p["items"]) and p["largo"] != "hoja":
        por_temas = 1 + math.ceil(p["temas"] * L["por_tema"]) if p["temas"] else 0
        por_items = 1 + math.ceil(p["items"] * L["por_item"]) if p["items"] else 0
        paginas = min(L["max"], max(L["min"], por_temas, por_items))
        partes = ([f"{p['temas']} {plural(p['temas'], 'tema', 'temas')} × {coma(L['por_tema'])}"]
                  if p["temas"] else []) + \
                 ([f"{p['items']} {plural(p['items'], 'ítem', 'ítems')} × {coma(L['por_item'])}"]
                  if p["items"] else [])
        origen = f"portada + el mayor de {' o '.join(partes)}, dentro de {L['min']} a {L['max']}"
    else:
        paginas = L["defecto"]
        origen = ("una sola página" if p["largo"] == "hoja"
                  else f"punto medio de {L['min']} a {L['max']}; con temas=N se ajusta al contenido")
    # Temas o ítems que no entran en el largo (o en las páginas pedidas): se recortaban en silencio.
    if p["largo"] != "hoja":
        tope_paginas = p["paginas"] or L["max"]
        for clave, por, uno, varios in (("temas", "por_tema", "tema", "temas"), ("items", "por_item", "ítem", "ítems")):
            if p[clave] and 1 + math.ceil(p[clave] * L[por]) > tope_paginas:
                donde = (plural(tope_paginas, "la página pedida", f"las {tope_paginas} páginas pedidas")
                         if p["paginas"] else f"{p['largo']} (máx. {L['max']})")
                avisos.append(f"{p[clave]} {plural(p[clave], uno, varios)} × {coma(L[por])} + portada = "
                              f"{1 + math.ceil(p[clave] * L[por])} páginas: no entran en {donde}; agrupar {varios}.")
    paginas_min = None if paginas == 1 else min(L["min"], paginas)

    T = TEXTO[p["texto"]]
    parte = round((TEXTO_HOJA[p["texto"]] if paginas == 1 else T["parte"]) + AJUSTE_POR_IMAGENES[p["imagenes"]], 2)
    paginas_texto = round(paginas * parte, 2)
    tope = round(paginas * parte * PALABRAS_POR_PAGINA)
    piso = round(paginas * T["piso"] * PALABRAS_POR_PAGINA) if T["piso"] and paginas > 1 else None

    if p["imagenes"] == "menos":
        vis_min, vis_max = paginas // 2, paginas
    elif p["imagenes"] == "mas":
        vis_min, vis_max = max(2, math.ceil(1.5 * paginas)), None
    else:
        vis_min, vis_max = max(1, paginas - 1), None

    if p["texto"] == "mas" and p["imagenes"] == "mas" and p["largo"] in ("hoja", "breve"):
        avisos.append("Más texto y más imágenes en un documento corto: entra si se recortan temas. "
                      "Priorizar los que el lector necesita.")
    if p["texto"] == "menos" and p["imagenes"] == "menos":
        avisos.append("Menos texto y menos imágenes: el peso lo llevan las tablas y las cifras.")
    reparto = None
    if paginas == 1 and p["items"]:
        avisos.append(f"items={p['items']} en una hoja: ~{tope // p['items']} palabras por ítem (las celdas "
                      "cuentan); una fila de tabla por ítem; plantilla de consulta.")
    elif paginas == 1:
        reparto = [(nombre, parte_, round(tope * parte_)) for nombre, parte_ in REPARTO_HOJA]

    medir = ["<doc>.tex", f"--paginas {paginas}"]
    if paginas_min is not None:
        medir.append(f"--paginas-min {paginas_min}")
    medir += [f"--paginas-texto {str(paginas_texto)}", f"--parte-texto {parte:g}", f"--densa {T['densa']}",
              f"--visuales-min {vis_min}"]
    if vis_max is not None:
        medir.append(f"--visuales-max {vis_max}")
    if piso:
        medir.append(f"--paginas-texto-min {round(paginas * T['piso'], 2)}")
    if p["lector"]:
        medir.append(f"--lector {p['lector']}")
    casa = str(Path.home())
    ruta_medir = str(MEDIR).replace(casa, "~", 1) if " " not in str(MEDIR) else f'"{MEDIR}"'

    return {
        "parametros": p,
        "paginas": paginas, "paginas_min": paginas_min, "rango_paginas": [L["min"], L["max"]],
        "origen_paginas": origen, "reparto_hoja": reparto,
        "parte_texto": parte, "paginas_texto": paginas_texto, "tope_palabras": tope,
        "piso_palabras": piso, "densa": T["densa"],
        "visuales_min": vis_min, "visuales_max": vis_max,
        # Con estudio en breve, el mapa del tema de la portada hace de índice.
        "indice": None if (p["lector"] == "estudio" and p["largo"] == "breve") else L["indice"],
        "preambulo": r"\usepackage[impresion]{dossier}" if p["salida"] == "impresion" else r"\usepackage{dossier}",
        "estructura": LECTORES.get(p["lector"]) if p["lector"] else None,
        "medir": " ".join(medir), "medir_linea": f"python3 {ruta_medir} " + " ".join(medir),
        "avisos": avisos,
    }


def coma(x: float) -> str:
    return f"{x:g}".replace(".", ",")


def miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def imprimir(r: dict, resto: list[str], dudas: list) -> None:
    p = r["parametros"]
    nombres = {"mas": "más", "menos": "menos", "normal": "normal"}
    print(f"Perfil: {p['largo']} — texto {nombres[p['texto']]} — imágenes {nombres[p['imagenes']]}"
          f" — lector {p['lector'] or 'según el pedido'} — formato "
          f"{'impresión' if p['salida'] == 'impresion' else 'digital'}")
    if r["paginas"] == 1:
        print("Páginas: 1")
    else:
        minimo, maximo = r["rango_paginas"]
        print(f"Páginas: hasta {r['paginas']} ({p['largo']}: {minimo} a {maximo}; menos de "
              f"{r['paginas_min']} es un aviso) · {r['origen_paginas']}")
    linea = (f"Texto: hasta {round(r['parte_texto'] * 100)} % → {coma(r['paginas_texto'])} "
             f"{plural(r['paginas_texto'], 'página', 'páginas')}, "
             f"{miles(r['tope_palabras'])} palabras de prosa")
    if r["piso_palabras"]:
        linea += f", y al menos {miles(r['piso_palabras'])}"
    print(linea + f". Página densa desde {r['densa']} palabras.")
    if r["reparto_hoja"]:
        print(f"Reparto orientativo de las {miles(r['tope_palabras'])} palabras: " + ", ".join(
            f"{nombre} ~{round(parte * 100)} % ({n})" for nombre, parte, n in r["reparto_hoja"]) + ".")
    vis = f"al menos {r['visuales_min']}"
    ultimo = r["visuales_min"]
    if r["visuales_max"] is not None:
        vis += f" y como mucho {r['visuales_max']}"
        ultimo = r["visuales_max"]
    print(f"Imágenes: {vis} {plural(ultimo, 'pieza visual', 'piezas visuales')} (gráficos, diagramas, "
          "capturas de interfaces; no cuentan "
          "tablas, cifras ni fotos de páginas de texto). El mínimo es una meta: se completa con material real.")
    sin_indice = "ninguno (una sola página)" if r["paginas"] == 1 else "ninguno: el mapa del tema lo reemplaza"
    print(f"Índice: {r['indice'] or sin_indice} · preámbulo: {r['preambulo']}")
    if r["estructura"]:
        print(f"Estructura para lector={p['lector']}:")
        for e in r["estructura"]:
            print(f"  - {e}")
    for a in r["avisos"]:
        print(a if a.startswith("Interpreté") else f"AVISO: {a}")
    for crudo, candidatos in dudas:
        print(f"DUDA: «{crudo}» se parece a {' o '.join(candidatos)}. Preguntar al usuario "
              "antes de seguir; mientras tanto se tomó el valor por defecto.")
    if resto:
        print(f"Resto (tema del documento): {' '.join(resto)}")
    print(f"Medir con: {r['medir_linea']}")


def main() -> int:
    # Sin argparse: «-imagenes» y «-texto» son parámetros, no opciones. Los parámetros
    # pueden llegar sueltos o como un solo argumento (el texto que siguió a /dossier).
    tokens = [t for arg in sys.argv[1:] for t in arg.split()]
    if any(t in ("-h", "--help") for t in tokens):
        print(__doc__)
        return 0
    como_json = "--json" in tokens
    p, avisos, resto, dudas = parsear([t for t in tokens if t != "--json"])
    r = calcular(p)
    r["avisos"] = avisos + r["avisos"]
    if como_json:
        print(json.dumps({**r, "resto": resto, "dudas": dudas}, ensure_ascii=False, indent=1))
    else:
        imprimir(r, resto, dudas)
    return 0


if __name__ == "__main__":
    sys.exit(main())
