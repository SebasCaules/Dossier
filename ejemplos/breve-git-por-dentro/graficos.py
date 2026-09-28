"""Gráficos del documento. Uso: python3 graficos.py (escribe en fig/).

Los datos salen de correr demo.sh, que arma el repositorio de prueba y al final imprime,
por commit, cuántos objetos escribe y cuántos reutiliza.
"""
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # sin __pycache__ en la carpeta del documento

from estilo_graficos import P, figura, guardar, texto_sobre  # noqa: E402

AQUI = Path(__file__).resolve().parent


def conteo_por_commit():
    """[(mensaje, escritos, reutilizados)] en el orden de la historia (sección 7 de demo.sh)."""
    salida = subprocess.run(["sh", str(AQUI / "demo.sh")], capture_output=True, text=True,
                            check=True).stdout
    filas = salida.split("## 7.", 1)[1].splitlines()[1:]
    return [(m, int(n), int(r)) for m, n, r in (f.split("|") for f in filas if "|" in f)]


# 1. Objetos que escribe cada commit y objetos que reutiliza --------------------------
# Fuente: demo.sh, sección 7. «Escritos» incluye el propio commit; «reutilizados» son las
# entradas de sus trees que ya existían en un commit anterior.
def escritos_y_reutilizados():
    datos = conteo_por_commit()
    nombres = {"Merge branch 'sopa'": "Merge de sopa", "README con las tres recetas": "README nuevo"}
    etiquetas = [f"{i}. {nombres.get(m, m)}" for i, (m, _, _) in enumerate(datos, 1)]
    escritos = [n for _, n, _ in datos]
    reusados = [r for _, _, r in datos]
    fuerte, gris = P["acento"], P["linea"]

    fig, ax = figura(alto_mm=46, ancho=0.56)
    ys = list(range(len(datos)))[::-1]  # el primer commit arriba
    b1 = ax.barh(ys, escritos, color=fuerte, height=0.62, edgecolor="white", linewidth=1.5,
                 label="escritos")
    b2 = ax.barh(ys, reusados, left=escritos, color=gris, height=0.62, edgecolor="white",
                 linewidth=1.5, label="reutilizados")
    for barras, color in ((b1, fuerte), (b2, gris)):
        for b in barras:
            if b.get_width() > 0:
                ax.text(b.get_x() + b.get_width() / 2, b.get_y() + b.get_height() / 2,
                        str(int(b.get_width())), ha="center", va="center",
                        color=texto_sobre(color), fontweight="semibold")
    ax.set_yticks(ys, etiquetas)
    ax.tick_params(axis="y", length=0)
    for lado in ("left", "bottom", "top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_xticks([])
    ax.set_xlim(0, max(n + r for n, r in zip(escritos, reusados)) + 0.2)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False,
              handlelength=1.2, borderaxespad=0.2)
    guardar(fig, "f1_escritos_reutilizados.pdf")


if __name__ == "__main__":
    escritos_y_reutilizados()
