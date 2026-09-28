"""Gráficos del documento. Uso: python3 graficos.py (escribe en fig/).

Una función por gráfico, con la fuente de cada valor en el comentario. Los valores se
calculan aquí mismo a partir de las cotas publicadas; no se copian a mano.
"""
import math
import sys

sys.dont_write_bytecode = True  # sin __pycache__ en la carpeta del documento

from estilo_graficos import P, figura, guardar, num  # noqa: E402

N = 10 ** 6  # un millón de claves


def altura_avl_max(n):
    """Altura máxima (en aristas) de un AVL con n claves: la del árbol de Fibonacci.
    N(h) = N(h-1) + N(h-2) + 1 es el mínimo de nodos de un AVL de altura h (W, «AVL tree»);
    la altura máxima es el mayor h con N(h) <= n."""
    minimos = {-1: 0, 0: 1}
    h = 0
    while True:
        h += 1
        minimos[h] = minimos[h - 1] + minimos[h - 2] + 1
        if minimos[h] > n:
            return h - 1


def alturas():
    # Altura en aristas (CLRS 12: número de aristas del camino más largo de la raíz a una hoja).
    # - ABB sin balancear, claves insertadas en orden: una cadena de n nodos, altura n - 1 (CLRS 12).
    # - Rojo-negro: altura <= 2 lg(n + 1) (CLRS 13, lema 13.1) -> 39.
    # - AVL: máximo exacto con la recurrencia de arriba -> 27.
    # - Binario completo, la mínima posible para n claves: floor(lg n) -> 19.
    # - Árbol B con grado mínimo t = 100: h <= log_t((n + 1) / 2) (CLRS 18, teorema 18.1) -> 2.
    datos = [
        ("ABB, claves en orden", N - 1),
        ("Rojo-negro (cota)", math.floor(2 * math.log2(N + 1))),
        ("AVL (máximo)", altura_avl_max(N)),
        ("Binario completo", math.floor(math.log2(N))),
        ("Árbol B, t = 100", math.floor(math.log((N + 1) / 2, 100))),
    ]
    for nombre, valor in datos:
        print(f"{nombre}: {valor}")

    fig, ax = figura(alto_mm=25, ancho=0.56)
    ys = list(range(len(datos)))[::-1]  # la primera fila arriba
    colores = [P.get("acento2", "#b8433a")] + [P.get("linea", "#b9c0cc")] * (len(datos) - 1)
    ax.barh(ys, [v - 0.8 for _, v in datos], color=colores, height=0.62, left=0.8)  # termina en v
    ax.set_xscale("log")
    ax.set_xlim(0.8, 2.2e7)
    ax.set_yticks(ys, [e for e, _ in datos])
    ax.tick_params(axis="y", length=0)
    for lado in ("left", "bottom", "top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_xticks([])
    ax.minorticks_off()
    for y, (_, v) in zip(ys, datos):
        ax.text(v * 1.3, y, num(v), va="center", ha="left", color=P.get("tinta", "#16233a"))
    ax.set_title("Altura con un millón de claves (escala logarítmica)", loc="left")
    guardar(fig, "f1_alturas.pdf")


if __name__ == "__main__":
    alturas()
