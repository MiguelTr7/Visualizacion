# -*- coding: utf-8 -*-
"""
StreamView Analytics - Analisis exploratorio (CRISP-DM Fase 4)

Genera las visualizaciones del informe ejecutivo a partir de los datos
procesados. Cada figura responde a una pregunta de negocio explicita y
justifica su tipo de grafico segun la naturaleza de los datos.

Uso:  python src/eda_visualizaciones.py
"""
from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

sys.path.insert(0, str(Path(__file__).parent))
import estilo
from estilo import ROJO, AZUL, CARBON, GRIS, NARANJA, VERDE, TIPO_COLOR

PROC = Path("data/processed")
IMG = Path("images")


def cargar():
    catalogo = pd.read_csv(PROC / "catalogo_unificado.csv")
    generos = pd.read_csv(PROC / "catalogo_generos.csv")
    peliculas = pd.read_csv(PROC / "peliculas_limpio.csv")
    return catalogo, generos, peliculas


def guardar(fig, nombre):
    IMG.mkdir(exist_ok=True)
    fig.savefig(IMG / f"{nombre}.png")
    plt.close(fig)
    print(f"  images/{nombre}.png")


# Candidatos de posicion probados en orden para cada etiqueta: arriba,
# abajo, y luego desplazamientos laterales.
_OFFSETS = [(0, 15), (0, -21), (46, 4), (-46, 4), (52, -14), (-52, -14),
            (0, 29), (0, -35), (70, 16), (-70, 16)]


def etiquetar_sin_colision(ax, xs, ys, textos, fontsize=9.5):
    """Coloca etiquetas junto a cada punto evitando que se superpongan.

    Recorre los puntos de mayor a menor valor en Y y para cada uno elige el
    primer desplazamiento candidato cuyo rectangulo de texto no choque con
    los ya asignados. Sin esto las etiquetas de generos cercanos quedan
    ilegibles unas sobre otras.
    """
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    log_x = ax.get_xscale() == "log"

    def a_fraccion(x, y):
        fx = ((np.log10(x) - np.log10(x0)) / (np.log10(x1) - np.log10(x0))
              if log_x else (x - x0) / (x1 - x0))
        return fx, (y - y0) / (y1 - y0)

    ocupados = []
    orden = np.argsort(-np.asarray(ys, dtype=float))
    xs, ys, textos = list(xs), list(ys), list(textos)

    for i in orden:
        fx, fy = a_fraccion(xs[i], ys[i])
        ancho = len(str(textos[i])) * 0.0072 * (fontsize / 9.5)
        alto = 0.030
        for dx, dy in _OFFSETS:
            cx = fx + dx / 900.0
            cy = fy + dy / 620.0
            caja = (cx - ancho / 2, cy - alto / 2, cx + ancho / 2, cy + alto / 2)
            choca = any(not (caja[2] < o[0] or caja[0] > o[2] or
                             caja[3] < o[1] or caja[1] > o[3]) for o in ocupados)
            if not choca:
                ocupados.append(caja)
                ax.annotate(textos[i], (xs[i], ys[i]), textcoords="offset points",
                            xytext=(dx, dy), ha="center", fontsize=fontsize,
                            color=CARBON)
                break


# --------------------------------------------------------------------------
# 1. Composicion del catalogo por genero
#    Pregunta: en que generos esta concentrada la oferta?
#    Grafico: barras horizontales agrupadas. Categorias nominales con
#    etiquetas largas -> la orientacion horizontal evita rotar el texto, y
#    la longitud es el atributo visual mas preciso para comparar magnitudes.
# --------------------------------------------------------------------------
def fig_composicion_generos(generos):
    conteo = generos.groupby(["genero", "tipo"]).size().unstack(fill_value=0)
    conteo["total"] = conteo.sum(axis=1)
    conteo = conteo.sort_values("total", ascending=True).tail(12)

    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(conteo))
    alto = 0.4
    ax.barh(y + alto / 2, conteo["Película"], alto, color=ROJO, label="Películas")
    ax.barh(y - alto / 2, conteo["Serie"], alto, color=AZUL, label="Series")
    ax.set_yticks(y)
    ax.set_yticklabels(conteo.index)
    ax.set_xlabel("Cantidad de títulos")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: estilo.miles(v)))
    estilo.solo_eje_x(ax)

    # Una barra en cero se leeria como "no existe ese contenido", cuando en
    # realidad la categoria no existe en la taxonomia de origen de ese
    # formato. Se advierte explicitamente para no inducir a error.
    for i, (nombre, fila) in enumerate(conteo.iterrows()):
        if fila["Serie"] == 0:
            ax.text(120, i - alto / 2, "categoría no disponible para series",
                    va="center", fontsize=8.5, color="#8A8A8A", style="italic")

    estilo.titular(
        ax,
        "Drama y Comedia concentran la oferta en ambos formatos",
        "Títulos por género y tipo de contenido · Top 12 géneros",
    )
    ax.legend(loc="lower right")
    estilo.fuente(fig)
    guardar(fig, "01_composicion_generos")
    return conteo


