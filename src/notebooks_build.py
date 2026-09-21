# -*- coding: utf-8 -*-
"""
StreamView Analytics - Generador de los notebooks del proyecto

Construye y ejecuta los cuadernos que documentan las fases 2 a 4 de CRISP-DM,
dejando las salidas embebidas para que se puedan leer sin necesidad de
ejecutarlos. Reutilizan los modulos de src/, de modo que el notebook y los
entregables comparten exactamente el mismo codigo.

Uso:  python src/notebooks_build.py
"""
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

NB = Path("notebooks")

PREAMBULO = """import os
from pathlib import Path

# Permite ejecutar el cuaderno tanto desde la raiz del proyecto como desde notebooks/
if Path.cwd().name == "notebooks":
    os.chdir("..")

import sys
sys.path.insert(0, "src")

import pandas as pd
import numpy as np
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 30)
print("Directorio de trabajo:", Path.cwd().name)"""


def md(txt):
    return nbf.v4.new_markdown_cell(txt)


def code(txt):
    return nbf.v4.new_code_cell(txt)


# ---------------------------------------------------------------------------
# Notebook 1: comprension y preparacion de los datos
# ---------------------------------------------------------------------------
def notebook_comprension():
    c = [
        md("""# 01 · Comprensión y preparación de los datos
### CRISP-DM · Fases 2 y 3 — StreamView Analytics

Este cuaderno documenta el diagnóstico de las fuentes entregadas por la organización y las
decisiones de limpieza que se derivan de él. Su propósito no es producir gráficos, sino
**establecer qué permiten y qué no permiten afirmar estos datos** antes de analizarlos.

| Fase | Contenido |
|---|---|
| 2 · Comprensión de los datos | Perfilado, calidad, diseño muestral |
| 3 · Preparación de los datos | Limpieza, armonización, integración |"""),
        code(PREAMBULO),

        md("""## 1. Carga de las fuentes originales

Se trabaja sobre los archivos tal como los entregó la organización, sin modificarlos."""),
        code("""peliculas = pd.read_csv("data/raw/netflix_movies_detailed_up_to_2025.csv")
series = pd.read_csv("data/raw/netflix_tv_shows_detailed_up_to_2025.csv")

print(f"Películas : {peliculas.shape[0]:,} filas x {peliculas.shape[1]} columnas")
print(f"Series    : {series.shape[0]:,} filas x {series.shape[1]} columnas")
print(f"\\nColumnas solo en películas: {sorted(set(peliculas.columns) - set(series.columns))}")"""),

        md("""## 2. Perfilado: tipos, ausencias y cardinalidad

El perfilado es el primer filtro: revela columnas inutilizables y ausencias que condicionan
el análisis posterior."""),
        code("""def perfilar(df, nombre):
    info = pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "nulos": df.isna().sum(),
        "%nulos": (df.isna().sum() / len(df) * 100).round(2),
        "únicos": df.nunique(),
    })
    print(f"===== {nombre} =====")
    print(info.to_string())
    print()
    return info

_ = perfilar(peliculas, "PELÍCULAS")
_ = perfilar(series, "SERIES")"""),

        md("""### Primeras señales de alerta

- `duration` es **100% nula** en películas y toma un **único valor constante** en series.
- `director` falta en cerca de dos tercios de las series.
- `rating` y `vote_average` presentan exactamente la misma cardinalidad: hay que comprobar si
  son la misma variable duplicada."""),
        code("""print("¿rating es idéntica a vote_average?")
print("  Películas:", (peliculas["rating"] == peliculas["vote_average"]).all())
print("  Series   :", (series["rating"] == series["vote_average"]).all())

print("\\nValores únicos de 'duration':")
print("  Películas:", peliculas["duration"].unique()[:5])
print("  Series   :", series["duration"].unique()[:5])"""),

        md("""## 3. Hallazgo determinante: el diseño muestral

La distribución de títulos por año de estreno revela que **no estamos ante el catálogo completo**."""),
        code("""conteo = pd.DataFrame({
    "películas": peliculas["release_year"].value_counts().sort_index(),
    "series": series["release_year"].value_counts().sort_index(),
})
print(conteo.to_string())
print(f"\\n¿Todos los años tienen el mismo número de títulos? "
      f"{conteo['películas'].nunique() == 1 and conteo['series'].nunique() == 1}")"""),

        md("""> **Consecuencia metodológica.** Ambas fuentes contienen exactamente 1.000 títulos por año
> entre 2010 y 2025: se trata de una **muestra estratificada por año**, no del catálogo real.
>
> Esto invalida de antemano cualquier conclusión sobre crecimiento o contracción del catálogo
> en el tiempo, porque el volumen anual es **constante por diseño**. Todas las comparaciones
> temporales del proyecto son de composición y de calidad, nunca de volumen."""),

        md("""## 4. Ceros que en realidad son ausencias

Tres variables usan el cero para representar «sin dato». Promediarlas sin corregir
distorsionaría todos los resultados."""),
        code("""print("Títulos sin votos (vote_count == 0):")
print(f"  Películas: {(peliculas['vote_count'] == 0).sum():,} "
      f"({(peliculas['vote_count'] == 0).mean()*100:.1f}%)")
print(f"  Series   : {(series['vote_count'] == 0).sum():,} "
      f"({(series['vote_count'] == 0).mean()*100:.1f}%)")

print("\\n¿Esos títulos figuran con calificación 0,0?")
sin_votos = series[series["vote_count"] == 0]
print(f"  De {len(sin_votos):,} series sin votos, {(sin_votos['vote_average'] == 0).sum():,} "
      f"tienen vote_average = 0")

print("\\nVariables financieras en cero (solo películas):")
print(f"  budget  == 0: {(peliculas['budget'] == 0).sum():,} "
      f"({(peliculas['budget'] == 0).mean()*100:.1f}%)")
print(f"  revenue == 0: {(peliculas['revenue'] == 0).sum():,} "
      f"({(peliculas['revenue'] == 0).mean()*100:.1f}%)")"""),

        md("""Si se promediaran los ceros como si fueran calificaciones reales, el resultado cambiaría
de forma sustantiva. La comparación lo demuestra:"""),
        code("""con_ceros = series["vote_average"].mean()
sin_ceros = series.loc[series["vote_count"] > 0, "vote_average"].mean()
print(f"Calificación media de las series contando los ceros : {con_ceros:.2f}")
print(f"Calificación media excluyendo los no calificados    : {sin_ceros:.2f}")
print(f"Diferencia                                          : {sin_ceros - con_ceros:.2f} puntos")"""),

        md("""## 5. Taxonomías de género divergentes

Al intentar comparar géneros entre formatos aparece un problema de integración: **las dos
fuentes no usan la misma clasificación**."""),
        code("""gp = set(peliculas["genres"].dropna().str.split(", ").explode())
gs = set(series["genres"].dropna().str.split(", ").explode())

print(f"Solo en películas ({len(gp - gs)}):", sorted(gp - gs))
print(f"\\nSolo en series ({len(gs - gp)}):", sorted(gs - gp))
print(f"\\nEn ambas ({len(gp & gs)}):", sorted(gp & gs))"""),

        md("""> **Por qué importa.** Las películas separan `Action` y `Adventure`; las series los agrupan en
> `Action & Adventure`. Lo mismo ocurre con ciencia ficción y fantasía. Comparar géneros sin
> armonizar produciría categorías que parecen exclusivas de un formato cuando en realidad son
> un artefacto de la clasificación de origen.
>
> Este hallazgo, surgido durante la fase de análisis, obligó a **volver a la fase de preparación**
> — el comportamiento iterativo que CRISP-DM prescribe."""),

        md("""## 6. Otros hallazgos de calidad"""),
        code("""print("Identificadores duplicados:")
print(f"  Películas: {peliculas['show_id'].duplicated().sum()}")
print(f"  Series   : {series['show_id'].duplicated().sum()}")

print("\\n¿'date_added' es una fecha real de incorporación al catálogo?")
for nombre, df in [("Películas", peliculas), ("Series", series)]:
    fecha = pd.to_datetime(df["date_added"], errors="coerce")
    coincide = (fecha.dt.year == df["release_year"]).mean() * 100
    print(f"  {nombre}: coincide con release_year en el {coincide:.1f}% de los casos")"""),

        md("""> `date_added` cae **siempre** en el mismo año de estreno, por lo que no representa la fecha
> real de incorporación al catálogo y se descarta como eje temporal."""),

        md("""## 7. Preparación: ejecución del pipeline

Todas las decisiones anteriores están implementadas en `src/data_prep.py`. El pipeline parte de
los archivos originales y genera los conjuntos analíticos de forma reproducible."""),
        code("""import data_prep
import importlib
importlib.reload(data_prep)

data_prep.main()"""),

        md("""### Resumen de las decisiones aplicadas

| Problema detectado | Decisión |
|---|---|
| `rating` duplica a `vote_average` | Columna eliminada |
| `duration` nula o constante | Columna eliminada |
| Calificación 0,0 sin votos | Convertida a valor ausente |
| `budget` / `revenue` en cero | Tratados como dato faltante |
| `show_id` duplicados | Deduplicados |
| Taxonomías de género divergentes | Armonizadas a una taxonomía única en español |
| `date_added` no confiable | Descartada como eje temporal |
| Muestreo estratificado | Documentado: prohíbe conclusiones sobre volumen |"""),

        md("""## 8. Verificación del resultado"""),
        code("""catalogo = pd.read_csv("data/processed/catalogo_unificado.csv")
generos = pd.read_csv("data/processed/catalogo_generos.csv")

print(f"Catálogo unificado : {len(catalogo):,} títulos")
print(f"Tabla de géneros   : {len(generos):,} pares título-género")
print(f"Títulos calificados: {catalogo['calificado'].sum():,} "
      f"({catalogo['calificado'].mean()*100:.1f}%)")
print(f"\\nGéneros armonizados ({generos['genero'].nunique()}):")
print(sorted(generos["genero"].unique()))"""),

        md("""---
**Siguiente paso:** `02_analisis_exploratorio.ipynb` — CRISP-DM fase 4."""),
    ]
    nb = nbf.v4.new_notebook(cells=c)
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}}
    return nb


