"""Estilo de los gráficos de un dossier: la misma letra, el mismo tamaño y la misma
paleta que el PDF.

    from estilo_graficos import plt, P, SERIES, figura, guardar, num, pct, barras_h, rotular
    from estilo_graficos import densidad, sombrear, corte, escalones   # funciones y tramos

Cada figura se dibuja a su tamaño final (el ancho del texto de dossier.sty es 174 mm) y
LaTeX la incluye sin escalar, así la letra del gráfico mide lo mismo en el papel que en
el código. La paleta se lee de dossier.sty y de los \\definecolor del .tex de esta carpeta:
si el documento adopta los colores de un proyecto, los gráficos los siguen solos.
"""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("pdf")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.mathtext import MathTextParser  # noqa: E402

AQUI = Path(__file__).resolve().parent
FIG = AQUI / "fig"
ANCHO_TEXTO_MM = 174
MM = 1 / 25.4

_DEFINECOLOR = re.compile(r"\\definecolor\{(\w+)\}\{HTML\}\{([0-9A-Fa-f]{6})\}")


def leer_paleta(*archivos: Path) -> dict[str, str]:
    """Colores `\\definecolor{nombre}{HTML}{RRGGBB}` de los archivos dados; el último gana.
    Ignora las líneas comentadas."""
    paleta: dict[str, str] = {}
    for archivo in archivos:
        if not archivo.exists():
            continue
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            codigo = re.split(r"(?<!\\)%", linea, maxsplit=1)[0]
            for nombre, valor in _DEFINECOLOR.findall(codigo):
                paleta[nombre] = "#" + valor.lower()
    return paleta


P = leer_paleta(AQUI / "dossier.sty", *sorted(AQUI.glob("*.tex")))

# Colores para distinguir categorías o series: la paleta de referencia de la skill dataviz,
# que pasa su validador sobre fondo blanco en este orden (ver dataviz/references/palette.md).
# Los colores del documento (P) sirven para destacar una serie contra gris, no para
# distinguir categorías: el acento es demasiado oscuro y apagado para ese uso. Si el
# proyecto trae su propia paleta categórica, reemplazar esta lista y validarla.
# Con puntos o mapas, donde cualquier par de colores queda junto, usar solo los tres primeros.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"]


def _fuente() -> str:
    """La familia del documento si el sistema la tiene; si no, una sin serifa cualquiera.

    Avenir Next viene en una colección .ttc y matplotlib solo lee su primera cara, que es
    la Bold: todo el gráfico saldría en negrita. Por eso se extraen la Regular, la Demi
    Bold (la negrita del documento) y la Italic a archivos sueltos, una sola vez.
    """
    ttc = Path("/System/Library/Fonts/Avenir Next.ttc")  # macOS; en otros sistemas, DejaVu Sans
    if not ttc.exists():
        return "DejaVu Sans"
    try:
        import logging

        from fontTools.ttLib import TTCollection

        logging.getLogger("fontTools").setLevel(logging.ERROR)
        cache = Path(matplotlib.get_cachedir()) / "dossier-fuentes"
        cache.mkdir(parents=True, exist_ok=True)
        coleccion = None
        for cara in ("Regular", "Demi Bold", "Italic"):
            destino = cache / f"AvenirNext-{cara.replace(' ', '')}.ttf"
            if not destino.exists():
                coleccion = coleccion or TTCollection(str(ttc))
                for fuente in coleccion.fonts:
                    if fuente["name"].getDebugName(4) == f"Avenir Next {cara}":
                        fuente.save(str(destino))
                        break
            fm.fontManager.addfont(str(destino))
        return "Avenir Next"
    except Exception:
        return "DejaVu Sans"


FAMILIA = _fuente()