# --------------------------------------------------------------------------
# 2. Distribucion de calificaciones
#    Pregunta: como se distribuye la calidad percibida del catalogo?
#    Grafico: histograma. Variable continua -> revela forma, centro y
#    dispersion, informacion que un promedio aislado ocultaria.
# --------------------------------------------------------------------------
def fig_distribucion_calificaciones(catalogo):
    cal = catalogo[catalogo["calificado"]]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bins = np.arange(0, 10.4, 0.4)
    resumen = {}
    for tipo in ("Película", "Serie"):
        datos = cal.loc[cal["tipo"] == tipo, "vote_average"]
        etiqueta = "Películas" if tipo == "Película" else "Series"
        ax.hist(datos, bins=bins, alpha=0.65, color=TIPO_COLOR[tipo],
                label=f"{etiqueta} (n={estilo.miles(len(datos))})")
        ax.axvline(datos.median(), color=TIPO_COLOR[tipo], ls="--", lw=1.6)
        resumen[etiqueta] = (datos.median(), datos.mean())
    ax.set_xlabel("Calificación promedio de la audiencia (0-10)")
    ax.set_ylabel("Cantidad de títulos")
    ax.set_xlim(0, 10)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: estilo.miles(v)))
    estilo.solo_eje_y(ax)
    estilo.titular(
        ax,
        "Las series se concentran en calificaciones más altas que las películas",
        "Distribución de calificaciones · líneas punteadas = mediana · excluye títulos sin votos",
    )
    ax.legend(loc="upper left")
    estilo.fuente(fig)
    guardar(fig, "02_distribucion_calificaciones")
    return resumen


# --------------------------------------------------------------------------
# 3. Distribucion de popularidad
#    Pregunta: como se reparte la atencion de la audiencia?
#    Grafico: histograma en escala logaritmica. La variable abarca tres
#    ordenes de magnitud; en escala lineal el 99% de los datos colapsaria
#    en la primera barra y el grafico no comunicaria nada.
# --------------------------------------------------------------------------
def fig_distribucion_popularidad(catalogo):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bins = np.logspace(np.log10(catalogo["popularity"].min()),
                       np.log10(catalogo["popularity"].max()), 60)
    ax.hist(catalogo["popularity"], bins=bins, color=GRIS, edgecolor="white", lw=0.4)
    p99 = catalogo["popularity"].quantile(0.99)
    top = catalogo[catalogo["popularity"] > p99]
    ax.hist(top["popularity"], bins=bins, color=ROJO, edgecolor="white", lw=0.4)
    ax.set_xscale("log")
    ax.set_xlabel("Índice de popularidad (escala logarítmica)")
    ax.set_ylabel("Cantidad de títulos")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: estilo.miles(v)))
    ax.axvline(p99, color=CARBON, ls="--", lw=1.4)
    ax.text(p99 * 1.2, ax.get_ylim()[1] * 0.80,
            f"Percentil 99\n{estilo.miles(len(top))} títulos concentran\nla atención máxima",
            fontsize=9.5, color=CARBON)
    estilo.solo_eje_y(ax)
    estilo.titular(
        ax,
        "La atención de la audiencia se concentra en una minoría de títulos",
        f"Distribución del índice de popularidad · {estilo.miles(len(catalogo))} títulos · escala log",
    )
    estilo.fuente(fig)
    guardar(fig, "03_distribucion_popularidad")
    return p99, len(top)