# ---------------------------------------------------------------------------
# Notebook 2: analisis exploratorio
# ---------------------------------------------------------------------------
def notebook_exploracion():
    c = [
        md("""# 02 · Análisis exploratorio mediante visualizaciones
### CRISP-DM · Fase 4 — StreamView Analytics

Este cuaderno regenera las visualizaciones del informe ejecutivo y documenta los hallazgos que
sostienen las recomendaciones. Cada figura responde a una pregunta de negocio explícita.

> Requiere haber ejecutado antes `01_comprension_y_preparacion.ipynb` o `python src/data_prep.py`."""),
        code(PREAMBULO),
        code("""from IPython.display import Image, display
import estilo
import eda_visualizaciones as eda

estilo.aplicar_estilo()
catalogo, generos, peliculas = eda.cargar()

print(f"Catálogo : {len(catalogo):,} títulos")
print(f"Géneros  : {len(generos):,} pares título-género")
print(f"Películas: {len(peliculas):,} (con datos financieros)")"""),

        md("""## 1. Indicadores generales del catálogo"""),
        code("""cal = catalogo[catalogo["calificado"]]

print(f"Títulos analizados        : {len(catalogo):,}")
print(f"Con calificación válida   : {len(cal):,} ({len(cal)/len(catalogo)*100:.1f}%)")
print(f"Calificación promedio     : {cal['vote_average'].mean():.2f}")
print(f"Popularidad mediana       : {catalogo['popularity'].median():.1f}")
print(f"Popularidad máxima        : {catalogo['popularity'].max():.1f}")
print(f"Razón máximo/mediana      : {catalogo['popularity'].max()/catalogo['popularity'].median():.0f}x")

print("\\nCalificación mediana por formato:")
print(cal.groupby("tipo")["vote_average"].agg(["count", "median", "mean"]).round(2).to_string())"""),

        md("""## 2. Composición del catálogo

**Pregunta:** ¿en qué géneros está concentrada la oferta?

**Representación elegida:** barras horizontales agrupadas. La longitud es el atributo visual que
se decodifica con mayor precisión, y la orientación horizontal evita rotar etiquetas largas."""),
        code("""eda.fig_composicion_generos(generos)
display(Image("images/01_composicion_generos.png"))"""),

        md("""## 3. Distribución de la calidad percibida

**Pregunta:** ¿cómo se distribuye la valoración de la audiencia?

**Representación elegida:** histograma. Al tratarse de una variable continua, interesa la forma
completa de la distribución y no solo su promedio."""),
        code("""eda.fig_distribucion_calificaciones(catalogo)
display(Image("images/02_distribucion_calificaciones.png"))"""),

        md("""## 4. Cómo se reparte la atención

**Pregunta:** ¿la audiencia distribuye su atención o la concentra?

**Representación elegida:** histograma en escala logarítmica. La variable abarca tres órdenes de
magnitud; en escala lineal el 99% de los títulos colapsaría en la primera barra."""),
        code("""eda.fig_distribucion_popularidad(catalogo)
display(Image("images/03_distribucion_popularidad.png"))"""),

        md("""## 5. Hallazgo central: atención frente a valoración

**Pregunta:** ¿lo más popular es lo mejor evaluado?

**Representación elegida:** dispersión con cuadrantes. Para evaluar la relación entre dos
variables continuas, la posición conjunta es el único codificador que permite ver —o descartar—
la correlación.

Se exige un mínimo de 50 votos: una calificación sostenida por dos o tres votos es ruido, no señal."""),
        code("""ev = catalogo[catalogo["calificado"] & (catalogo["vote_count"] >= 50)]
corr = ev["popularity"].corr(ev["vote_average"])

print(f"Títulos evaluables (>= 50 votos): {len(ev):,}")
print(f"Correlación popularidad-calificación: {corr:.3f}")
print("\\nCorrelaciones entre las variables clave:")
print(ev[["popularity", "vote_count", "vote_average", "release_year"]].corr().round(3).to_string())"""),
        code("""eda.fig_popularidad_vs_calidad(catalogo)
display(Image("images/04_popularidad_vs_calidad.png"))"""),

        md("""### Segmentación en cuadrantes

Los cuadrantes se definen sobre las **medianas** y no sobre los promedios, porque ambas
variables tienen distribuciones muy asimétricas: la mediana divide el universo en partes
comparables."""),
        code("""mx, my = ev["popularity"].median(), ev["vote_average"].median()
cuadrantes = pd.DataFrame([
    {"segmento": "Éxitos consolidados", "criterio": "alta atención · alta valoración",
     "títulos": len(ev[(ev.popularity >= mx) & (ev.vote_average > my)]),
     "acción": "Proteger: asegurar renovación de derechos"},
    {"segmento": "Calidad sin visibilidad", "criterio": "baja atención · alta valoración",
     "títulos": len(ev[(ev.popularity < mx) & (ev.vote_average > my)]),
     "acción": "Promover: máxima prioridad, costo marginal cero"},
    {"segmento": "Populares mal evaluados", "criterio": "alta atención · baja valoración",
     "títulos": len(ev[(ev.popularity >= mx) & (ev.vote_average <= my)]),
     "acción": "Vigilar: erosionan la percepción de calidad"},
    {"segmento": "Bajo rendimiento", "criterio": "baja atención · baja valoración",
     "títulos": len(ev[(ev.popularity < mx) & (ev.vote_average <= my)]),
     "acción": "Revisar: candidatos a depuración"},
])
print(cuadrantes.to_string(index=False))"""),

        md("""> **Hallazgo 1.** Popularidad y calidad percibida son **dimensiones prácticamente
> independientes**. Gestionar el catálogo con una sola métrica optimiza un objetivo a costa del
> otro. El cuadrante de *calidad sin visibilidad* concentra contenido ya pagado cuyo valor no se
> está capturando."""),

        md("""## 6. Géneros: dónde invierte el catálogo y qué rinde mejor

**Pregunta:** ¿coincide la apuesta del catálogo con lo que la audiencia mejor valora?

**Representación elegida:** dispersión con burbujas. Tres variables simultáneas: posición X e Y
para las dos críticas y tamaño para la tercera, que solo requiere comparación gruesa."""),
        code("""g = (generos[generos["vote_count"] > 0]
     .groupby("genero")
     .agg(titulos=("show_id", "count"),
          calificacion=("vote_average", "mean"),
          popularidad=("popularity", "median"))
     .query("titulos >= 200"))

print("Mejor evaluados:")
print(g.sort_values("calificacion", ascending=False).head(6).round(2).to_string())
print("\\nPeor evaluados:")
print(g.sort_values("calificacion").head(4).round(2).to_string())"""),
        code("""eda.fig_generos_calidad_volumen(generos)
display(Image("images/05_generos_calidad_volumen.png"))"""),

        md("""> **Hallazgo 2.** Los géneros mejor evaluados son sistemáticamente **los menos
> representados**. Esa franja —calidad sobre la mediana, oferta por debajo— define la oportunidad
> de crecimiento más clara del catálogo."""),

        md("""## 7. Evolución temporal

**Pregunta:** ¿la calidad del contenido mejora o se deteriora?

**Representación elegida:** líneas con panel de contexto. La línea es el estándar para series
temporales; el panel inferior expone la limitación de los datos junto al gráfico."""),
        code("""anual = cal.pivot_table(index="release_year", columns="tipo",
                        values="vote_average", aggfunc="mean").round(3)
anual["brecha"] = (anual["Serie"] - anual["Película"]).round(3)
print(anual.to_string())
print(f"\\nAños en que las series superan a las películas: "
      f"{(anual['brecha'] > 0).sum()} de {len(anual)}")
print(f"Brecha media  : {anual['brecha'].mean():.2f} puntos")
print(f"Brecha mínima : {anual['brecha'].min():.2f} puntos")"""),
        code("""eda.fig_evolucion_temporal(catalogo)
display(Image("images/06_evolucion_temporal.png"))"""),

        md("""> **Hallazgo 3.** La ventaja de las series es **estructural, no coyuntural**: se sostiene en
> los 16 años analizados sin una sola excepción.
>
> **Cautela:** el último año presenta una proporción de títulos sin calificar muy superior al
> resto, por lo que su promedio no es comparable con los anteriores."""),

        md("""## 8. Estabilidad de la jerarquía entre géneros

**Representación elegida:** mapa de calor. Dos dimensiones más una medida: el color permite leer
la matriz completa de un vistazo, imposible con doce líneas superpuestas."""),
        code("""eda.fig_heatmap_genero_ano(generos)
display(Image("images/09_heatmap_genero_ano.png"))"""),

        md("""## 9. Mercados de origen

**Pregunta:** ¿el idioma donde el catálogo concentra su inversión es el mejor valorado?

**Representación elegida:** barras horizontales ordenadas, con línea base en cero. Truncar el eje
habría exagerado visualmente diferencias de décimas de punto."""),
        code("""idi = (cal[cal["idioma"] != "Otro"]
       .groupby("idioma")
       .agg(titulos=("show_id", "count"), calificacion=("vote_average", "mean"))
       .query("titulos >= 300")
       .sort_values("calificacion", ascending=False))
print(idi.round(2).to_string())

pos = idi.index.get_loc("Inglés") + 1
print(f"\\nEl inglés reúne {idi.loc['Inglés', 'titulos']:,} títulos "
      f"({idi.loc['Inglés', 'titulos']/len(cal)*100:.1f}% del catálogo calificado)")
print(f"pero ocupa la posición {pos} de {len(idi)} en calificación promedio.")"""),
        code("""eda.fig_mercados_idiomas(catalogo)
display(Image("images/07_mercados_idiomas.png"))"""),

        md("""> **Hallazgo 4.** La concentración del catálogo **no coincide con la valoración**: el mercado
> dominante en volumen está entre los peor evaluados."""),

        md("""## 10. Desempeño comercial

**Pregunta:** ¿una mayor inversión garantiza un mayor retorno?

**Representación elegida:** dispersión log-log con diagonal de equilibrio. Ambas variables cubren
varios órdenes de magnitud, y la diagonal convierte una comparación numérica en una lectura
posicional inmediata."""),
        code("""fin = peliculas.dropna(subset=["budget", "revenue"])
fin = fin[(fin["budget"] > 1000) & (fin["revenue"] > 1000)]

print(f"Películas con dato financiero: {len(fin):,} "
      f"({len(fin)/len(peliculas)*100:.1f}% del total)")
print(f"Superan el punto de equilibrio: {(fin['revenue'] >= fin['budget']).mean()*100:.1f}%")
print(f"Retorno mediano: {fin['roi'].median():.2f}x")

print("\\nCorrelaciones con los ingresos:")
print(f"  Presupuesto  : {fin['budget'].corr(fin['revenue']):.2f}")
print(f"  Nº de votos  : {fin['vote_count'].corr(fin['revenue']):.2f}")
print(f"  Calificación : {fin['vote_average'].corr(fin['revenue']):.2f}")"""),
        code("""eda.fig_financiero(peliculas)
display(Image("images/08_financiero.png"))"""),

        md("""> Los ingresos correlacionan fuertemente con el presupuesto y con el número de votos —es
> decir, con la **escala de exposición**— pero muy débilmente con la calificación. La taquilla
> mide alcance, no calidad. Esto refuerza el hallazgo central desde una fuente independiente."""),

        md("""## 11. Rentabilidad según escala de inversión

**Representación elegida:** barras verticales con doble codificación. Categorías ordinales en su
orden natural; la altura muestra la tasa de éxito y la etiqueta interior el retorno mediano."""),
        code("""tramos = fin.copy()
tramos["escala"] = pd.cut(tramos["budget"], [0, 5e6, 30e6, 100e6, np.inf],
                          labels=["Bajo (<5M)", "Medio (5-30M)",
                                  "Alto (30-100M)", "Muy alto (>100M)"])
resumen = tramos.groupby("escala", observed=True).apply(
    lambda x: pd.Series({
        "películas": len(x),
        "% rentables": round((x["revenue"] >= x["budget"]).mean() * 100, 1),
        "ROI mediano": round(x["roi"].median(), 2),
    }), include_groups=False)
print(resumen.to_string())"""),
        code("""eda.fig_rentabilidad_escala(peliculas)
display(Image("images/10_rentabilidad_escala.png"))"""),

        md("""> **Hallazgo 5.** El riesgo comercial **no está en las apuestas grandes**: la tasa de éxito
> crece con la escala de inversión. El peor desempeño está en el tramo medio, que además
> concentra el mayor número de películas.
>
> **Cautela:** solo una fracción de las películas informa datos financieros, y es plausible que
> sean las de mayor circulación comercial. Lectura indicativa."""),

        md("""## 12. Consolidación de métricas

Todas las cifras citadas en el informe ejecutivo y en la presentación se calculan en un único
lugar y se exportan, de modo que ningún número se transcribe a mano."""),
        code("""import metricas
import importlib
importlib.reload(metricas)

metricas.main()"""),

        md("""---
## Síntesis de los hallazgos

| # | Hallazgo | Implicancia para el negocio |
|---|---|---|
| 1 | Popularidad y calidad son independientes | Gestionar con una sola métrica es incorrecto |
| 2 | Los géneros mejor evaluados son los menos representados | Oportunidad de crecimiento acotada |
| 3 | La ventaja de las series es estructural | Justifica desplazar producción a formatos episódicos |
| 4 | El mercado dominante no es el mejor valorado | Margen para rebalancear la adquisición |
| 5 | El riesgo está en el tramo medio de inversión | Revisar la política de presupuestos intermedios |

**Siguiente paso:** los entregables se generan con `src/dashboard_build.py`,
`src/informe_build.py` y `src/presentacion_build.py`."""),
    ]
    nb = nbf.v4.new_notebook(cells=c)
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}}
    return nb


def main():
    NB.mkdir(exist_ok=True)
    for nombre, constructor in [("01_comprension_y_preparacion", notebook_comprension),
                                ("02_analisis_exploratorio", notebook_exploracion)]:
        nb = constructor()
        print(f"Ejecutando {nombre}...", end=" ", flush=True)
        cliente = NotebookClient(nb, timeout=600, kernel_name="python3",
                                 resources={"metadata": {"path": "."}})
        cliente.execute()
        ruta = NB / f"{nombre}.ipynb"
        nbf.write(nb, ruta)
        print(f"OK -> {ruta}")


if __name__ == "__main__":
    main()
