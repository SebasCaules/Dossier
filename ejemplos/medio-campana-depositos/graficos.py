"""Gráficos y cifras del documento. Uso: python3 graficos.py (escribe en fig/).

Todos los datos salen de un solo archivo público: bank-additional-full.csv, del dataset
Bank Marketing de UCI (Moro, Cortez y Rita, 2014; licencia CC BY 4.0). No viene con el
ejemplo: se baja de https://archive.ics.uci.edu/dataset/222/bank+marketing y se deja en
datos/bank-additional-full.csv (el README lo explica).

Cada fila es un cliente contactado en una campaña de depósitos a plazo de un banco
portugués, de mayo de 2008 a noviembre de 2010, en orden de fecha. La columna `duration`
(duración de la última llamada) solo se conoce después de llamar: no se usa para decidir
a quién llamar.

`python3 graficos.py cifras` imprime, además, cada cifra que cita el texto.
"""
import sys

sys.dont_write_bytecode = True  # sin __pycache__ en la carpeta del documento

from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from estilo_graficos import P, SERIES, barras_h, figura, guardar, num, pct, rotular  # noqa: E402

DATOS = Path(__file__).resolve().parent / "datos" / "bank-additional-full.csv"
MESES = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
GRIS = P.get("linea", "#b9c0cc")
ACENTO = P.get("acento", "#22456f")
TINTA = P.get("tinta", "#16233a")


def cargar():
    if not DATOS.exists():
        sys.exit(f"Falta {DATOS.name}: bajarlo de "
                 "https://archive.ics.uci.edu/dataset/222/bank+marketing y dejarlo en datos/.")
    d = pd.read_csv(DATOS, sep=";")
    d["si"] = (d.y == "yes").astype(int)
    d["mes"] = d.month.map({m: i + 1 for i, m in enumerate(MESES)})
    # El archivo está en orden de fecha y empieza en mayo de 2008: el año sube cada vez que
    # el mes vuelve atrás. Es una reconstrucción (el archivo no trae el año).
    d["anio"] = 2008 + (d.mes.diff() < 0).cumsum()
    return d


def grupo(d):
    """Orden de llamada propuesto: A, B, C, D (ver la sección «A quién llamar primero»)."""
    a = d.poutcome == "success"
    b = ~a & ((d.poutcome == "failure") | (d.age <= 24) | (d.age >= 60))
    c = ~a & ~b & (d.contact == "cellular")
    return pd.Series(np.select([a, b, c], ["A", "B", "C"], "D"), index=d.index)


def tasa(x):
    return 100 * x.mean()


# 1. Resultado de la campaña anterior -------------------------------------------------
# Fuente: columna poutcome (resultado de la campaña anterior) y y.
def resultado_anterior(d):
    g = d.groupby("poutcome").si.apply(tasa)
    etiquetas = {"success": "Aceptó", "failure": "No aceptó", "nonexistent": "Sin campaña anterior"}
    fig, ax = figura(alto_mm=26, ancho=0.3)
    barras_h(ax, [etiquetas[k] for k in g.index], list(g.values), destacar="Aceptó", fmt=pct)
    ax.set_title("Según la campaña anterior")
    guardar(fig, "f01_anterior.pdf")


# 2. Edad ------------------------------------------------------------------------------
# Fuente: columna age y y.
def edad(d):
    cortes = [0, 24, 29, 39, 49, 59, 200]
    nombres = ["hasta\n24", "25\na 29", "30\na 39", "40\na 49", "50\na 59", "60\no más"]
    g = d.groupby(pd.cut(d.age, cortes, labels=nombres), observed=True).si.apply(tasa)
    fig, ax = figura(alto_mm=34, ancho=0.46)
    colores = [ACENTO if k in ("hasta\n24", "60\no más") else GRIS for k in g.index]
    barras = ax.bar(range(len(g)), g.values, color=colores, width=0.62)
    rotular(ax, barras, fmt=lambda v: pct(v, 0))
    ax.set_xticks(range(len(g)), g.index)
    ax.tick_params(axis="x", length=0)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title("Según la edad")
    guardar(fig, "f02_edad.pdf")


