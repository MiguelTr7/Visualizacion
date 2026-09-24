# Inteligencia de Catálogo — StreamView Analytics

Proyecto de visualización de datos para la asignatura **ADY1104 Visualización de Datos**
(Evaluaciones EP1 Encargo y EP2 Presentación).

En el marco del encargo, el equipo asume el rol de consultores en analítica y comunicación
visual contratados por **StreamView Analytics**, una plataforma internacional de streaming que
necesita comprender el desempeño de su catálogo para fundamentar sus decisiones de adquisición,
producción y promoción de contenido.

**Hallazgo central:** la popularidad de un título y su calificación por parte de la audiencia
son dimensiones prácticamente independientes (r = 0,09 en películas y 0,01 en series). El catálogo
contiene **3.222 títulos de alta calidad y baja visibilidad**: contenido ya pagado cuyo valor no se
está capturando.

---

## Metodología: CRISP-DM

| Fase | Aplicación | Dónde está |
|---|---|---|
| 1 · Comprensión del negocio | Problema, audiencia objetivo, propósito comunicacional | Informe §1-3 |
| 2 · Comprensión de los datos | Perfilado, calidad, detección del diseño muestral | Informe §5 · `notebooks/01` |
| 3 · Preparación de los datos | Limpieza, armonización de taxonomías, integración | Informe §6 · `src/data_prep.py` |
| 4 · Modelado / Análisis | Análisis exploratorio visual y segmentación por cuadrantes | Informe §7-8 · `notebooks/02` |
| 5 · Evaluación | Revisión crítica de la solución y validez de los hallazgos | Informe §11 |
| 6 · Despliegue | Dashboard, narrativa visual e informe ejecutivo | Informe §9-10 · `dashboard/` |

El proceso fue iterativo: la fase 4 obligó a retroceder a la fase 3 al detectar que películas y
series usaban **taxonomías de género distintas**, lo que producía categorías artificialmente
exclusivas de un formato.

---

## Entregables

| # | Entregable | Archivo |
|---|---|---|
| 1 | Informe ejecutivo | `reports/informe_ejecutivo/informe_ejecutivo.html` |
| 2 | Dashboard interactivo | `dashboard/dashboard.html` |
| 3 | Presentación ejecutiva (18 diapositivas) | `reports/informe_ejecutivo/presentacion_ejecutiva.html` (HTML) y `.pptx` (PowerPoint) |
| 4 | Notebooks documentados | `notebooks/01…`, `notebooks/02…` |
| 5 | Visualizaciones | `images/` (12 figuras) |
| 6 | Datos y código reproducible | `data/`, `src/` |

### Cómo obtener los PDF

El informe y la presentación se entregan en HTML autocontenido y se exportan a PDF desde el
navegador, sin necesidad de instalar nada:

- **Informe:** abrir el archivo → `Ctrl+P` → *Guardar como PDF* → A4, márgenes predeterminados,
  activar **Gráficos de fondo**.
- **Presentación:** abrir el archivo → `Ctrl+P` → *Guardar como PDF* → orientación
  **horizontal**, márgenes **ninguno**, activar **Gráficos de fondo**.

### Cómo abrir el dashboard

Doble clic en `dashboard/dashboard.html`. No requiere servidor, instalación ni conexión: los
30.904 registros van embebidos en el archivo y el filtrado se resuelve en el navegador.

---

## Estructura del proyecto