# --------------------------------------------------------------------------
# 4. Popularidad vs calidad  [HALLAZGO CENTRAL]
#    Pregunta: lo mas popular es lo mejor evaluado?
#    Grafico: dispersion con cuadrantes. Para evaluar la relacion entre dos
#    variables continuas la posicion conjunta es el unico atributo que
#    permite ver (o descartar) la correlacion; los cuadrantes traducen esa
#    nube en cuatro decisiones de negocio accionables.
# --------------------------------------------------------------------------
def fig_popularidad_vs_calidad(catalogo):
    d = catalogo[catalogo["calificado"] & (catalogo["vote_count"] >= 50)].copy()

    fig, ejes = plt.subplots(1, 2, figsize=(13, 6.8), sharey=True)
    resultado = {}

    for ax, tipo in zip(ejes, ("Película", "Serie")):
        s = d[d["tipo"] == tipo]
        corr = s["popularity"].corr(s["vote_average"])
        mx, my = s["popularity"].median(), s["vote_average"].median()

        joyas = s[(s["popularity"] < mx) & (s["vote_average"] > my)]
        exitos = s[(s["popularity"] >= mx) & (s["vote_average"] > my)]
        bajos = s[(s["popularity"] < mx) & (s["vote_average"] <= my)]
        sobre = s[(s["popularity"] >= mx) & (s["vote_average"] <= my)]
        resultado[tipo] = dict(corr=corr, joyas=len(joyas), sobre=len(sobre), n=len(s))

        ax.scatter(s["popularity"], s["vote_average"], s=7, alpha=0.18,
                   color=GRIS, edgecolors="none")
        ax.scatter(joyas["popularity"], joyas["vote_average"], s=7, alpha=0.32,
                   color=VERDE, edgecolors="none")
        ax.axvline(mx, color=CARBON, lw=1.2, ls="--")
        ax.axhline(my, color=CARBON, lw=1.2, ls="--")
        ax.set_xscale("log")
        ax.set_xlabel("Popularidad (escala logarítmica)")
        ax.set_ylim(1, 10.6)

        etiqueta = "Películas" if tipo == "Película" else "Series"
        ax.set_title(f"{etiqueta}   ·   r = {estilo.decimal(corr)}   ·   "
                     f"n = {estilo.miles(len(s))}",
                     fontsize=12, pad=10, loc="left", color=TIPO_COLOR[tipo])

        for x, y, txt, color, va in [
            (0.03, 0.97, f"CALIDAD SIN\nVISIBILIDAD\n{estilo.miles(len(joyas))}", VERDE, "top"),
            (0.97, 0.97, f"ÉXITOS\nCONSOLIDADOS\n{estilo.miles(len(exitos))}", ROJO, "top"),
            (0.03, 0.03, f"BAJO\nRENDIMIENTO\n{estilo.miles(len(bajos))}", "#8A8A8A", "bottom"),
            (0.97, 0.03, f"POPULARES MAL\nEVALUADOS\n{estilo.miles(len(sobre))}", NARANJA, "bottom"),
        ]:
            ax.text(x, y, txt, transform=ax.transAxes, fontsize=8.8, color=color,
                    fontweight="bold", va=va, ha="left" if x < 0.5 else "right",
                    linespacing=1.35,
                    bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=color,
                              lw=1.1, alpha=0.93))

    ejes[0].set_ylabel("Calificación de la audiencia (0-10)")

    # Se reserva la franja superior antes de colocar los titulos, para que
    # tight_layout no los solape con los subtitulos de cada panel.
    fig.tight_layout(rect=[0, 0, 1, 0.88])
    fig.text(0.006, 0.975,
             "Lo más popular no es lo mejor evaluado, en ninguno de los dos formatos",
             fontsize=15, fontweight="bold", color=CARBON, ha="left", va="top")
    fig.text(0.006, 0.917,
             "Popularidad vs. calificación, con medianas calculadas dentro de cada formato · "
             "títulos con 50 votos o más",
             fontsize=10.5, color="#6B6B6B", ha="left", va="top")
    estilo.fuente(fig, "Fuente: catálogo Netflix 2010-2025 · El índice de popularidad no es "
                       "comparable entre formatos, por eso cada panel usa su propia escala y "
                       "sus propias medianas.")
    guardar(fig, "04_popularidad_vs_calidad")
    return resultado