# 3. Ocupación -------------------------------------------------------------------------
# Fuente: columna job y y. «unknown» (330 clientes) queda afuera.
def ocupacion(d):
    nombres = {"student": "Estudiante", "retired": "Jubilado", "unemployed": "Desempleado",
               "admin.": "Administrativo", "management": "Gerencia", "technician": "Técnico",
               "self-employed": "Independiente", "housemaid": "Servicio doméstico",
               "entrepreneur": "Empresario", "services": "Servicios", "blue-collar": "Obrero"}
    x = d[d.job != "unknown"]
    g = x.groupby("job").si.apply(tasa)
    fig, ax = figura(alto_mm=50, ancho=0.36)
    barras_h(ax, [nombres[k] for k in g.index], list(g.values),
             destacar=["Estudiante", "Jubilado"], fmt=pct)
    ax.set_title("Según la ocupación")
    guardar(fig, "f03_ocupacion.pdf")


# 4. Tipo de teléfono, según la campaña anterior ----------------------------------------
# Fuente: columnas contact, poutcome y y.
def telefono(d):
    orden = [("success", "Aceptó\nantes"), ("failure", "No aceptó\nantes"),
             ("nonexistent", "Sin campaña\nanterior")]
    fig, ax = figura(alto_mm=40, ancho=0.46)
    ancho = 0.36
    for j, (tipo, nombre, color) in enumerate([("cellular", "Celular", SERIES[0]),
                                               ("telephone", "Fijo", SERIES[1])]):
        vals = [tasa(d[(d.poutcome == p) & (d.contact == tipo)].si) for p, _ in orden]
        xs = np.arange(len(orden)) + (j - 0.5) * (ancho + 0.03)
        barras = ax.bar(xs, vals, width=ancho, color=color, label=nombre)
        rotular(ax, barras, fmt=lambda v: pct(v, 0))
    ax.set_xticks(range(len(orden)), [n for _, n in orden])
    ax.tick_params(axis="x", length=0)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper right", handlelength=1, handleheight=0.8, fontsize=8)
    ax.set_title("Según el teléfono")
    guardar(fig, "f04_telefono.pdf")


# 5. Curva de ganancia: la lista ordenada contra el azar ---------------------------------
# Fuente: las columnas que se conocen antes de llamar. Quedan afuera duration (se conoce al
# cortar) y campaign, month y day_of_week (el total de intentos y la fecha del último
# contacto se conocen al terminar la campaña). Se arma con las campañas hasta abril de 2009
# y se prueba con las de mayo de 2009 a noviembre de 2010.
def prueba(d):
    from sklearn.ensemble import HistGradientBoostingClassifier

    antes = (d.anio < 2009) | ((d.anio == 2009) & (d.mes <= 4))
    x = d.drop(columns=["y", "si", "duration", "campaign", "month", "day_of_week", "anio", "mes"])
    x = pd.get_dummies(x, columns=[c for c in x.columns if x[c].dtype == object])
    modelo = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=0)
    modelo.fit(x[antes], d.si[antes])
    puntaje = modelo.predict_proba(x[~antes])[:, 1]
    return antes, puntaje


def curva(puntaje, y):
    """Parte acumulada de los depósitos al llamar en orden de puntaje. Los empates (los
    grupos A a D) se reparten en proporción: dentro de un grupo, el orden es al azar."""
    t = pd.DataFrame({"p": puntaje, "y": np.asarray(y)})
    g = t.groupby("p").y.agg(["size", "sum"]).sort_index(ascending=False)
    xs = np.concatenate([[0], g["size"].cumsum() / len(t)])
    ys = np.concatenate([[0], g["sum"].cumsum() / t.y.sum()])
    return xs, ys