plt.rcParams.update({
    "font.family": [FAMILIA, "DejaVu Sans"],
    "font.size": 8.5,
    "text.color": P.get("tinta", "#16233a"),
    "axes.edgecolor": P.get("linea", "#b9c0cc"),
    "axes.labelcolor": P.get("rotulo", "#3d4d66"),
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 9,
    "axes.titleweight": "semibold",
    "axes.titlelocation": "left",
    "xtick.color": P.get("apagado", "#5f6779"),
    "ytick.color": P.get("apagado", "#5f6779"),
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
    "pdf.fonttype": 42,
})
if FAMILIA == "Avenir Next":
    # Las fórmulas ($\sigma = 120$) en la letra del documento, no en DejaVu; lo que Avenir
    # no tiene (algunos símbolos) sale de STIX sin serifa. La α de Avenir itálica es igual
    # a su «a»: \alpha sale de DejaVu Sans oblicua (ver _formula).
    plt.rcParams.update({
        "mathtext.fontset": "custom",
        "mathtext.rm": "Avenir Next",
        "mathtext.sf": "Avenir Next",
        "mathtext.it": "Avenir Next:italic",
        "mathtext.bf": "Avenir Next:bold",
        "mathtext.cal": "DejaVu Sans:italic",
        "mathtext.fallback": "stixsans",
    })

# Dentro de cada $…$: la coma decimal sin espacio (mathtext trata «,» como puntuación y
# escribe «0, 05»; como icomma en el PDF, «$a, b$» conserva el suyo) y, con Avenir, \alpha
# en otra letra para que no se lea «a = 0,05».
_COMA_DECIMAL = re.compile(r"(?<=\d),(?=\d)")
_ALFA = re.compile(r"\\alpha(?![A-Za-z])")
_parse_original = MathTextParser.parse


def _formula(m: re.Match) -> str:
    texto = _COMA_DECIMAL.sub("{,}", m.group(0))
    if FAMILIA == "Avenir Next":
        texto = _ALFA.sub(r"{\\mathcal{\\alpha}}", texto)
    return texto


def _parse_formula(self, s, *args, **kwargs):
    return _parse_original(self, re.sub(r"\$[^$]*\$", _formula, s), *args, **kwargs)


MathTextParser.parse = _parse_formula


def figura(alto_mm: float = 60, ancho: float = 1.0, **kw):
    """`plt.subplots` al tamaño final. `ancho` es la fracción del ancho del texto."""
    return plt.subplots(figsize=(ANCHO_TEXTO_MM * ancho * MM, alto_mm * MM), **kw)


