"""Gráficos del documento. Uso: python3 graficos.py (escribe en fig/).

Una función por gráfico, con la fuente de sus datos en el comentario.
"""
import sys

sys.dont_write_bytecode = True  # sin __pycache__ en la carpeta del documento

from estilo_graficos import P, SERIES, figura, guardar, texto_sobre  # noqa: E402


# 1. Viajes de ida y vuelta (RTT) hasta la primera respuesta HTTP ----------------------
# Cuenta propia a partir de los diagramas de mensajes de las fuentes; la consulta DNS no
# entra (depende del resolvedor y de su caché):
#   TCP: RFC 9293, figura 6. El cliente queda ESTABLISHED al recibir el SYN,ACK: 1 RTT.
#   TLS 1.2: RFC 5246, figura 1. Los datos de la aplicación van después del Finished
#            del servidor: 2 RTT.
#   TLS 1.3: RFC 8446, figura 1. El cliente manda su Finished y los datos después del
#            primer vuelo del servidor: 1 RTT. Con HelloRetryRequest (figura 2), el
#            ClientHello se repite: 2 RTT. Con 0-RTT (figura 4), la petición viaja con el
#            ClientHello: 0 RTT antes de la petición.
#   HTTP: la petición y su respuesta, 1 RTT (RFC 9110, sección 4.3.3: la petición se
#         envía por la conexión ya asegurada).
CASOS = [  # (rótulo, TCP, TLS, HTTP)
    ("TLS 1.2", 1, 2, 1),
    ("TLS 1.3", 1, 1, 1),
    ("TLS 1.3 con\nHelloRetryRequest", 1, 2, 1),
    ("TLS 1.3 con 0-RTT\n(reanudación)", 1, 0, 1),
]
TRAMOS = [("TCP", SERIES[0]), ("TLS", SERIES[1]), ("HTTP", SERIES[2])]


def viajes():
    fig, ax = figura(alto_mm=46, ancho=0.56)
    casos = CASOS[::-1]  # barh dibuja de abajo hacia arriba
    ys = range(len(casos))
    izquierda = [0] * len(casos)
    for k, (nombre, color) in enumerate(TRAMOS):
        valores = [c[k + 1] for c in casos]
        barras = ax.barh(list(ys), valores, left=izquierda, color=color, height=0.6,
                         edgecolor="white", linewidth=1.2, label=nombre)
        for barra, v in zip(barras, valores):
            if v:
                ax.text(barra.get_x() + v / 2, barra.get_y() + barra.get_height() / 2, str(v),
                        ha="center", va="center", color=texto_sobre(color), fontsize=7)
        izquierda = [a + b for a, b in zip(izquierda, valores)]
    for y, total in zip(ys, izquierda):
        ax.text(total + 0.08, y, f"{total} RTT", va="center", ha="left", color=P["tinta"],
                fontweight="semibold" if casos[y][0] == "TLS 1.3" else "normal")
    ax.set_yticks(list(ys), [c[0] for c in casos])
    ax.tick_params(axis="y", length=0)
    for lado in ("left", "bottom", "top", "right"):
        ax.spines[lado].set_visible(False)
    ax.set_xticks([])
    ax.set_xlim(0, 5.1)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, frameon=False,
              handlelength=1.0, handleheight=0.8, columnspacing=1.2, borderaxespad=0.2)
    guardar(fig, "f1_viajes.pdf")


if __name__ == "__main__":
    viajes()