def ganancia(d):
    antes, puntaje = prueba(d)
    despues = d[~antes]
    regla = grupo(despues).map({"A": 3, "B": 2, "C": 1, "D": 0}).values
    fig, ax = figura(alto_mm=62, ancho=0.5)
    ax.plot([0, 100], [0, 100], color=GRIS, lw=1.2, ls=(0, (3, 2)), label="Al azar")
    for s, nombre, color in [(regla, "Grupos A a D", SERIES[0]),
                             (puntaje, "Puntaje estadístico", SERIES[1])]:
        xs, ys = curva(s, despues.si)
        ax.plot(100 * xs, 100 * ys, color=color, lw=2, label=nombre)
    ax.axvline(20, color=GRIS, lw=0.6)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xticks([0, 20, 40, 60, 80, 100], ["0", "20 %", "40 %", "60 %", "80 %", "100 %"])
    ax.set_yticks([0, 20, 40, 60, 80, 100], ["0", "20 %", "40 %", "60 %", "80 %", "100 %"])
    ax.set_xlabel("parte de la lista llamada, en orden")
    ax.set_ylabel("parte de los depósitos")
    ax.grid(color=P.get("fondo", "#eef1f5"), lw=0.6)
    ax.legend(loc="lower right", handlelength=1.6, fontsize=8)
    ax.set_title("Depósitos conseguidos al llamar en orden")
    guardar(fig, "f05_ganancia.pdf")


# 6. Mes a mes: clientes llamados y parte que aceptó -----------------------------------
# Fuente: columnas month (y el año reconstruido por el orden del archivo) y y.
def meses(d):
    g = d.groupby(["anio", "mes"]).si.agg(["size", "mean"])
    pos = [(a - 2008) * 12 + m - 5 for a, m in g.index]  # 0 = mayo de 2008
    fig, (ax1, ax2) = figura(alto_mm=100, ancho=1.0, nrows=2, sharex=True)
    ax1.bar(pos, g["size"], color=GRIS, width=0.7)
    ax1.set_yticks([0, 4000, 8000], ["0", "4.000", "8.000"])
    ax1.set_title("Clientes llamados por mes")
    chico = (g["size"] < 100).values  # meses con menos de 100 clientes: punto hueco
    for i in range(1, len(pos)):  # la línea no cruza los meses sin llamadas
        if pos[i] - pos[i - 1] == 1:
            ax2.plot(pos[i - 1:i + 1], 100 * g["mean"].iloc[i - 1:i + 1], color=ACENTO, lw=1.5)
    xs, ys = [p for p, c in zip(pos, chico) if not c], [v for v, c in zip(100 * g["mean"], chico) if not c]
    ax2.plot(xs, ys, color=ACENTO, lw=0, marker="o", ms=3.5)
    xs, ys = [p for p, c in zip(pos, chico) if c], [v for v, c in zip(100 * g["mean"], chico) if c]
    ax2.plot(xs, ys, color=ACENTO, lw=0, marker="o", ms=3.5, mfc="white", mew=1.2)
    ax2.set_yticks([0, 20, 40, 60], ["0", "20 %", "40 %", "60 %"])
    ax2.set_ylim(0, 70)
    ax2.set_title("Parte que aceptó el depósito")
    ax2.grid(axis="y", color=P.get("fondo", "#eef1f5"), lw=0.6)
    marcas = [p for p in range(0, 31) if (p + 5 - 1) % 12 + 1 in (5, 11)]
    ax2.set_xticks(marcas, [f"{MESES_ES[(p + 4) % 12]} {2008 + (p + 4) // 12}" for p in marcas])
    ax2.tick_params(axis="x", length=0)
    for a in (2009, 2010):
        for ax in (ax1, ax2):
            ax.axvline((a - 2008) * 12 - 4.5, color=GRIS, lw=0.6, ls=(0, (2, 2)))
    fig.subplots_adjust(hspace=0.45)
    guardar(fig, "f06_meses.pdf")