def guardar(fig, nombre: str) -> Path:
    """Guarda en fig/ como PDF vectorial (texto seleccionable) y cierra la figura."""
    FIG.mkdir(exist_ok=True)
    ruta = FIG / nombre
    fig.savefig(ruta, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return ruta


def num(x: float, dec: int = 0) -> str:
    """12345.6 -> '12.345,6' (miles con punto, decimales con coma)."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x: float, dec: int = 1) -> str:
    return f"{num(x, dec)} %"


def _luminancia(hexa: str) -> float:
    canales = [int(hexa.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lineales = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in canales]
    return 0.2126 * lineales[0] + 0.7152 * lineales[1] + 0.0722 * lineales[2]


def texto_sobre(fondo: str) -> str:
    """Blanco o tinta, el que más contraste tenga sobre `fondo`: para rótulos dentro de una
    barra. Sobre el naranja de SERIES, el blanco no llega a 3,5:1 y la tinta sí."""
    tinta = P.get("tinta", "#16233a")
    lf = _luminancia(fondo)
    con_blanco = 1.05 / (lf + 0.05)
    con_tinta = (max(lf, _luminancia(tinta)) + 0.05) / (min(lf, _luminancia(tinta)) + 0.05)
    return "white" if con_blanco >= con_tinta else tinta


def rotular(ax, barras, fmt=num, color=None):
    """Escribe el valor al final de cada barra (columnas o barras horizontales).

    `barras` es lo que devuelven `ax.bar` o `ax.barh`. Cuando el valor está escrito, no
    hace falta eje: conviene quitarlo con `ax.set_yticks([])` (o `set_xticks`).
    """
    color = color or P.get("tinta", "#16233a")
    horizontal = barras.orientation == "horizontal"
    tope = 0.0
    for barra in barras:
        x, y, ancho, alto = barra.get_x(), barra.get_y(), barra.get_width(), barra.get_height()
        if horizontal:
            tope = max(tope, x + ancho)
            ax.annotate(fmt(ancho), (x + ancho, y + alto / 2), xytext=(3, 0),
                        textcoords="offset points", va="center", ha="left", color=color)
        else:
            tope = max(tope, y + alto)
            ax.annotate(fmt(alto), (x + ancho / 2, y + alto), xytext=(0, 2),
                        textcoords="offset points", va="bottom", ha="center", color=color)
    # aire para que el rótulo más largo no choque con el título ni con el borde
    if horizontal:
        ax.set_xlim(right=tope * 1.14)
    else:
        ax.set_ylim(top=tope * 1.16)
    return ax


def barras_h(ax, etiquetas, valores, destacar=None, fmt=num, color=None, color_destacado=None):
    """Barras horizontales desde cero, de mayor a menor, con el valor al final de cada una.

    Es la forma que conviene cuando los valores están cerca (27,3 y 28,1): las etiquetas
    encima de puntos se pisan y una barra que arranca en cero no exagera la diferencia.
    `destacar` es la etiqueta (o lista de etiquetas) que va en el color de acento. Los
    empates quedan en el orden en que se pasan, de arriba hacia abajo.
    """
    # de mayor a menor (el orden estable respeta los empates) y al revés, porque barh
    # dibuja de abajo hacia arriba
    pares = sorted(zip(etiquetas, valores), key=lambda par: -par[1])[::-1]
    destacadas = {destacar} if isinstance(destacar, str) else set(destacar or [])
    base = color or P.get("linea", "#b9c0cc")
    fuerte = color_destacado or P.get("acento", "#22456f")
    colores = [fuerte if e in destacadas else base for e, _ in pares]
    ys = range(len(pares))
    ax.barh(list(ys), [v for _, v in pares], color=colores, height=0.62)
    ax.set_yticks(list(ys), [e for e, _ in pares])
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    tope = max(v for _, v in pares) if pares else 1
    for y, (e, v) in zip(ys, pares):
        ax.text(v + tope * 0.012, y, fmt(v), va="center", ha="left",
                color=P.get("tinta", "#16233a"),
                fontweight="semibold" if e in destacadas else "normal")
    ax.set_xlim(0, tope * 1.14)
    return ax


# ---------------------------------------------------------------- funciones y tramos
def _mezcla(color: str, alfa: float) -> str:
    """El color que se ve al pintar `color` con opacidad `alfa` sobre blanco."""
    canales = [int(color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(255 - alfa * (255 - c)):02x}" for c in canales)


def _eje_funcion(ax):
    """Eje x limpio y sin eje y (la altura de una densidad no se lee), con aire arriba para
    la leyenda y los rótulos de corte. Los límites salen de las curvas de `densidad`."""
    curvas = [linea for linea in ax.lines if linea.get_gid() == "densidad"]
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", length=2, pad=2)
    if curvas:
        xs = np.concatenate([np.asarray(c.get_xdata(), float) for c in curvas])
        ys = np.concatenate([np.asarray(c.get_ydata(), float) for c in curvas])
        ax.set_xlim(xs.min(), xs.max())
        # un renglón de aire por cada entrada de la leyenda, para que no pise el pico
        leyenda = sum(1 for c in curvas if not c.get_label().startswith("_"))
        ax.set_ylim(0, ys.max() * (1.18 + 0.13 * leyenda))


def densidad(ax, x, y, color=None, rotulo=None):
    """Una curva (una densidad, una función de una variable) sobre un eje x limpio.

    Con `rotulo`, la curva entra en la leyenda, arriba a la izquierda. Los parámetros salen
    de un ejemplo de la fuente, nunca inventados para ilustrar.
    """
    color = color or P.get("acento", "#22456f")
    ax.plot(np.asarray(x, float), np.asarray(y, float), color=color, lw=1.4,
            solid_capstyle="round", label=rotulo, gid="densidad")
    _eje_funcion(ax)
    if rotulo:
        ax.legend(loc="upper left", handlelength=1.4, borderaxespad=0.2)
    return ax


def sombrear(ax, x, y, desde, hasta, color=None, fuerte=False, rotulo=None):
    """El área bajo la curva entre `desde` y `hasta` (una probabilidad, una región de rechazo).

    `fuerte` la pinta más oscura: una parte dentro de otra (el valor p dentro de alfa). El
    rótulo va pegado al área, sin línea guía: adentro si el área es alta; si es una cola,
    encima de la curva y hacia afuera.
    """
    color = color or P.get("acento", "#22456f")
    x, y = np.asarray(x, float), np.asarray(y, float)
    desde, hasta = max(desde, x.min()), min(hasta, x.max())
    xs = np.concatenate([[desde], x[(x > desde) & (x < hasta)], [hasta]])
    ys = np.interp(xs, x, y)
    alfa = 0.7 if fuerte else 0.25
    ax.fill_between(xs, 0, ys, color=color, alpha=alfa, lw=0)
    if rotulo:
        area = float(np.sum((ys[1:] + ys[:-1]) / 2 * np.diff(xs)))
        xc = float(np.sum((xs[1:] * ys[1:] + xs[:-1] * ys[:-1]) / 2 * np.diff(xs)) / area) if area > 0 else (desde + hasta) / 2
        yc = float(np.interp(xc, x, y))
        if yc > 0.35 * y.max():
            ax.text(xc, yc * 0.4, rotulo, ha="center", va="center", color=texto_sobre(_mezcla(color, alfa)))
        else:
            afuera = xc > x[np.argmax(y)]
            ax.annotate(rotulo, (xc, yc), xytext=(2 if afuera else -2, 3), textcoords="offset points",
                        ha="left" if afuera else "right", va="bottom", color=P.get("tinta", "#16233a"))
    return ax


def corte(ax, x, rotulo, nivel=0, lado=None):
    """Una línea vertical en un valor (un valor crítico, un umbral) con su rótulo arriba.

    El rótulo va del lado libre, el opuesto al pico de las curvas; `lado` ("izq" o "der")
    lo fija. Con dos cortes cercanos, `nivel=1` baja el segundo rótulo un renglón (2, dos
    renglones), así no se pisan. Si el rótulo toca la leyenda, pasa al otro lado (si ahí
    entra en el eje y `lado` no lo fijó) o baja un renglón.
    """
    picos = [c.get_xdata()[np.argmax(c.get_ydata())] for c in ax.lines if c.get_gid() == "densidad"]
    pico = float(np.mean(picos)) if picos else float(np.mean(ax.get_xlim()))
    derecha = lado == "der" if lado in ("izq", "der") else x >= pico
    trans = ax.get_xaxis_transform()

    def poner(derecha, nivel):
        alto = 0.97 - 0.15 * nivel
        texto = ax.annotate(rotulo, (x, alto), xycoords=trans, xytext=(3 if derecha else -3, 0),
                            textcoords="offset points", ha="left" if derecha else "right",
                            va="top", color=P.get("tinta", "#16233a"))
        return texto, alto

    texto, alto = poner(derecha, nivel)
    leyenda = ax.get_legend()
    if leyenda is not None:
        caja = leyenda.get_window_extent()
        eje = ax.get_window_extent()

        def libre(t):
            c = t.get_window_extent()
            return not c.overlaps(caja) and c.x0 >= eje.x0 - 1 and c.x1 <= eje.x1 + 1

        if not libre(texto) and lado is None:
            otro, alto_otro = poner(not derecha, nivel)
            if libre(otro):
                texto.remove()
                texto, alto = otro, alto_otro
            else:
                otro.remove()
        extra = 0
        while not libre(texto) and extra < 3:  # del mismo lado, un renglón más abajo
            extra += 1
            texto.remove()
            texto, alto = poner(derecha, nivel + extra)
    ax.plot([x, x], [0, alto], transform=trans, color=P.get("rotulo", "#3d4d66"), lw=0.8,
            ls=(0, (3, 2)), gid="corte")
    return ax


def escalones(ax, tramos, color=None):
    """Una escala por tramos (días según la antigüedad, una alícuota según el monto).

    `tramos` = [(desde, hasta, valor, rótulo), ...]; sin rótulo (None o ""), el valor. Cada
    tramo es un escalón con su rótulo encima; el eje x marca los bordes y el y se quita.
    """
    color = color or P.get("linea", "#b9c0cc")
    tope = max(valor for _, _, valor, _ in tramos)
    for desde, hasta, valor, rotulo in tramos:
        ax.fill_between([desde, hasta], 0, valor, color=color, lw=0)
        ax.text((desde + hasta) / 2, valor + tope * 0.03, rotulo or num(valor), ha="center",
                va="bottom", color=P.get("tinta", "#16233a"), fontweight="semibold")
    bordes = sorted({t[0] for t in tramos} | {t[1] for t in tramos})
    for borde in bordes[1:-1]:
        ax.axvline(borde, color="white", lw=1.2)  # separa escalones contiguos
    ax.set_xticks(bordes, [num(b, 0 if float(b).is_integer() else 1) for b in bordes])
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", length=2, pad=2)
    ax.set_xlim(bordes[0], bordes[-1])
    ax.set_ylim(0, tope * 1.2)
    return ax
