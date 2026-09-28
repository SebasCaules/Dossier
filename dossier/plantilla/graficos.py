"""Gráficos del documento. Uso: python3 graficos.py (escribe en fig/).

Una función por gráfico, con la fuente de sus datos en el comentario. Los datos se leen
del archivo del proyecto cuando existe; si se copian a mano, cada valor lleva su fuente.
Las dos funciones de abajo son ejemplos y no se llaman: se reemplazan por las del
documento, y cada una se llama al final. Sin gráficos, se borran y el final queda sin
llamadas.
"""
import sys

sys.dont_write_bytecode = True  # sin __pycache__ en la carpeta del documento

from estilo_graficos import SERIES, barras_h, figura, guardar, pct, rotular  # noqa: E402


# 1. Ejemplo: comparación de pocos valores cercanos -----------------------------------
# Fuente: <archivo o fila del registro de donde salen los valores>
def ejemplo():
    fig, ax = figura(alto_mm=32, ancho=0.62)
    barras_h(ax, ["Al 31/03/2026", "Sin duplicados", "Al 31/01/2026"],
             [27.3, 28.1, 19.6], destacar="Sin duplicados", fmt=pct)
    ax.set_title("Tickets fuera de plazo")  # el título, en el color del texto
    guardar(fig, "f1_ejemplo.pdf")


# 2. Ejemplo: columnas con el valor escrito (una serie: el primer color de SERIES) ---------
# Fuente: <archivo o fila del registro de donde salen los valores>
def ejemplo_categorias():
    fig, ax = figura(alto_mm=40, ancho=0.5)
    barras = ax.bar(["2023", "2024", "2025"], [310, 420, 380], color=SERIES[0], width=0.6)
    rotular(ax, barras)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title("Clientes nuevos por año")
    guardar(fig, "f2_categorias.pdf")


if __name__ == "__main__":
    # Una llamada por gráfico del documento, en orden. Los ejemplos no se llaman: la
    # plantilla los usa como fig/f1_ejemplo.pdf y fig/f2_categorias.pdf.
    # ejemplo()
    # ejemplo_categorias()
    pass