# 7. Euríbor ---------------------------------------------------------------------------
# Fuente: columna euribor3m (indicador diario del Banco de Portugal, según la
# descripción del dataset) y y.
def euribor(d):
    cortes = [0, 1, 3, 6]
    nombres = ["menos de 1 %", "1 a 3 %", "3 % o más"]
    b = pd.cut(d.euribor3m, cortes, labels=nombres)
    g = d.groupby(b, observed=True).si.apply(tasa)
    fig, ax = figura(alto_mm=30, ancho=0.34)
    barras_h(ax, list(g.index), list(g.values), destacar="menos de 1 %", fmt=pct)
    ax.set_title("Según el euríbor a 3 meses")
    guardar(fig, "f07_euribor.pdf")


# 8. Día de la semana, año por año ------------------------------------------------------
# Fuente: columna day_of_week, el año reconstruido y y.
def dias(d):
    orden = ["mon", "tue", "wed", "thu", "fri"]
    nombres = ["lu", "ma", "mi", "ju", "vi"]
    fig, ejes = figura(alto_mm=48, ancho=0.6, ncols=3)
    for ax, anio in zip(ejes, (2008, 2009, 2010)):
        x = d[d.anio == anio]
        g = x.groupby("day_of_week").si.apply(tasa).reindex(orden)
        barras = ax.bar(range(5), g.values, width=0.66,
                        color=[ACENTO if k == "mon" else GRIS for k in orden])
        for b in barras:
            ax.annotate(num(b.get_height(), 1), (b.get_x() + b.get_width() / 2, b.get_height()),
                        xytext=(0, 2), textcoords="offset points", ha="center", va="bottom",
                        fontsize=6.5, color=TINTA)
        ax.set_ylim(0, max(g.values) * 1.2)
        ax.set_xticks(range(5), nombres)
        ax.tick_params(axis="x", length=0, labelsize=7.5)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_title(str(anio), fontsize=8.5)
    fig.subplots_adjust(wspace=0.15)
    guardar(fig, "f08_dias.pdf")


# 9. Depósitos cada 100 llamadas, según el intento ---------------------------------------
# Fuente: columna campaign (contactos con el cliente en esta campaña, incluido el último)
# y y. El intento k lo recibieron los clientes con campaign >= k; el depósito se cuenta en
# el último contacto (campaign == k y y == yes).
def por_intento(d):
    ks = range(1, 11)
    llamadas = [(d.campaign >= k).sum() for k in ks]
    depositos = [((d.campaign == k) & (d.si == 1)).sum() for k in ks]
    v = [100 * s / n for s, n in zip(depositos, llamadas)]
    fig, ax = figura(alto_mm=66, ancho=0.46)
    barras = ax.bar(list(ks), v, width=0.66, color=[ACENTO if k <= 3 else GRIS for k in ks])
    rotular(ax, barras, fmt=lambda x: num(x, 1))
    ax.set_xticks(list(ks), [str(k) for k in ks])
    ax.tick_params(axis="x", length=0)
    ax.set_xlabel("intento")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_title("Depósitos cada 100 llamadas")
    guardar(fig, "f09_intento.pdf")


# 10. Acumulado: llamadas y depósitos hasta el intento k ---------------------------------
# Fuente: columna campaign y y, como en el gráfico 9.
def acumulado(d):
    ks = np.arange(1, d.campaign.max() + 1)
    llamadas = np.array([(d.campaign >= k).sum() for k in ks]).cumsum() / d.campaign.sum()
    depositos = np.array([((d.campaign == k) & (d.si == 1)).sum() for k in ks]).cumsum() / d.si.sum()
    ks, llamadas, depositos = ks[:10], 100 * llamadas[:10], 100 * depositos[:10]
    fig, ax = figura(alto_mm=74, ancho=0.7)
    ax.plot(ks, depositos, color=SERIES[0], lw=2, marker="o", ms=3.5, label="Depósitos")
    ax.plot(ks, llamadas, color=SERIES[1], lw=2, marker="o", ms=3.5, label="Llamadas")
    for serie, dx, dy in ((depositos, -4, 5), (llamadas, 5, -12)):
        ax.annotate(pct(serie[2], 0), (3, serie[2]), xytext=(dx, dy), textcoords="offset points",
                    ha="right" if dx < 0 else "left", color=TINTA, fontweight="semibold")
    ax.axvline(3, color=GRIS, lw=0.6)
    ax.set_xticks(list(ks), [str(k) for k in ks])
    ax.tick_params(axis="x", length=0)
    ax.set_xlabel("hasta el intento")
    ax.set_ylim(30, 105)
    ax.set_yticks([40, 60, 80, 100], ["40 %", "60 %", "80 %", "100 %"])
    ax.grid(axis="y", color=P.get("fondo", "#eef1f5"), lw=0.6)
    ax.legend(loc="lower right", handlelength=1.4, fontsize=8)
    ax.set_title("Parte del total, acumulada")
    guardar(fig, "f10_acumulado.pdf")