```
visualizacion/
├── data/
│   ├── raw/                     Datos originales, sin modificar
│   │   ├── netflix_movies_detailed_up_to_2025.csv
│   │   └── netflix_tv_shows_detailed_up_to_2025.csv
│   └── processed/               Datos depurados e integrados
│       ├── catalogo_unificado.csv     31.991 títulos (películas + series)
│       ├── catalogo_generos.csv       Tabla larga título-género
│       ├── peliculas_limpio.csv       Incluye variables financieras
│       ├── series_limpio.csv
│       └── metricas.json              Cifras consolidadas del proyecto
├── notebooks/
│   ├── 01_comprension_y_preparacion.ipynb    CRISP-DM fases 2 y 3
│   └── 02_analisis_exploratorio.ipynb        CRISP-DM fase 4
├── src/
│   ├── estilo.py                Estándar visual (paleta, tipografía, reglas)
│   ├── data_prep.py             Limpieza, armonización e integración
│   ├── metricas.py              Consolidación de todas las cifras
│   ├── eda_visualizaciones.py   Las 12 figuras del informe
│   ├── dashboard_build.py       Generador del dashboard interactivo
│   ├── informe_build.py         Generador del informe ejecutivo
│   ├── presentacion_build.py    Generador de la presentación (HTML)
│   ├── presentacion_pptx.py     Generador de la presentación (PowerPoint)
│   └── notebooks_build.py       Generador y ejecutor de los notebooks
├── dashboard/
│   └── dashboard.html           Dashboard autocontenido
├── images/                      12 visualizaciones en PNG
├── reports/informe_ejecutivo/
│   ├── informe_ejecutivo.html
│   ├── presentacion_ejecutiva.html
│   └── presentacion_ejecutiva.pptx
├── requirements.txt
└── README.md
```

---

## Reproducir el proyecto completo

```bash
pip install -r requirements.txt

python src/data_prep.py            # Fase 3: limpieza e integración
python src/metricas.py             # Consolidación de cifras
python src/eda_visualizaciones.py  # Fase 4: las 12 figuras
python src/dashboard_build.py      # Fase 6: dashboard
python src/informe_build.py        # Fase 6: informe ejecutivo
python src/presentacion_build.py   # Fase 6: presentación (HTML)
python src/presentacion_pptx.py    # Fase 6: presentación (PowerPoint)
python src/notebooks_build.py      # Notebooks ejecutados con salidas
```

Cada script parte de los archivos originales y no depende del estado previo del proyecto, salvo
por el orden indicado. **Ninguna cifra del informe o la presentación se escribe a mano**: todas
se leen desde `metricas.json`, por lo que si cambian los datos de origen, cambian los documentos.

---

## Hallazgos principales

| # | Hallazgo | Evidencia |
|---|---|---|
| 1 | Popularidad y calidad percibida son independientes | r = 0,09 en películas y 0,01 en series (n = 15.397) |
| 2 | Existen 3.222 títulos de calidad sin visibilidad | 20,9% del catálogo evaluable |
| 3 | La ventaja de las series es estructural | Superan a las películas los 16 años; brecha 1,13 con ≥50 votos |
| 4 | El mercado dominante no es el mejor valorado | El inglés: 47,4% del catálogo, puesto 10 de 12 en calidad |
| 5 | Los géneros mejor evaluados son los menos representados | Documental 7,24 · Infantil 7,20 · Musical 6,96 |
| 6 | El riesgo comercial está en el tramo medio | 56,2% de éxito frente a 89,6% en el tramo muy alto |

---

## Propuestas comerciales (Informe §12)

Tres estrategias de adquisición y retención derivadas de los hallazgos anteriores, sin usar
variables financieras — solo popularidad, calificación, votos, género, formato y año.

| Propuesta | Hallazgo que la respalda | Palanca | KPI |
|---|---|---|---|
| **1. Programa Joyas Ocultas** *(prioritaria)* | 3.222 títulos ya en catálogo, bien evaluados, con baja visibilidad | Exposición editorial, costo de contenido cero | % de usuarios que consumen el segmento al mes |
| 2. Radar de Momentum por Género | Rotación real de interés (Terror +93,8%, Suspenso +78,3%); no hay tendencia agregada (r≈0) | Adquisición dirigida por género en alza | Variación trimestral de popularidad por género |
| 3. Series como Ancla de Suscripción | Ventaja de +1,13 puntos de las series sobre películas, sostenida 16 años | Retención por hábito episódico | Retorno semanal y episodios completados en 7 días |

La Propuesta 1 recibe tratamiento extendido en el informe (figura dedicada, ejemplos de títulos
reales, mecanismo detallado) y una diapositiva propia en la presentación, por ser la única que no
requiere inversión en contenido nuevo.

---

## Advertencias metodológicas