# --------------------------------------------------------------------------
# 5. Genero: calidad vs volumen de oferta
#    Pregunta: donde invierte el catalogo y que generos rinden mejor?
#    Grafico: dispersion con burbujas. Tres variables simultaneas -> se
#    asigna posicion X e Y a las dos criticas (mas precisas de leer) y
#    tamano a la tercera, que solo requiere comparacion gruesa.
# --------------------------------------------------------------------------
def fig_generos_calidad_volumen(generos):
    g = (generos[generos["vote_count"] > 0]
         .groupby("genero")
         .agg(titulos=("show_id", "count"),
              calificacion=("vote_average", "mean"),
              popularidad=("popularity", "median"))
         .query("titulos >= 200"))

    fig, ax = plt.subplots(figsize=(11, 7))
    med_cal = g["calificacion"].median()
    med_vol = g["titulos"].median()
    ax.axhline(med_cal, color=GRIS, ls="--", lw=1.1)
    ax.axvline(med_vol, color=GRIS, ls="--", lw=1.1)

    colores = [VERDE if (c > med_cal and v < med_vol)
               else (ROJO if c > med_cal else GRIS)
               for c, v in zip(g["calificacion"], g["titulos"])]
    ax.scatter(g["titulos"], g["calificacion"], s=g["popularidad"] * 4.5,
               c=colores, alpha=0.55, edgecolors="white", linewidths=1.5)

    etiquetar_sin_colision(ax, g["titulos"], g["calificacion"], g.index)

    ax.set_xlabel("Cantidad de títulos en el catálogo")
    ax.set_ylabel("Calificación promedio de la audiencia")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: estilo.miles(v)))
    estilo.titular(
        ax,
        "Existen géneros de alta calificación con baja presencia en el catálogo",
        "Género por volumen y calidad · tamaño = popularidad mediana · "
        "verde = calidad sobre la mediana con oferta reducida",
    )
    estilo.fuente(fig)
    guardar(fig, "05_generos_calidad_volumen")
    return g


# --------------------------------------------------------------------------
# 6. Evolucion temporal de la calidad percibida
#    Pregunta: el contenido reciente mejora o empeora en evaluacion?
#    Grafico: lineas + panel de contexto. La linea es el estandar para
#    series temporales; el panel inferior advierte del sesgo de maduracion
#    de votos, evitando que el lector saque conclusiones invalidas.
# --------------------------------------------------------------------------
def fig_evolucion_temporal(catalogo):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10.5, 8), sharex=True,
                                   gridspec_kw={"height_ratios": [2.4, 1]})
    tendencias = {}
    for tipo in ("Película", "Serie"):
        d = catalogo[(catalogo["tipo"] == tipo) & catalogo["calificado"]]
        serie = d.groupby("release_year")["vote_average"].mean()
        etiqueta = "Películas" if tipo == "Película" else "Series"
        ax1.plot(serie.index, serie.values, color=TIPO_COLOR[tipo], lw=2.6,
                 marker="o", ms=4)
        ax1.annotate(etiqueta, (serie.index[-1], serie.values[-1]),
                     xytext=(8, 0), textcoords="offset points",
                     color=TIPO_COLOR[tipo], fontweight="bold", va="center",
                     fontsize=10.5)
        tendencias[etiqueta] = serie
    ax1.set_ylabel("Calificación promedio")
    ax1.set_xlim(2009.5, 2026.5)

    brecha = (tendencias["Series"] - tendencias["Películas"])
    estilo.titular(
        ax1,
        "Las series superan a las películas en calificación todos los años",
        f"Promedio anual · brecha media de {estilo.decimal(brecha.mean())} puntos, "
        f"sostenida en los 16 años analizados",
    )

    # 2025 concentra la mayor proporcion de titulos sin calificar: su
    # promedio se calcula sobre una fraccion pequena y no es comparable.
    for eje in (ax1, ax2):
        eje.axvspan(2024.5, 2026.5, color="#F5F5F5", zorder=0)
    ax1.text(2024.6, ax1.get_ylim()[0] + 0.05,
             "2025:\ncobertura\nparcial", fontsize=8.5, color="#8A8A8A", va="bottom")

    sin = (catalogo.assign(sin_votos=~catalogo["calificado"])
           .groupby(["release_year", "tipo"])["sin_votos"].mean().unstack() * 100)
    ax2.plot(sin.index, sin["Película"], color=ROJO, lw=2, ls=":")
    ax2.plot(sin.index, sin["Serie"], color=AZUL, lw=2, ls=":")
    ax2.set_ylabel("% sin calificar")
    ax2.set_xlabel("Año de estreno")
    ax2.text(0.015, 0.92,
             "Advertencia metodológica: los títulos recientes acumulan menos votos",
             transform=ax2.transAxes, fontsize=9.5, color="#6B6B6B", va="top")
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}%"))
    estilo.fuente(fig)
    guardar(fig, "06_evolucion_temporal")
    return tendencias, sin