# 11. Llamadas por depósito, según el grupo ---------------------------------------------
# Fuente: columna campaign (llamadas a cada cliente en la campaña) y y, por grupo A a D.
def costo_grupo(d):
    g = d.groupby(grupo(d)).agg(llamadas=("campaign", "sum"), depositos=("si", "sum"))
    v = g.llamadas / g.depositos
    fig, ax = figura(alto_mm=26, ancho=0.5)
    barras_h(ax, [f"Grupo {k}" for k in v.index], list(v.values), destacar="Grupo A",
             fmt=lambda x: num(x, 1))
    ax.set_title("Llamadas por cada depósito")
    guardar(fig, "f11_costo.pdf")


# 12. Los grupos, antes y después de abril de 2009 ----------------------------------------
# Fuente: grupo A a D y y, separando las campañas hasta abril de 2009 y las posteriores.
def grupos_periodo(d):
    antes = (d.anio < 2009) | ((d.anio == 2009) & (d.mes <= 4))
    fig, ax = figura(alto_mm=50, ancho=0.46)
    ancho = 0.36
    for j, (filtro, nombre, color) in enumerate([(antes, "hasta abr 2009", SERIES[0]),
                                                 (~antes, "desde may 2009", SERIES[1])]):
        x = d[filtro]
        v = x.groupby(grupo(x)).si.apply(tasa).reindex(list("ABCD"))
        xs = np.arange(4) + (j - 0.5) * (ancho + 0.03)
        barras = ax.bar(xs, v.values, width=ancho, color=color, label=nombre)
        rotular(ax, barras, fmt=lambda t: num(t, 0))
    ax.set_xticks(range(4), [f"Grupo {k}" for k in "ABCD"])
    ax.tick_params(axis="x", length=0)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper right", handlelength=1, handleheight=0.8, fontsize=8)
    ax.set_title("Aceptan, en %, por grupo")
    guardar(fig, "f12_periodos.pdf")


# 13. Hipoteca, préstamo y mora -----------------------------------------------------------
# Fuente: columnas housing, loan, default y y. «unknown» de hipoteca y préstamo (990
# clientes) y mora «yes» (3 clientes) quedan afuera.
def datos_financieros(d):
    paneles = [("housing", "Hipoteca", [("yes", "sí"), ("no", "no")]),
               ("loan", "Préstamo personal", [("yes", "sí"), ("no", "no")]),
               ("default", "Mora", [("no", "no"), ("unknown", "sin dato")])]
    fig, ejes = figura(alto_mm=46, ancho=0.85, ncols=3)
    for ax, (col, titulo, cats) in zip(ejes, paneles):
        v = [tasa(d[d[col] == c].si) for c, _ in cats]
        colores = [ACENTO if c == "unknown" else GRIS for c, _ in cats]
        barras = ax.bar(range(len(cats)), v, width=0.6, color=colores)
        rotular(ax, barras, fmt=lambda t: pct(t, 1))
        ax.set_ylim(0, 16)
        ax.set_xticks(range(len(cats)), [n for _, n in cats])
        ax.tick_params(axis="x", length=0)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_title(titulo, fontsize=8.5)
    fig.subplots_adjust(wspace=0.25)
    guardar(fig, "f13_financieros.pdf")


