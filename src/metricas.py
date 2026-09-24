# -*- coding: utf-8 -*-
"""
StreamView Analytics - Consolidacion de metricas del proyecto

Calcula en un solo lugar todas las cifras que citan el informe ejecutivo y la
presentacion, y las deja en data/processed/metricas.json. De este modo ningun
numero del entregable se transcribe a mano: si cambian los datos de origen,
cambian los documentos.

Uso:  python src/metricas.py
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np

PROC = Path("data/processed")


def cargar():
    return (pd.read_csv(PROC / "catalogo_unificado.csv"),
            pd.read_csv(PROC / "catalogo_generos.csv"),
            pd.read_csv(PROC / "peliculas_limpio.csv"),
            pd.read_csv(PROC / "series_limpio.csv"))


def calcular():
    catalogo, generos, peliculas, series = cargar()
    m = {}

    # --- Volumen y cobertura -------------------------------------------
    m["titulos_total"] = int(len(catalogo))
    m["peliculas_total"] = int(len(peliculas))
    m["series_total"] = int(len(series))
    m["anio_min"] = int(catalogo["release_year"].min())
    m["anio_max"] = int(catalogo["release_year"].max())
    m["anios_cubiertos"] = m["anio_max"] - m["anio_min"] + 1
    m["titulos_por_anio_formato"] = int(
        catalogo.groupby(["release_year", "tipo"]).size().mode().iloc[0])

    m["calificados"] = int(catalogo["calificado"].sum())
    m["calificados_pct"] = round(catalogo["calificado"].mean() * 100, 1)
    m["sin_calificar"] = int((~catalogo["calificado"]).sum())
    m["sin_calificar_peliculas"] = int((~peliculas["calificado"]).sum())
    m["sin_calificar_series"] = int((~series["calificado"]).sum())

    # --- Calidad percibida ---------------------------------------------
    cal = catalogo[catalogo["calificado"]]
    m["calificacion_media"] = round(cal["vote_average"].mean(), 2)
    for clave, tipo in (("peliculas", "Película"), ("series", "Serie")):
        s = cal.loc[cal["tipo"] == tipo, "vote_average"]
        m[f"calificacion_mediana_{clave}"] = round(s.median(), 2)
        m[f"calificacion_media_{clave}"] = round(s.mean(), 2)
    m["brecha_series_peliculas"] = round(
        m["calificacion_media_series"] - m["calificacion_media_peliculas"], 2)

    anual = (cal.pivot_table(index="release_year", columns="tipo",
                             values="vote_average", aggfunc="mean"))
    m["brecha_anual_minima"] = round((anual["Serie"] - anual["Película"]).min(), 2)
    m["anios_series_sobre_peliculas"] = int((anual["Serie"] > anual["Película"]).sum())

    # La ventaja de las series debe comprobarse controlando por numero de
    # votos: las series calificadas acumulan bastantes menos votos que las
    # peliculas, y sin ese control la brecha podria ser un artefacto.
    ctrl = cal[cal["vote_count"] >= 50]
    g = ctrl.groupby("tipo")["vote_average"].mean()
    m["brecha_series_peliculas_controlada"] = round(g["Serie"] - g["Película"], 2)
    anual_ctrl = ctrl.pivot_table(index="release_year", columns="tipo",
                                  values="vote_average", aggfunc="mean")
    dif = anual_ctrl["Serie"] - anual_ctrl["Película"]
    m["anios_series_sobre_peliculas_controlada"] = int((dif > 0).sum())
    m["brecha_anual_minima_controlada"] = round(dif.min(), 2)
    m["calificacion_series_inicio"] = round(anual["Serie"].iloc[0], 2)
    m["calificacion_series_fin"] = round(anual["Serie"].iloc[-1], 2)
    m["calificacion_peliculas_inicio"] = round(anual["Película"].iloc[0], 2)
    m["calificacion_peliculas_fin"] = round(anual["Película"].iloc[-1], 2)

    # --- Concentracion de la atencion ----------------------------------
    p99 = catalogo["popularity"].quantile(0.99)
    m["popularidad_mediana"] = round(catalogo["popularity"].median(), 1)
    m["popularidad_maxima"] = round(catalogo["popularity"].max(), 1)
    m["popularidad_p99"] = round(p99, 1)
    m["titulos_sobre_p99"] = int((catalogo["popularity"] > p99).sum())
    m["ratio_max_mediana"] = int(round(
        catalogo["popularity"].max() / catalogo["popularity"].median()))

    # --- Hallazgo central: popularidad vs calidad ----------------------
    # El indice de popularidad NO es comparable entre formatos: la mediana de
    # las series cuadruplica la de las peliculas porque la fuente lo calcula de
    # forma distinta segun el tipo de contenido. Por eso tanto la correlacion
    # como los cuadrantes se calculan DENTRO de cada formato; agregarlos
    # mezclaria dos poblaciones con escalas incompatibles y convertiria el
    # corte de popularidad en un simple separador de formato.
    UMBRAL = 50
    ev = catalogo[catalogo["calificado"] & (catalogo["vote_count"] >= UMBRAL)].copy()
    m["evaluables"] = int(len(ev))
    m["umbral_votos"] = UMBRAL

    partes = []
    for tipo in ("Película", "Serie"):
        s = ev[ev["tipo"] == tipo].copy()
        mx, my = s["popularity"].median(), s["vote_average"].median()
        alta_pop = s["popularity"] >= mx
        alta_cal = s["vote_average"] > my
        s["cuadrante"] = np.select(
            [~alta_pop & alta_cal, alta_pop & alta_cal, alta_pop & ~alta_cal],
            ["calidad_sin_visibilidad", "exitos", "populares_mal_evaluados"],
            default="bajo_rendimiento")
        partes.append(s)
        clave = "peliculas" if tipo == "Película" else "series"
        m[f"correlacion_pop_calidad_{clave}"] = round(
            s["popularity"].corr(s["vote_average"]), 3)
        m[f"evaluables_{clave}"] = int(len(s))
        m[f"mediana_popularidad_{clave}"] = round(mx, 1)
    ev = pd.concat(partes)

    conteo = ev["cuadrante"].value_counts()
    m["cuad_calidad_sin_visibilidad"] = int(conteo.get("calidad_sin_visibilidad", 0))
    m["cuad_exitos"] = int(conteo.get("exitos", 0))
    m["cuad_bajo_rendimiento"] = int(conteo.get("bajo_rendimiento", 0))
    m["cuad_populares_mal_evaluados"] = int(conteo.get("populares_mal_evaluados", 0))
    m["pct_calidad_sin_visibilidad"] = round(
        m["cuad_calidad_sin_visibilidad"] / m["evaluables"] * 100, 1)
    m["pct_populares_mal_evaluados"] = round(
        m["cuad_populares_mal_evaluados"] / m["evaluables"] * 100, 1)
    joyas = ev[ev["cuadrante"] == "calidad_sin_visibilidad"]
    m["cuad_calidad_sin_visibilidad_peliculas"] = int((joyas["tipo"] == "Película").sum())
    m["cuad_calidad_sin_visibilidad_series"] = int((joyas["tipo"] == "Serie").sum())

    # Sesgo de seleccion del umbral: no afecta por igual a ambos formatos.
    cal_todo = catalogo[catalogo["calificado"]]
    for tipo, clave in (("Película", "peliculas"), ("Serie", "series")):
        s = cal_todo[cal_todo["tipo"] == tipo]
        m[f"pct_supera_umbral_{clave}"] = round(
            (s["vote_count"] >= UMBRAL).mean() * 100, 1)
    m["pct_peliculas_en_evaluables"] = round((ev["tipo"] == "Película").mean() * 100, 1)

    # --- Propuesta comercial 2: Programa "Joyas Ocultas" -----------------
    # Caracterizacion del cuadrante "calidad sin visibilidad" para fundamentar
    # la propuesta de activacion editorial: por genero, por idioma, y su
    # calidad promedio frente al resto del catalogo evaluable.
    m["joyas_calificacion_media_peliculas"] = round(
        joyas.loc[joyas["tipo"] == "Película", "vote_average"].mean(), 2)
    m["joyas_calificacion_media_series"] = round(
        joyas.loc[joyas["tipo"] == "Serie", "vote_average"].mean(), 2)
    resto = ev[ev["cuadrante"] != "calidad_sin_visibilidad"]
    m["resto_calificacion_media_peliculas"] = round(
        resto.loc[resto["tipo"] == "Película", "vote_average"].mean(), 2)
    m["resto_calificacion_media_series"] = round(
        resto.loc[resto["tipo"] == "Serie", "vote_average"].mean(), 2)

    top_generos_joyas = joyas["genero_principal"].value_counts().head(5)
    m["joyas_top_generos"] = [
        {"genero": g, "titulos": int(n)} for g, n in top_generos_joyas.items()]
    top_idiomas_joyas = joyas["idioma"].value_counts().head(5)
    m["joyas_top_idiomas"] = [
        {"idioma": i, "titulos": int(n)} for i, n in top_idiomas_joyas.items()]

    ejemplos = (joyas.sort_values("vote_average", ascending=False)
               .drop_duplicates(subset="genero_principal")
               .head(6))
    m["joyas_ejemplos"] = [
        {"title": r.title, "tipo": r.tipo, "anio": int(r.release_year),
         "genero": r.genero_principal, "idioma": r.idioma,
         "calificacion": round(r.vote_average, 2), "votos": int(r.vote_count)}
        for r in ejemplos.itertuples()]

    # --- Propuesta comercial 1: Radar de Momentum por Genero -------------
    # Variacion de la popularidad mediana entre 2010-2018 y 2022-2024. Es la
    # base de la propuesta de adquisicion dirigida por genero en alza: mide
    # rotacion de interes, no crecimiento general del catalogo.
    reciente = (generos[(generos["release_year"] >= 2022) & (generos["release_year"] <= 2024)]
               .groupby("genero")["popularity"].median())
    antiguo = (generos[(generos["release_year"] >= 2010) & (generos["release_year"] <= 2018)]
              .groupby("genero")["popularity"].median())
    momentum = pd.DataFrame({"reciente": reciente, "antiguo": antiguo}).dropna()
    momentum["variacion_pct"] = round((momentum["reciente"] / momentum["antiguo"] - 1) * 100, 1)
    momentum = momentum.sort_values("variacion_pct", ascending=False)
    m["momentum_top_generos"] = [
        {"genero": g, "variacion_pct": r.variacion_pct,
         "popularidad_reciente": round(r.reciente, 1)}
        for g, r in momentum.head(5).iterrows()]
    m["momentum_bottom_generos"] = [
        {"genero": g, "variacion_pct": r.variacion_pct,
         "popularidad_reciente": round(r.reciente, 1)}
        for g, r in momentum.tail(3).iterrows()]
    m["correlacion_anio_popularidad_peliculas"] = round(
        catalogo.loc[catalogo["tipo"] == "Película", "release_year"]
        .corr(catalogo.loc[catalogo["tipo"] == "Película", "popularity"]), 3)
    m["correlacion_anio_popularidad_series"] = round(
        catalogo.loc[catalogo["tipo"] == "Serie", "release_year"]
        .corr(catalogo.loc[catalogo["tipo"] == "Serie", "popularity"]), 3)


    # --- Generos --------------------------------------------------------
    g = (generos[generos["vote_count"] > 0]
         .groupby("genero")
         .agg(titulos=("show_id", "count"),
              calificacion=("vote_average", "mean"),
              popularidad=("popularity", "median"))
         .query("titulos >= 200"))
    m["generos_analizados"] = int(len(g))
    m["generos_top"] = [
        {"genero": i, "titulos": int(r.titulos), "calificacion": round(r.calificacion, 2)}
        for i, r in g.sort_values("calificacion", ascending=False).head(5).iterrows()]
    m["generos_bajos"] = [
        {"genero": i, "titulos": int(r.titulos), "calificacion": round(r.calificacion, 2)}
        for i, r in g.sort_values("calificacion").head(3).iterrows()]
    m["generos_volumen"] = [
        {"genero": i, "titulos": int(r.titulos), "calificacion": round(r.calificacion, 2)}
        for i, r in g.sort_values("titulos", ascending=False).head(3).iterrows()]
    # Oportunidad: calidad sobre la mediana pero oferta bajo la mediana
    med_c, med_v = g["calificacion"].median(), g["titulos"].median()
    opor = g[(g["calificacion"] > med_c) & (g["titulos"] < med_v)]
    m["generos_oportunidad"] = [
        {"genero": i, "titulos": int(r.titulos), "calificacion": round(r.calificacion, 2)}
        for i, r in opor.sort_values("calificacion", ascending=False).iterrows()]

    # --- Mercados por idioma -------------------------------------------
    idi = (cal[cal["idioma"] != "Otro"]
           .groupby("idioma")
           .agg(titulos=("show_id", "count"), calificacion=("vote_average", "mean"))
           .query("titulos >= 300"))
    m["mercados_analizados"] = int(len(idi))
    m["mercados_top"] = [
        {"idioma": i, "titulos": int(r.titulos), "calificacion": round(r.calificacion, 2)}
        for i, r in idi.sort_values("calificacion", ascending=False).head(3).iterrows()]
    ing = idi.loc["Inglés"]
    m["ingles_titulos"] = int(ing.titulos)
    m["ingles_calificacion"] = round(ing.calificacion, 2)
    m["ingles_pct_catalogo"] = round(ing.titulos / len(cal) * 100, 1)
    m["ingles_posicion"] = int(
        idi.sort_values("calificacion", ascending=False).index.get_loc("Inglés") + 1)
    mejor = idi.sort_values("calificacion", ascending=False).iloc[0]
    m["brecha_mejor_mercado_ingles"] = round(mejor.calificacion - ing.calificacion, 2)

    # --- Desempeno financiero ------------------------------------------
    fin = peliculas.dropna(subset=["budget", "revenue"])
    fin = fin[(fin["budget"] > 1000) & (fin["revenue"] > 1000)]
    m["peliculas_con_finanzas"] = int(len(fin))
    m["peliculas_con_finanzas_pct"] = round(len(fin) / len(peliculas) * 100, 1)
    m["pct_rentables"] = round((fin["revenue"] >= fin["budget"]).mean() * 100, 1)
    m["corr_presupuesto_ingreso"] = round(fin["budget"].corr(fin["revenue"]), 2)
    m["corr_votos_ingreso"] = round(fin["vote_count"].corr(fin["revenue"]), 2)
    m["corr_calificacion_ingreso"] = round(fin["vote_average"].corr(fin["revenue"]), 2)
    m["roi_mediano"] = round(fin["roi"].median(), 2)
    m["presupuesto_mediano_millones"] = round(fin["budget"].median() / 1e6, 1)

    # Rentabilidad segun escala de inversion
    fin = fin.copy()
    fin["escala"] = pd.cut(fin["budget"],
                           [0, 5e6, 30e6, 100e6, np.inf],
                           labels=["Bajo (<5M)", "Medio (5-30M)",
                                   "Alto (30-100M)", "Muy alto (>100M)"])
    esc = fin.groupby("escala", observed=True).apply(
        lambda x: pd.Series({
            "peliculas": len(x),
            "pct_rentables": round((x["revenue"] >= x["budget"]).mean() * 100, 1),
            "roi_mediano": round(x["roi"].median(), 2)}), include_groups=False)
    m["rentabilidad_por_escala"] = [
        {"escala": i, "peliculas": int(r.peliculas),
         "pct_rentables": r.pct_rentables, "roi_mediano": r.roi_mediano}
        for i, r in esc.iterrows()]

    # --- Calidad de datos (para la evaluacion critica) ------------------
    # Se leen los archivos originales para que estas cifras describan el dato
    # crudo y no el ya depurado.
    from data_prep import RAW
    peliculas_raw = pd.read_csv(RAW / "netflix_movies_detailed_up_to_2025.csv")
    series_raw = pd.read_csv(RAW / "netflix_tv_shows_detailed_up_to_2025.csv")

    m["budget_ceros_pct"] = round((peliculas_raw["budget"] == 0).mean() * 100, 1)
    m["revenue_ceros_pct"] = round((peliculas_raw["revenue"] == 0).mean() * 100, 1)
    m["director_nulos_series_pct"] = round(series_raw["director"].isna().mean() * 100, 1)
    m["descripcion_nulos_series_pct"] = round(
        series_raw["description"].isna().mean() * 100, 1)
    m["series_id_duplicados"] = int(series_raw["show_id"].duplicated().sum())
    m["series_registros_originales"] = int(len(series_raw))
    m["peliculas_variables"] = int(peliculas_raw.shape[1])
    m["series_variables"] = int(series_raw.shape[1])
    m["generos_solo_peliculas"] = int(len(
        set(peliculas_raw["genres"].dropna().str.split(", ").explode())
        - set(series_raw["genres"].dropna().str.split(", ").explode())))
    m["generos_solo_series"] = int(len(
        set(series_raw["genres"].dropna().str.split(", ").explode())
        - set(peliculas_raw["genres"].dropna().str.split(", ").explode())))

    m["registros_dashboard"] = int(catalogo["genero_principal"].notna().pipe(sum))

    return m


def main():
    m = calcular()
    salida = PROC / "metricas.json"
    salida.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{salida}  ({len(m)} metricas)")
    for k in ("titulos_total", "calificados_pct",
              "correlacion_pop_calidad_peliculas", "correlacion_pop_calidad_series",
              "cuad_calidad_sin_visibilidad", "brecha_series_peliculas_controlada",
              "pct_rentables", "ingles_posicion", "roi_mediano"):
        print(f"  {k:38} {m[k]}")


if __name__ == "__main__":
    main()