# --------------------------------------------------------------------------
# 7. Mercados por idioma
#    Pregunta: que mercados idiomaticos ofrecen mejor calidad percibida?
#    Grafico: barras horizontales ordenadas. En un ranking de categorias es
#    el orden lo que comunica; el color se reserva para destacar el top 3.
# --------------------------------------------------------------------------
def fig_mercados_idiomas(catalogo):
    d = (catalogo[catalogo["calificado"] & (catalogo["idioma"] != "Otro")]
         .groupby("idioma")
         .agg(titulos=("show_id", "count"), calificacion=("vote_average", "mean"))
         .query("titulos >= 300")
         .sort_values("calificacion"))

    fig, ax = plt.subplots(figsize=(10, 6.5))
    # El acento marca al protagonista del titular: el idioma que domina en
    # volumen pero no en calidad percibida.
    colores = [ROJO if idioma == "Inglés" else GRIS for idioma in d.index]
    ax.barh(d.index, d["calificacion"], color=colores)
    for i, (_, fila) in enumerate(d.iterrows()):
        ax.text(fila["calificacion"] + 0.07, i, estilo.decimal(fila["calificacion"]),
                va="center", fontsize=9.5, color=CARBON, fontweight="bold")
        ax.text(0.15, i, f"{estilo.miles(fila['titulos'])} títulos",
                va="center", fontsize=9, color="white")
    ax.set_xlabel("Calificación promedio de la audiencia")
    ax.set_xlim(0, d["calificacion"].max() + 0.7)
    estilo.solo_eje_x(ax)
    estilo.titular(
        ax,
        "El inglés domina el catálogo, pero no la calidad percibida",
        "Calificación promedio por idioma original · mercados con 300 títulos calificados o más",
    )
    estilo.fuente(fig)
    guardar(fig, "07_mercados_idiomas")
    return d


# --------------------------------------------------------------------------
# 8. Desempeno financiero de las peliculas
#    Pregunta: una mayor inversion garantiza un mayor retorno?
#    Grafico: dispersion log-log con linea de equilibrio. Ambas variables
#    cubren varios ordenes de magnitud y la diagonal separa visualmente
#    exito de perdida sin necesidad de calcular nada.
# --------------------------------------------------------------------------
def fig_financiero(peliculas):
    d = peliculas.dropna(subset=["budget", "revenue"])
    d = d[(d["budget"] > 1000) & (d["revenue"] > 1000)]
    rentable = d["revenue"] >= d["budget"]

    fig, ax = plt.subplots(figsize=(10.5, 7))
    ax.scatter(d.loc[~rentable, "budget"], d.loc[~rentable, "revenue"],
               s=11, alpha=0.35, color=GRIS, edgecolors="none",
               label="Bajo el punto de equilibrio")
    ax.scatter(d.loc[rentable, "budget"], d.loc[rentable, "revenue"],
               s=11, alpha=0.40, color=ROJO, edgecolors="none",
               label="Sobre el punto de equilibrio")
    lims = [d["budget"].min(), d["budget"].max()]
    ax.plot(lims, lims, color=CARBON, lw=1.6, ls="--",
            label="Punto de equilibrio (ingreso = presupuesto)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    # El formato por defecto usa la convencion inglesa de separadores.
    fmt = FuncFormatter(
        lambda v, _: (f"${estilo.miles(v/1e6)}M" if v >= 1e6
                      else f"${estilo.miles(v/1e3)}K"))
    ax.xaxis.set_major_formatter(fmt)
    ax.yaxis.set_major_formatter(fmt)
    ax.set_xlabel("Presupuesto")
    ax.set_ylabel("Ingresos")
    leyenda = ax.legend(loc="upper left", markerscale=2.4, handletextpad=0.6,
                        borderpad=0.8, labelspacing=0.7)
    leyenda.get_frame().set_facecolor("white")
    leyenda.get_frame().set_alpha(0.9)
    leyenda.set_frame_on(True)
    leyenda.get_frame().set_edgecolor("#DDDDDD")
    pct = rentable.mean() * 100
    estilo.titular(
        ax,
        f"Dos de cada tres películas superan su punto de equilibrio",
        f"Presupuesto vs. ingresos · {estilo.decimal(pct, 1)}% por sobre la diagonal · "
        f"escala log-log · n={estilo.miles(len(d))} películas con dato financiero",
    )
    estilo.fuente(fig)
    guardar(fig, "08_financiero")
    return d, pct


# --------------------------------------------------------------------------
# 9. Mapa de calor genero x ano
#    Pregunta: hay generos que mejoran o se deterioran sostenidamente?
#    Grafico: heatmap. Dos dimensiones (una categorica, una temporal) mas
#    una medida -> el color codifica intensidad y permite leer la matriz
#    completa de un vistazo, imposible con 12 lineas superpuestas.
# --------------------------------------------------------------------------
def fig_heatmap_genero_ano(generos):
    g = generos[generos["vote_count"] > 0]
    top = g["genero"].value_counts().head(12).index
    matriz = (g[g["genero"].isin(top)]
              .pivot_table(index="genero", columns="release_year",
                           values="vote_average", aggfunc="mean"))
    # Ordenar las filas por calificacion global hace que el eje vertical
    # comunique la jerarquia entre generos, en vez de desperdiciarlo en un
    # orden por volumen que no aporta a la lectura del color.
    matriz = matriz.loc[matriz.mean(axis=1).sort_values(ascending=False).index]

    fig, ax = plt.subplots(figsize=(12, 6.5))
    im = ax.imshow(matriz.values, aspect="auto", cmap="RdYlGn", vmin=5.0, vmax=7.5)
    ax.set_xticks(range(len(matriz.columns)))
    ax.set_xticklabels(matriz.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matriz.index)))
    ax.set_yticklabels(matriz.index)
    ax.grid(False)
    cbar = fig.colorbar(im, ax=ax, pad=0.015)
    cbar.set_label("Calificación promedio", fontsize=10)
    cbar.outline.set_visible(False)
    estilo.titular(
        ax,
        "Todos los géneros mejoran, pero la jerarquía entre ellos no cambia",
        "Calificación promedio por género y año · Top 12 géneros por volumen · "
        "filas ordenadas por calificación global",
    )
    estilo.fuente(fig)
    guardar(fig, "09_heatmap_genero_ano")
    return matriz