# 14. Intentos 1 a 3 contra 4 o más, por grupo ------------------------------------------
# Fuente: columna campaign y y, por grupo A a D. Llamadas de los intentos 1 a 3: la suma de
# min(campaign, 3); del 4 en adelante: la suma de max(campaign - 3, 0). Cada depósito se
# cuenta en el último contacto, como en el gráfico 9.
def intentos_grupo(d):
    g = grupo(d)
    filas = []
    for k in "ABCD":
        x = d[g == k]
        pocos = 100 * ((x.campaign <= 3) & (x.si == 1)).sum() / x.campaign.clip(upper=3).sum()
        muchos = 100 * ((x.campaign > 3) & (x.si == 1)).sum() / (x.campaign - 3).clip(lower=0).sum()
        filas.append((pocos, muchos))
    fig, ax = figura(alto_mm=66, ancho=0.46)
    ancho = 0.36
    for j, (nombre, color) in enumerate([("intentos 1 a 3", SERIES[0]), ("4 o más", SERIES[1])]):
        xs = np.arange(4) + (j - 0.5) * (ancho + 0.03)
        barras = ax.bar(xs, [f[j] for f in filas], width=ancho, color=color, label=nombre)
        rotular(ax, barras, fmt=lambda t: num(t, 1))
    ax.set_ylim(0, max(f[0] for f in filas) * 1.18)  # rotular fija el tope con la última serie
    ax.set_xticks(range(4), [f"Grupo {k}" for k in "ABCD"])
    ax.tick_params(axis="x", length=0)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper right", handlelength=1, handleheight=0.8, fontsize=8)
    ax.set_title("Depósitos cada 100 llamadas, por grupo")
    guardar(fig, "f14_intentos_grupo.pdf")


