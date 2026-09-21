"""
StreamView Analytics - Preparacion de datos (CRISP-DM Fase 3)

Lee los catalogos crudos de peliculas y series desde data/raw/, aplica las
decisiones de limpieza derivadas de la fase de Comprension de los Datos y
genera los datasets analiticos en data/processed/.

Uso:  python src/data_prep.py
"""
from pathlib import Path
import pandas as pd
import numpy as np

RAW = Path("data/raw")
PROC = Path("data/processed")

IDIOMAS = {
    'en': 'Inglés', 'es': 'Español', 'fr': 'Francés', 'ja': 'Japonés',
    'ko': 'Coreano', 'zh': 'Chino', 'hi': 'Hindi', 'de': 'Alemán',
    'it': 'Italiano', 'pt': 'Portugués', 'tr': 'Turco', 'ru': 'Ruso',
    'ar': 'Árabe', 'tl': 'Tagalo', 'th': 'Tailandés', 'pl': 'Polaco',
    'nl': 'Neerlandés', 'sv': 'Sueco', 'da': 'Danés', 'id': 'Indonesio',
}

# Ambas fuentes traen taxonomias de genero distintas: las peliculas separan
# "Action"/"Adventure" y "Science Fiction"/"Fantasy", mientras que las series
# los agrupan en "Action & Adventure" y "Sci-Fi & Fantasy". Compararlos sin
# armonizar produciria categorias artificialmente exclusivas de un formato.
GENEROS = {
    'Action': 'Acción y Aventura',
    'Adventure': 'Acción y Aventura',
    'Action & Adventure': 'Acción y Aventura',
    'Science Fiction': 'Ciencia Ficción y Fantasía',
    'Fantasy': 'Ciencia Ficción y Fantasía',
    'Sci-Fi & Fantasy': 'Ciencia Ficción y Fantasía',
    'War': 'Bélico y Político',
    'War & Politics': 'Bélico y Político',
    'Animation': 'Animación',
    'Comedy': 'Comedia',
    'Crime': 'Crimen',
    'Documentary': 'Documental',
    'Drama': 'Drama',
    'Family': 'Familiar',
    'Kids': 'Infantil',
    'Mystery': 'Misterio',
    'Western': 'Western',
    'History': 'Histórico',
    'Horror': 'Terror',
    'Music': 'Musical',
    'Romance': 'Romance',
    'Thriller': 'Suspenso',
    'News': 'Noticias',
    'Reality': 'Reality',
    'Soap': 'Telenovela',
    'Talk': 'Talk Show',
    'TV Movie': 'Película para TV',
}


def cargar_crudos():
    peliculas = pd.read_csv(RAW / "netflix_movies_detailed_up_to_2025.csv")
    series = pd.read_csv(RAW / "netflix_tv_shows_detailed_up_to_2025.csv")
    return peliculas, series


def limpiar(df):
    df = df.copy()

    # 'rating' es una copia exacta de 'vote_average'; 'duration' no aporta
    # (nula al 100% en peliculas, constante "1 Seasons" en series).
    df = df.drop(columns=[c for c in ("rating", "duration") if c in df.columns])

    df = df.drop_duplicates(subset="show_id", keep="first")

    # Un titulo sin votos no vale 0.0: es ausencia de calificacion.
    sin_votos = df["vote_count"] == 0
    df.loc[sin_votos, "vote_average"] = np.nan

    # En budget/revenue el 0 enmascara el dato faltante.
    for col in ("budget", "revenue"):
        if col in df.columns:
            df[col] = df[col].replace(0, np.nan)

    df["date_added"] = pd.to_datetime(df["date_added"], errors="coerce")

    for col in ("country", "genres", "cast", "director", "description"):
        if col in df.columns:
            df[col] = df[col].fillna("Sin informacion")

    df["idioma"] = df["language"].map(IDIOMAS).fillna("Otro")
    df["pais_principal"] = (df["country"].str.split(", ").str[0]
                            .replace("Sin informacion", np.nan))
    df["genero_principal"] = (df["genres"].str.split(", ").str[0]
                              .map(GENEROS))
    df["calificado"] = df["vote_count"] > 0

    if "revenue" in df.columns:
        df["roi"] = df["revenue"] / df["budget"]
        df["utilidad"] = df["revenue"] - df["budget"]

    return df


def construir_catalogo(peliculas, series):
    """Une ambas fuentes en un unico catalogo analitico."""
    comunes = [c for c in peliculas.columns if c in series.columns]
    catalogo = pd.concat(
        [peliculas[comunes], series[comunes]], ignore_index=True
    )
    catalogo["tipo"] = catalogo["type"].map(
        {"Movie": "Película", "TV Show": "Serie"}
    )
    return catalogo


def explotar_generos(catalogo):
    """Tabla larga titulo-genero, con la taxonomia armonizada entre formatos.

    Al fusionar categorias (p. ej. Action + Adventure) un mismo titulo puede
    quedar asignado dos veces al genero resultante, por lo que se deduplica
    el par titulo-genero para no inflar los conteos.
    """
    generos = (catalogo[["show_id", "tipo", "title", "release_year",
                         "popularity", "vote_average", "vote_count", "idioma"]]
               .assign(genero=catalogo["genres"].str.split(", "))
               .explode("genero"))
    generos["genero"] = generos["genero"].map(GENEROS)
    generos = generos.dropna(subset=["genero"])
    return generos.drop_duplicates(subset=["show_id", "tipo", "genero"])


def main():
    PROC.mkdir(parents=True, exist_ok=True)
    peliculas_raw, series_raw = cargar_crudos()

    peliculas = limpiar(peliculas_raw)
    series = limpiar(series_raw)
    catalogo = construir_catalogo(peliculas, series)
    generos = explotar_generos(catalogo)

    peliculas.to_csv(PROC / "peliculas_limpio.csv", index=False)
    series.to_csv(PROC / "series_limpio.csv", index=False)
    catalogo.to_csv(PROC / "catalogo_unificado.csv", index=False)
    generos.to_csv(PROC / "catalogo_generos.csv", index=False)

    print(f"peliculas_limpio.csv    {len(peliculas):>6,} filas x {peliculas.shape[1]} cols")
    print(f"series_limpio.csv       {len(series):>6,} filas x {series.shape[1]} cols")
    print(f"catalogo_unificado.csv  {len(catalogo):>6,} filas x {catalogo.shape[1]} cols")
    print(f"catalogo_generos.csv    {len(generos):>6,} filas x {generos.shape[1]} cols")
    print(f"\nTitulos calificados: {catalogo['calificado'].sum():,} "
          f"({catalogo['calificado'].mean()*100:.1f}%)")
    print(f"Peliculas con dato financiero: {peliculas['revenue'].notna().sum():,}")


if __name__ == "__main__":
    main()