# --------------------------------------------------------------------------
# 10. Rentabilidad segun escala de inversion
#     Pregunta: que tramos de presupuesto rinden mejor?
#     Grafico: barras verticales con doble codificacion. La altura muestra la
#     tasa de exito y la etiqueta el retorno mediano, para que la comparacion
#     entre tramos no dependa de leer dos graficos separados.
# --------------------------------------------------------------------------
def fig_rentabilidad_escala(peliculas):
    d = peliculas.dropna(subset=["budget", "revenue"])
    d = d[(d["budget"] > 1000) & (d["revenue"] > 1000)].copy()
    d["escala"] = pd.cut(d["budget"], [0, 5e6, 30e6, 100e6, np.inf],
                         labels=["Bajo\n(menos de 5M)", "Medio\n(5-30M)",
                                 "Alto\n(30-100M)", "Muy alto\n(más de 100M)"])
    g = d.groupby("escala", observed=True).agg(
        peliculas=("budget", "size"),
        exito=("revenue", lambda s: (s >= d.loc[s.index, "budget"]).mean() * 100),
        roi=("roi", "median"))

    fig, ax = plt.subplots(figsize=(10, 6))
    peor = g["exito"].idxmin()
    colores = [NARANJA if i == peor else (ROJO if i == g["exito"].idxmax() else GRIS)
               for i in g.index]
    barras = ax.bar(range(len(g)), g["exito"], color=colores, width=0.62)
    ax.set_xticks(range(len(g)))
    ax.set_xticklabels(g.index)
    ax.set_ylabel("Películas que superan su punto de equilibrio")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}%"))
    ax.set_ylim(0, 105)
    for barra, (_, fila) in zip(barras, g.iterrows()):
        ax.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 2.5,
                f"{estilo.decimal(fila['exito'], 1)}%", ha="center",
                fontsize=11.5, fontweight="bold", color=CARBON)
        ax.text(barra.get_x() + barra.get_width()/2, barra.get_height()/2,
                f"retorno mediano\n{estilo.decimal(fila['roi'])}x\n\n"
                f"{estilo.miles(fila['peliculas'])} películas",
                ha="center", va="center", fontsize=9.5, color="white")
    estilo.solo_eje_y(ax)
    estilo.titular(
        ax,
        "El tramo medio de inversión es el de peor desempeño",
        "Tasa de éxito comercial y retorno por escala de presupuesto · "
        f"n={estilo.miles(len(d))} películas con dato financiero",
    )
    estilo.fuente(fig)
    guardar(fig, "10_rentabilidad_escala")
    return g