def cifras(d):
    """Cada cifra que cita el texto, con la cuenta que la produce."""
    total, si = len(d), d.si.sum()
    print(f"Clientes {total} · depósitos {si} ({100 * si / total:.2f} %) · llamadas "
          f"{d.campaign.sum()} · llamadas por depósito {d.campaign.sum() / si:.2f}")
    print("Período:", d.anio.min(), MESES_ES[d.mes.iloc[0] - 1], "a", d.anio.max(),
          MESES_ES[d.mes.iloc[-1] - 1])
    print("Por año (clientes, % acepta):")
    print(d.groupby("anio").si.agg(["size", "mean"]).round(4).to_string())
    for col in ("poutcome", "contact", "day_of_week"):
        print(d.groupby(col).si.agg(["size", "sum", "mean"]).round(4).to_string())
    print(pd.crosstab([d.poutcome], d.contact, values=d.si, aggfunc="mean").round(4))
    print(pd.crosstab([d.poutcome], d.contact))
    print("Edad:", d.groupby(pd.cut(d.age, [0, 24, 59, 200]), observed=True).si
          .agg(["size", "mean"]).round(4).to_string())
    print("Estudiantes hasta 24:", round((d[d.job == "student"].age <= 24).mean(), 3),
          "· jubilados 60 o más:", round((d[d.job == "retired"].age >= 60).mean(), 3))
    g = grupo(d)
    t = d.groupby(g).si.agg(["size", "sum", "mean"])
    t["parte_lista"] = t["size"] / total
    t["parte_depositos"] = t["sum"] / si
    print("Grupos, todo el período:\n", t.round(4).to_string())
    antes, puntaje = prueba(d)
    for nombre, x in (("hasta abr 2009", d[antes]), ("desde may 2009", d[~antes])):
        gg = x.groupby(grupo(x)).si.agg(["size", "mean"])
        print(f"Grupos, {nombre}: {len(x)} clientes, acepta {100 * x.si.mean():.2f} %\n",
              gg.round(4).to_string())
    despues = d[~antes]
    for s, nombre in ((grupo(despues).map({"A": 3, "B": 2, "C": 1, "D": 0}).values, "regla"),
                      (puntaje, "puntaje")):
        xs, ys = curva(s, despues.si)
        print(f"Ganancia {nombre} al 20 %: {100 * np.interp(0.2, xs, ys):.1f} % · "
              f"al 50 %: {100 * np.interp(0.5, xs, ys):.1f} %")
    ks = range(1, d.campaign.max() + 1)
    llam = {k: (d.campaign >= k).sum() for k in ks}
    dep = {k: ((d.campaign == k) & (d.si == 1)).sum() for k in ks}
    for k in range(1, 11):
        print(f"intento {k}: llamadas {llam[k]}, depósitos {dep[k]}, cada 100: "
              f"{100 * dep[k] / llam[k]:.2f}")
    l3, d3 = sum(llam[k] for k in range(1, 4)), sum(dep[k] for k in range(1, 4))
    print(f"Intentos 1 a 3: llamadas {l3} ({100 * l3 / d.campaign.sum():.1f} %), depósitos "
          f"{d3} ({100 * d3 / si:.1f} %), cada 100: {100 * d3 / l3:.2f}")
    print(f"Intentos 4 o más: llamadas {d.campaign.sum() - l3}, depósitos {si - d3}, cada 100: "
          f"{100 * (si - d3) / (d.campaign.sum() - l3):.2f}")
    print("Más de 10 intentos:", (d.campaign > 10).sum(), "clientes,",
          d[d.campaign > 10].si.sum(), "depósitos · máximo", d.campaign.max())
    print("Euríbor:", d.groupby(pd.cut(d.euribor3m, [0, 1, 3, 6]), observed=True).si
          .agg(["size", "mean"]).round(4).to_string())
    m = d.groupby(["anio", "mes"]).si.agg(["size", "mean"])
    print("Meses con datos:", len(m), "· corr(log clientes, % acepta):",
          round(np.corrcoef(np.log(m["size"]), m["mean"])[0, 1], 2))
    print("Mayo 2008:", m.loc[(2008, 5)].round(4).to_dict(), "· 2010 promedio mensual de clientes:",
          round(m.loc[2010]["size"].mean()))
    print(m.round(3).to_string())
    t = d.groupby(g).agg(llamadas=("campaign", "sum"), depositos=("si", "sum"))
    print("Llamadas por depósito, por grupo:", (t.llamadas / t.depositos).round(2).to_dict())
    a = d.groupby("anio").agg(llamadas=("campaign", "sum"), depositos=("si", "sum"),
                              celular=("contact", lambda x: (x == "cellular").mean()))
    a["por_deposito"] = a.llamadas / a.depositos
    print("Por año:\n", a.round(3).to_string())
    for col in ("housing", "loan", "default", "marital", "education"):
        print(d.groupby(col).si.agg(["size", "mean"]).round(4).to_string())
    for k in "ABCD":
        x = d[g == k]
        l4 = (x.campaign - 3).clip(lower=0).sum()
        d4 = ((x.campaign > 3) & (x.si == 1)).sum()
        l13 = x.campaign.clip(upper=3).sum()
        d13 = ((x.campaign <= 3) & (x.si == 1)).sum()
        print(f"Grupo {k}: intentos 1 a 3 {l13} llamadas, {d13} depósitos ({100 * d13 / l13:.2f} "
              f"cada 100) · 4 o más {l4} llamadas, {d4} depósitos ({100 * d4 / l4:.2f} cada 100)")
    bcd = d[g != "A"]
    l4 = (bcd.campaign - 3).clip(lower=0).sum()
    d4 = ((bcd.campaign > 3) & (bcd.si == 1)).sum()
    print(f"Tope en B, C y D: {l4} llamadas menos ({100 * l4 / d.campaign.sum():.1f} %), hasta "
          f"{d4} depósitos ({100 * d4 / si:.1f} %)")
    print("Euríbor 2008: mínimo", d[d.anio == 2008].euribor3m.min(), "· desde 2009: máximo",
          d[d.anio > 2008].euribor3m.max())


if __name__ == "__main__":
    datos = cargar()
    if sys.argv[1:] == ["cifras"]:
        cifras(datos)
        sys.exit()
    for f in (resultado_anterior, edad, ocupacion, telefono, ganancia, meses, euribor, dias,
              por_intento, acumulado, costo_grupo, grupos_periodo, datos_financieros, intentos_grupo):
        f(datos)