Estas limitaciones condicionan la lectura de todos los resultados y están documentadas en
detalle en la sección 11 del informe.

- **No hay datos de usuarios.** Las fuentes describen el catálogo, no el comportamiento
  individual: no hay reproducciones, suscripciones, dispositivos ni cancelaciones. El proyecto
  **no puede medir retención ni engagement reales**; `popularity` se usa como aproximación de
  atención.
- **El muestreo impide analizar volumen.** Ambas fuentes contienen exactamente 1.000 títulos por
  año (2010-2025): es una muestra estratificada, no el catálogo. Ninguna conclusión sobre
  crecimiento del catálogo sería válida.
- **Cobertura financiera parcial.** Solo el 22,0% de las películas informa presupuesto e
  ingresos, y es plausible que sean las de mayor circulación comercial.
- **Calificaciones de origen externo.** Provienen de una comunidad de votantes que no equivale a
  la base de suscriptores de la plataforma.
- **Sesgo de maduración de votos.** Los títulos recientes acumulan menos votos, por lo que el
  último año no es comparable con los anteriores.
- **El índice de popularidad no es comparable entre formatos.** Su mediana en series (47,6)
  cuadruplica la de películas (11,4) porque la fuente lo calcula de forma distinta según el tipo de
  contenido. Por eso las correlaciones y los cuadrantes se calculan **dentro de cada formato**.
- **El umbral de 50 votos sesga la muestra evaluable.** Lo supera el 80,7% de las películas
  calificadas pero solo el 26,1% de las series, de modo que los recuentos absolutos por cuadrante
  están dominados por el formato película.
- **Inconsistencias de unidad en los datos financieros.** Algunos registros mezclan escalas
  (presupuestos de cientos de dólares con ingresos millonarios); se mitiga usando medianas.

---

## Decisiones de diseño visual

El proyecto aplica un estándar único definido en `src/estilo.py` y replicado en el dashboard:

- **Un solo color de acento por figura**, reservado al dato protagonista; el resto en grises.
  Paleta categórica segura para daltonismo (basada en Okabe-Ito).
- **Titulares que afirman el hallazgo**, no que rotulan el contenido: el lector obtiene la
  conclusión aunque solo recorra los títulos.
- **Líneas base en cero** en los gráficos de barras y **escalas logarítmicas declaradas** en los
  ejes, para no distorsionar la lectura.
- **Advertencias metodológicas dentro de las figuras**, no en notas al pie.
- **Comparaciones dentro de poblaciones homogéneas**: cuando una métrica no es comparable entre
  formatos, los cortes se calculan por formato en lugar de agregarlos.
- **Convención numérica local** (coma decimal, punto de miles) en todos los productos.
- Sin efectos tridimensionales, sin rejillas redundantes, con etiquetado directo en lugar de
  leyendas cuando es posible.

---

## Cobertura de los requisitos de la pauta

| Requisito | Dónde se cumple |
|---|---|
| Descripción del problema de negocio | Informe §1 · Diapositiva 2 |
| Objetivos del proyecto | Informe §2 |
| Audiencia objetivo y propósito comunicacional | Informe §3 · Diapositiva 2 |
| Descripción e integración de las fuentes de datos | Informe §5-6 · `notebooks/01` |
| Análisis exploratorio mediante visualizaciones | Informe §7 · `notebooks/02` · 12 figuras |
| Justificación de las representaciones gráficas | Informe §8 · comentarios en `eda_visualizaciones.py` |
| Narrativa visual (Data Storytelling) | Informe §9 · Diapositivas 5-12 |
| Dashboard interactivo con KPIs, filtros e interacción | Informe §10 · `dashboard/dashboard.html` |
| Evaluación crítica de la solución | Informe §11 · Diapositiva 14 |
| Conclusiones y recomendaciones | Informe §12 · Diapositivas 15-16 |
| Carpeta con estructura profesional | Este repositorio |

---

## Requisitos técnicos

Python 3.10 o superior. Dependencias en `requirements.txt`: pandas, numpy, matplotlib, seaborn,
plotly, jupyter, nbformat, openpyxl.