# --------------------------------------------------------------------------
# 11. Momentum de genero: rotacion de interes 2010-2018 vs 2022-2024
#     Pregunta: hacia que generos se esta moviendo la atencion de la audiencia?
#     Grafico: barras horizontales de variacion porcentual. No se usa el ano
#     como eje continuo (la correlacion global es practicamente nula) sino
#     una comparacion de dos ventanas, que aisla la rotacion de interes por
#     genero de la ausencia de tendencia agregada.
# --------------------------------------------------------------------------
def fig_momentum_generos(generos):
    reciente = (generos[(generos["release_year"] >= 2022) & (generos["release_year"] <= 2024)]
               .groupby("genero")["popularity"].median())
    antiguo = (generos[(generos["release_year"] >= 2010) & (generos["release_year"] <= 2018)]
              .groupby("genero")["popularity"].median())
    m = pd.DataFrame({"reciente": reciente, "antiguo": antiguo}).dropna()
    m["variacion"] = (m["reciente"] / m["antiguo"] - 1) * 100
    m = m.sort_values("variacion")

    fig, ax = plt.subplots(figsize=(10, 8))
    colores = [VERDE if v > 0 else GRIS for v in m["variacion"]]
    top3 = set(m.nlargest(3, "variacion").index)
    colores = [ROJO if i in top3 else c for i, c in zip(m.index, colores)]
    ax.barh(m.index, m["variacion"], color=colores)
    ax.axvline(0, color=CARBON, lw=1.2)
    ax.set_xlim(m["variacion"].min() - 22, m["variacion"].max() + 14)
    for i, (nombre, fila) in enumerate(m.iterrows()):
        x = fila["variacion"]
        ax.text(x + (2 if x >= 0 else -2), i, f"{estilo.decimal(x, 1)}%",
                va="center", ha="left" if x >= 0 else "right",
                fontsize=9, color=CARBON, fontweight="bold" if nombre in top3 else "normal")
    ax.set_xlabel("Variación de la popularidad mediana, 2022-2024 vs. 2010-2018")
    estilo.solo_eje_x(ax)
    estilo.titular(
        ax,
        "Terror, Suspenso y Acción ganan interés; los formatos de estudio lo pierden",
        "Variación porcentual de la popularidad mediana por género entre ambas ventanas "
        "· no implica crecimiento del catálogo",
    )
    estilo.fuente(fig, "Fuente: catálogo Netflix 2010-2025 · La correlación año-popularidad es "
                       "prácticamente nula (r=0,13 en películas, r=-0,05 en series): esto mide "
                       "rotación de interés entre géneros, no una tendencia agregada sostenida.")
    guardar(fig, "12_momentum_generos")
    return m


# --------------------------------------------------------------------------
# 12. Programa Joyas Ocultas: caracterizacion del cuadrante para activacion
#     Pregunta: que forma tiene el contenido de calidad sin visibilidad y
#     donde esta concentrado?
#     Grafico: dos paneles. Barras horizontales para el ranking de generos
#     (el orden comunica) y barras agrupadas para contrastar la calidad del
#     segmento contra el resto del catalogo evaluable, por formato.
# --------------------------------------------------------------------------
def fig_joyas_ocultas(catalogo):
    ev = catalogo[catalogo["calificado"] & (catalogo["vote_count"] >= 50)].copy()
    partes = []
    for tipo in ("Película", "Serie"):
        s = ev[ev["tipo"] == tipo].copy()
        mx, my = s["popularity"].median(), s["vote_average"].median()
        s["cuadrante"] = np.where((s["popularity"] < mx) & (s["vote_average"] > my),
                                  "joya", "resto")
        partes.append(s)
    ev = pd.concat(partes)
    joyas = ev[ev["cuadrante"] == "joya"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.5),
                                   gridspec_kw={"width_ratios": [1.3, 1]})

    top = joyas["genero_principal"].value_counts().head(8).sort_values()
    ax1.barh(top.index, top.values, color=VERDE, alpha=0.85)
    for i, v in enumerate(top.values):
        ax1.text(v + top.max() * 0.015, i, estilo.miles(v), va="center",
                 fontsize=9.5, color=CARBON, fontweight="bold")
    ax1.set_xlabel("Títulos en el cuadrante «calidad sin visibilidad»")
    estilo.solo_eje_x(ax1)
    ax1.set_title("¿Dónde están las joyas?", fontsize=12.5, fontweight="bold",
                  loc="left", color=CARBON, pad=10)

    x = np.arange(2)
    ancho = 0.32
    cal_joyas = [joyas.loc[joyas["tipo"] == t, "vote_average"].mean()
                for t in ("Película", "Serie")]
    cal_resto = [ev.loc[(ev["cuadrante"] == "resto") & (ev["tipo"] == t), "vote_average"].mean()
                for t in ("Película", "Serie")]
    ax2.bar(x - ancho/2, cal_joyas, ancho, color=VERDE, label="Joyas ocultas")
    ax2.bar(x + ancho/2, cal_resto, ancho, color=GRIS, label="Resto del catálogo evaluable")
    for xi, v in zip(x - ancho/2, cal_joyas):
        ax2.text(xi, v + 0.08, estilo.decimal(v), ha="center", fontsize=10,
                 fontweight="bold", color=CARBON)
    for xi, v in zip(x + ancho/2, cal_resto):
        ax2.text(xi, v + 0.08, estilo.decimal(v), ha="center", fontsize=10,
                 color=CARBON)
    ax2.set_xticks(x)
    ax2.set_xticklabels(["Películas", "Series"])
    ax2.set_ylabel("Calificación promedio de la audiencia")
    ax2.set_ylim(0, 9.5)
    ax2.legend(loc="upper left", fontsize=9.5)
    estilo.solo_eje_y(ax2)
    ax2.set_title("¿Qué tan buenas son?", fontsize=12.5, fontweight="bold",
                  loc="left", color=CARBON, pad=10)

    fig.suptitle("El catálogo ya contiene el contenido: falta exponerlo",
                 fontsize=15.5, fontweight="bold", x=0.01, ha="left", y=1.04,
                 color=CARBON)
    fig.text(0.01, 0.985,
             f"Programa Joyas Ocultas · {estilo.miles(len(joyas))} títulos calificados por sobre "
             "la mediana de su formato, con popularidad por debajo de ella",
             fontsize=10.5, color="#6B6B6B", ha="left", va="top")
    estilo.fuente(fig)
    fig.tight_layout(rect=[0, 0, 1, 0.87])
    guardar(fig, "11_joyas_ocultas")
    return joyas


def main():
    estilo.aplicar_estilo()
    catalogo, generos, peliculas = cargar()

    print("Generando visualizaciones:")
    fig_composicion_generos(generos)
    resumen_cal = fig_distribucion_calificaciones(catalogo)
    p99, n_top = fig_distribucion_popularidad(catalogo)
    cuadrantes = fig_popularidad_vs_calidad(catalogo)
    g = fig_generos_calidad_volumen(generos)
    fig_evolucion_temporal(catalogo)
    idiomas = fig_mercados_idiomas(catalogo)
    _, pct = fig_financiero(peliculas)
    fig_heatmap_genero_ano(generos)
    escala = fig_rentabilidad_escala(peliculas)
    momentum = fig_momentum_generos(generos)
    joyas = fig_joyas_ocultas(catalogo)

    print("\n--- CIFRAS CLAVE PARA EL INFORME ---")
    for tipo, r in cuadrantes.items():
        print(f"{tipo:9} r={r['corr']:.3f}  n={r['n']:,}  "
              f"calidad sin visibilidad={r['joyas']:,}  "
              f"populares mal evaluados={r['sobre']:,}")
    print(f"Peliculas rentables                  : {pct:.1f}%")
    print(f"Umbral percentil 99 popularidad      : {p99:.1f} ({n_top} titulos)")
    print(f"Mediana calificacion                 : {resumen_cal}")
    print("\nGeneros por calificacion (top 6):")
    print(g.sort_values("calificacion", ascending=False).head(6).round(2).to_string())
    print("\nGeneros por calificacion (ultimos 4):")
    print(g.sort_values("calificacion").head(4).round(2).to_string())
    print("\nIdiomas por calificacion:")
    print(idiomas.sort_values("calificacion", ascending=False).round(2).to_string())


if __name__ == "__main__":
    main()
