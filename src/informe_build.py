# -*- coding: utf-8 -*-
"""
StreamView Analytics - Generador del informe ejecutivo

Compone el informe ejecutivo en HTML listo para imprimir, tomando todas las
cifras desde data/processed/metricas.json y embebiendo las visualizaciones
como datos en linea, de modo que el archivo resultante es autocontenido y se
puede exportar a PDF desde el navegador (Ctrl+P > Guardar como PDF).

Uso:  python src/informe_build.py
"""
from pathlib import Path
import base64
import json

PROC = Path("data/processed")
IMG = Path("images")
OUT = Path("reports/informe_ejecutivo")


def n(x):
    """Entero con punto como separador de miles."""
    return f"{int(round(float(x))):,}".replace(",", ".")


def d(x, c=2):
    """Decimal con coma."""
    return f"{float(x):.{c}f}".replace(".", ",")


def img(nombre):
    ruta = IMG / f"{nombre}.png"
    b64 = base64.b64encode(ruta.read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


def figura(nombre, numero, pie):
    return (f'<figure><img src="{img(nombre)}" alt="Figura {numero}">'
            f'<figcaption><strong>Figura {numero}.</strong> {pie}</figcaption></figure>')


CSS = """
@page { size: A4; margin: 18mm 16mm 16mm; }
:root{
  --rojo:#E50914; --azul:#0072B2; --verde:#009E73; --naranja:#E69F00;
  --carbon:#221F1F; --gris:#6B6B6B; --linea:#DDD9D9; --fondo:#FBFAF9;
}
*{box-sizing:border-box}
body{
  margin:0; background:#fff; color:var(--carbon);
  font-family:"Georgia","Cambria",serif; font-size:10.7pt; line-height:1.62;
}
.hoja{max-width:187mm; margin:0 auto; padding:0 6mm 14mm}

h1,h2,h3,h4,.et,figcaption,table,.kpi,.portada-meta{
  font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;
}
h2{
  font-size:15.5pt; margin:0 0 3mm; padding-bottom:2mm;
  border-bottom:2.5px solid var(--rojo); letter-spacing:-.2px;
}
h2 .num{color:var(--rojo); margin-right:3mm; font-variant-numeric:tabular-nums}
h3{font-size:12pt; margin:7mm 0 2mm; color:#000}
h4{font-size:10.5pt; margin:5mm 0 1.5mm; color:var(--gris);
   text-transform:uppercase; letter-spacing:.7px}
p{margin:0 0 3mm; text-align:justify; hyphens:auto}
ul,ol{margin:0 0 3mm; padding-left:6mm}
li{margin-bottom:1.6mm}
strong{color:#000}

/* ---------- Portada ---------- */
.portada{
  height:252mm; display:flex; flex-direction:column; justify-content:space-between;
  page-break-after:always; padding:6mm 0;
}
.portada-marca{font-family:"Segoe UI",sans-serif; font-size:13pt; font-weight:700;
  letter-spacing:.5px}
.portada-marca span{color:var(--rojo)}
.portada-centro{border-left:5px solid var(--rojo); padding-left:9mm}
.portada h1{font-size:30pt; line-height:1.14; margin:0 0 4mm; letter-spacing:-.6px}
.portada .bajada{font-size:13pt; color:var(--gris); font-style:italic; margin:0}
.portada-meta{font-size:9.5pt; border-top:1px solid var(--linea); padding-top:4mm;
  display:grid; grid-template-columns:repeat(2,1fr); gap:3mm 8mm}
.portada-meta div span{display:block; font-size:8pt; text-transform:uppercase;
  letter-spacing:.8px; color:var(--gris); margin-bottom:.8mm}

/* ---------- Bloques ---------- */
section{page-break-before:always}
section.seguida{page-break-before:auto}
figure{margin:5mm 0; page-break-inside:avoid}
figure img{width:100%; display:block; border:1px solid var(--linea)}
figcaption{font-size:8.6pt; color:var(--gris); margin-top:1.8mm; line-height:1.45}

.kpis{display:grid; grid-template-columns:repeat(4,1fr); gap:3mm; margin:4mm 0 5mm}
.kpi{border:1px solid var(--linea); border-top:3px solid var(--rojo);
  padding:3mm 3mm 3.5mm; background:var(--fondo)}
.kpi .v{font-size:17pt; font-weight:700; line-height:1.1;
  font-variant-numeric:tabular-nums; font-family:"Segoe UI",sans-serif}
.kpi .e{font-size:7.8pt; color:var(--gris); text-transform:uppercase;
  letter-spacing:.5px; margin-top:1.2mm; line-height:1.3}
.kpi.a{border-top-color:var(--azul)} .kpi.v2{border-top-color:var(--verde)}
.kpi.n{border-top-color:var(--naranja)}

table{width:100%; border-collapse:collapse; font-size:9.2pt; margin:3mm 0 5mm;
  page-break-inside:avoid}
th{background:var(--carbon); color:#fff; text-align:left; padding:2.2mm 2.5mm;
  font-weight:600; font-size:8.6pt; text-transform:uppercase; letter-spacing:.4px}
td{padding:2mm 2.5mm; border-bottom:1px solid var(--linea); vertical-align:top}
tbody tr:nth-child(even){background:var(--fondo)}
td.num{text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap}

.destacado{background:var(--fondo); border-left:4px solid var(--rojo);
  padding:3.5mm 5mm; margin:4mm 0; page-break-inside:avoid}
.destacado p:last-child{margin-bottom:0}
.destacado.verde{border-left-color:var(--verde)}
.destacado.naranja{border-left-color:var(--naranja)}
.destacado .et{font-size:8pt; text-transform:uppercase; letter-spacing:.8px;
  color:var(--gris); font-weight:600; display:block; margin-bottom:1.5mm}

.hallazgo{border:1px solid var(--linea); padding:4mm 5mm; margin:4mm 0;
  page-break-inside:avoid}
.hallazgo h4{margin-top:0}
.hallazgo .linea{display:grid; grid-template-columns:22mm 1fr; gap:2mm;
  font-size:9.6pt; margin-bottom:1.5mm}
.hallazgo .linea b{font-family:"Segoe UI",sans-serif; font-size:8.4pt;
  text-transform:uppercase; letter-spacing:.5px; color:var(--gris); padding-top:.4mm}

.pasos{counter-reset:paso; list-style:none; padding:0; margin:4mm 0}
.pasos li{counter-increment:paso; position:relative; padding-left:11mm;
  margin-bottom:3.5mm; page-break-inside:avoid}
.pasos li::before{
  content:counter(paso); position:absolute; left:0; top:0;
  width:7.5mm; height:7.5mm; border-radius:50%; background:var(--carbon); color:#fff;
  font-family:"Segoe UI",sans-serif; font-size:9pt; font-weight:700;
  display:flex; align-items:center; justify-content:center;
}

footer{margin-top:9mm; padding-top:3mm; border-top:1px solid var(--linea);
  font-size:8.2pt; color:var(--gris); font-family:"Segoe UI",sans-serif}

@media screen{
  body{background:#EDEBEA; padding:8mm 0}
  .hoja{background:#fff; padding:14mm 16mm; box-shadow:0 2px 16px rgba(0,0,0,.14)}
  .aviso{max-width:187mm; margin:0 auto 6mm; background:#FFF6D6;
    border:1px solid #E6C84A; padding:3mm 5mm; font-size:9.5pt;
    font-family:"Segoe UI",sans-serif; border-radius:4px}
}
@media print{ .aviso{display:none} }
"""


def construir(m):
    gt = m["generos_top"]
    gb = m["generos_bajos"]
    go = m["generos_oportunidad"]
    mt = m["mercados_top"]
    esc = m["rentabilidad_por_escala"]
    peor = min(esc, key=lambda e: e["pct_rentables"])
    mejor = max(esc, key=lambda e: e["pct_rentables"])

    filas_oportunidad = "".join(
        f"<tr><td>{g['genero']}</td><td class='num'>{n(g['titulos'])}</td>"
        f"<td class='num'>{d(g['calificacion'])}</td></tr>" for g in go)

    filas_escala = "".join(
        f"<tr><td>{e['escala']}</td><td class='num'>{n(e['peliculas'])}</td>"
        f"<td class='num'>{d(e['pct_rentables'], 1)}%</td>"
        f"<td class='num'>{d(e['roi_mediano'])}x</td></tr>" for e in esc)

    filas_mercados = "".join(
        f"<tr><td>{x['idioma']}</td><td class='num'>{n(x['titulos'])}</td>"
        f"<td class='num'>{d(x['calificacion'])}</td></tr>" for x in mt)

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Informe ejecutivo · Inteligencia de Catálogo · StreamView Analytics</title>
<style>{CSS}</style></head>
<body>

<div class="aviso"><strong>Para exportar a PDF:</strong> presiona
<strong>Ctrl+P</strong> (o Cmd+P), elige <strong>Guardar como PDF</strong>,
tamaño A4, márgenes «predeterminados» y activa <strong>Gráficos de fondo</strong>.
Este aviso no se imprime.</div>

<div class="hoja">

<!-- ============ PORTADA ============ -->
<div class="portada">
  <div class="portada-marca">StreamView <span>Analytics</span></div>
  <div class="portada-centro">
    <h1>Inteligencia de Catálogo</h1>
    <p class="bajada">Qué mira la audiencia, qué valora,<br>y por qué no son lo mismo</p>
  </div>
  <div class="portada-meta">
    <div><span>Informe</span>Informe ejecutivo · Análisis exploratorio de contenidos</div>
    <div><span>Destinatario</span>Dirección de Contenidos, StreamView Analytics</div>
    <div><span>Metodología</span>CRISP-DM · Fases 1 a 6</div>
    <div><span>Período analizado</span>{m['anio_min']}–{m['anio_max']} · {n(m['titulos_total'])} títulos</div>
    <div><span>Asignatura</span>ADY1104 Visualización de Datos</div>
    <div><span>Evaluación</span>EP1 Encargo · EP2 Presentación</div>
  </div>
</div>

<!-- ============ RESUMEN EJECUTIVO ============ -->
<section class="seguida">
<h2><span class="num">—</span>Resumen ejecutivo</h2>

<p>StreamView Analytics dispone de un catálogo amplio y diverso, pero carece de una
lectura consolidada sobre <strong>qué contenido concentra la atención de su audiencia y qué
contenido esa audiencia realmente valora</strong>. Este informe analiza {n(m['titulos_total'])} títulos
estrenados entre {m['anio_min']} y {m['anio_max']} y documenta el hallazgo que ordena todas las
recomendaciones: <strong>popularidad y calidad percibida son dimensiones casi independientes</strong>.</p>

<div class="kpis">
  <div class="kpi"><div class="v">{n(m['titulos_total'])}</div>
    <div class="e">Títulos analizados</div></div>
  <div class="kpi a"><div class="v">r = {d(m['correlacion_pop_calidad_peliculas'])} / {d(m['correlacion_pop_calidad_series'])}</div>
    <div class="e">Correlación entre popularidad y calificación, en películas y en series</div></div>
  <div class="kpi v2"><div class="v">{n(m['cuad_calidad_sin_visibilidad'])}</div>
    <div class="e">Títulos de calidad sin visibilidad</div></div>
  <div class="kpi n"><div class="v">{d(m['pct_rentables'], 1)}%</div>
    <div class="e">Películas sobre su punto de equilibrio</div></div>
</div>

<h4>Los cinco hallazgos que sostienen este informe</h4>
<ol class="pasos">
<li><strong>Lo más popular no es lo mejor evaluado.</strong> Entre los {n(m['evaluables'])} títulos
con respaldo suficiente de votos, la correlación entre popularidad y calificación es de apenas
{d(m['correlacion_pop_calidad_peliculas'])} en películas y {d(m['correlacion_pop_calidad_series'])}
en series. Son dos ejes distintos y deben gestionarse por separado.</li>

<li><strong>Hay {n(m['cuad_calidad_sin_visibilidad'])} títulos de alta calificación y baja
visibilidad</strong> ({d(m['pct_calidad_sin_visibilidad'], 1)}% del catálogo evaluable). Es contenido
ya pagado que la audiencia valora cuando lo encuentra, pero que el sistema de descubrimiento
no está exponiendo.</li>

<li><strong>Las series superan a las películas los {m['anios_cubiertos']} años analizados,
sin excepción</strong>, con una brecha media de {d(m['brecha_series_peliculas'])} puntos y un mínimo
anual de {d(m['brecha_anual_minima'])}. No es una fluctuación: es una diferencia estructural de formato.</li>

<li><strong>El inglés concentra el {d(m['ingles_pct_catalogo'], 1)}% del catálogo calificado
pero ocupa el lugar {m['ingles_posicion']} de {m['mercados_analizados']} en calidad percibida</strong>
({d(m['ingles_calificacion'])} frente a {d(mt[0]['calificacion'])} del {mt[0]['idioma'].lower()}).
La inversión está concentrada donde la valoración es comparativamente más baja.</li>

<li><strong>El tramo medio de inversión es el peor negocio.</strong> Las películas de
{peor['escala'].lower().replace('(', '').replace(')', '')} tienen la menor tasa de éxito comercial
({d(peor['pct_rentables'], 1)}%), por debajo incluso de las producciones de bajo presupuesto.</li>
</ol>

<div class="destacado">
<span class="et">Recomendación principal</span>
<p>Separar la gestión de <strong>visibilidad</strong> de la gestión de <strong>adquisición</strong>.
Antes de comprar contenido nuevo, activar los {n(m['cuad_calidad_sin_visibilidad'])} títulos de calidad
que ya están en el catálogo sin exposición: es la única palanca de este informe con costo de
licenciamiento cero.</p>
</div>
</section>

<!-- ============ 1. PROBLEMA DE NEGOCIO ============ -->
<section>
<h2><span class="num">1</span>Descripción del problema de negocio</h2>

<h3>1.1 Contexto organizacional</h3>
<p>StreamView Analytics es una plataforma internacional de streaming digital que compite en un
mercado donde el costo de cambio para el usuario es prácticamente nulo: la cancelación está a un
clic de distancia. En ese escenario, la retención depende menos del tamaño del catálogo que de la
capacidad de la plataforma para <strong>poner el contenido correcto frente a la persona
correcta</strong>.</p>

<p>La organización acumula información sobre su catálogo —fichas de contenido, clasificaciones
de género, mercados de origen, métricas de atención y calificaciones agregadas de la audiencia—
pero esa información está dispersa y no se ha traducido en criterios de decisión. Las áreas de
contenido operan con intuición sectorial y con métricas de consumo aisladas.</p>

<h3>1.2 El problema</h3>
<p>La Dirección de Contenidos toma tres decisiones recurrentes y costosas —qué adquirir, qué
producir y qué promover— <strong>sin una lectura integrada que distinga entre contenido que
genera tráfico y contenido que genera satisfacción</strong>. Esa distinción importa porque
alimentan objetivos distintos: el tráfico sostiene el consumo del mes, la satisfacción sostiene
la renovación de la suscripción.</p>

<div class="destacado naranja">
<span class="et">Pregunta de negocio</span>
<p>¿Qué contenido del catálogo concentra la atención de la audiencia, qué contenido concentra
su valoración, y qué decisiones de adquisición, producción y promoción se desprenden de la
diferencia entre ambos?</p>
</div>

<h3>1.3 Criterio de éxito del proyecto</h3>
<p>El proyecto se considera exitoso si entrega a la Dirección de Contenidos: (a) evidencia
visual que permita distinguir atención de valoración; (b) una segmentación accionable del
catálogo; y (c) una herramienta de exploración autónoma que no dependa del equipo analítico
para responder preguntas de seguimiento.</p>
</section>

<!-- ============ 2. OBJETIVOS ============ -->
<section>
<h2><span class="num">2</span>Objetivos del proyecto</h2>

<h3>2.1 Objetivo general</h3>
<p>Desarrollar una solución de visualización de datos que permita a la Dirección de Contenidos de
StreamView Analytics comprender la composición y el desempeño de su catálogo, y fundamentar con
evidencia sus decisiones de adquisición, producción y promoción de contenido.</p>

<h3>2.2 Objetivos específicos</h3>
<ol>
<li>Integrar y depurar las fuentes de catálogo de películas y series en un conjunto analítico
único y trazable.</li>
<li>Caracterizar la composición del catálogo por género, formato, mercado de origen y año.</li>
<li>Determinar si existe relación entre la atención que recibe un título y la valoración que
obtiene de la audiencia.</li>
<li>Identificar segmentos de contenido con brechas entre calidad percibida y exposición.</li>
<li>Evaluar el desempeño comercial de la inversión en producción cinematográfica.</li>
<li>Construir un dashboard interactivo que permita explorar los hallazgos de forma autónoma.</li>
<li>Comunicar los resultados mediante una narrativa visual orientada a la decisión.</li>
</ol>

<h3>2.3 Alcance y límites</h3>
<p>El análisis se circunscribe a los <strong>atributos del catálogo y a las métricas agregadas de
recepción</strong> disponibles. No abarca datos individuales de usuarios —reproducciones,
suscripciones, dispositivos o sesiones—, por lo que las conclusiones se refieren al
comportamiento del contenido y no al de personas identificadas. Esta delimitación se retoma en
la evaluación crítica (sección 11).</p>
</section>

<!-- ============ 3. AUDIENCIA ============ -->
<section>
<h2><span class="num">3</span>Audiencia objetivo y propósito comunicacional</h2>

<h3>3.1 Caracterización de la audiencia</h3>
<p>La solución se diseñó para tres perfiles con necesidades de información distintas, y esa
diferencia determinó qué se muestra en cada producto del proyecto.</p>

<table>
<thead><tr><th style="width:23%">Audiencia</th><th style="width:27%">Qué decide</th>
<th style="width:27%">Qué necesita ver</th><th>Producto dirigido</th></tr></thead>
<tbody>
<tr><td><strong>Dirección de Contenidos</strong><br>(audiencia principal)</td>
<td>Qué adquirir, producir y renovar</td>
<td>Desempeño comparado por género, mercado y formato; brechas entre calidad y exposición</td>
<td>Informe ejecutivo y dashboard</td></tr>
<tr><td><strong>Comité ejecutivo</strong></td>
<td>Asignación de presupuesto de contenido</td>
<td>Pocos indicadores, conclusión explícita, implicancia económica</td>
<td>Resumen ejecutivo y presentación</td></tr>
<tr><td><strong>Equipo de producto y curatoría</strong></td>
<td>Qué promover y cómo ordenar el descubrimiento</td>
<td>Consulta granular por género, idioma, año y calificación</td>
<td>Dashboard interactivo</td></tr>
</tbody>
</table>

<h3>3.2 Propósito comunicacional</h3>
<p>El propósito no es descriptivo sino <strong>persuasivo y orientado a la decisión</strong>: la
solución busca que la Dirección de Contenidos adopte una distinción operativa entre atención y
valoración, y que reasigne esfuerzo de promoción hacia el contenido de calidad subexpuesto.</p>

<div class="destacado">
<span class="et">Mensaje único de la solución</span>
<p>StreamView Analytics no tiene un problema de catálogo: tiene un problema de visibilidad.
El contenido que su audiencia mejor valora ya está comprado, pero no se está mostrando.</p>
</div>

<h3>3.3 Estrategia de comunicación</h3>
<p>De ese propósito se derivan cuatro decisiones que atraviesan todos los productos visuales:</p>
<ul>
<li><strong>Titulares que afirman, no que rotulan.</strong> Cada figura se titula con su hallazgo
(«Lo más popular no es lo mejor evaluado») en lugar de con su contenido técnico
(«Popularidad vs. calificación»). El lector ejecutivo obtiene la conclusión aunque solo recorra
los títulos.</li>
<li><strong>Un solo color de acento por figura.</strong> El rojo se reserva para el dato
protagonista de cada gráfico; el resto del contenido se representa en grises. Esto dirige la
atención en lugar de dispersarla.</li>
<li><strong>Advertencias metodológicas visibles.</strong> Las limitaciones de los datos se
declaran dentro de las propias figuras, no en notas al pie, para evitar lecturas indebidas.</li>
<li><strong>Dos niveles de profundidad.</strong> El informe entrega la conclusión cerrada; el
dashboard permite verificarla y explorar casos particulares sin intermediarios.</li>
</ul>
</section>

<!-- ============ 4. METODOLOGÍA ============ -->
<section>
<h2><span class="num">4</span>Metodología: CRISP-DM</h2>

<p>El proyecto se estructuró siguiendo <strong>CRISP-DM</strong> (<em>Cross-Industry Standard
Process for Data Mining</em>), por tres razones: es independiente de la herramienta, es iterativo
—permite volver a fases anteriores cuando un hallazgo lo exige— y obliga a anclar el análisis en
una pregunta de negocio antes de tocar los datos.</p>

<table>
<thead><tr><th style="width:26%">Fase</th><th style="width:44%">Aplicación en este proyecto</th>
<th>Evidencia</th></tr></thead>
<tbody>
<tr><td><strong>1. Comprensión del negocio</strong></td>
<td>Definición del problema, la audiencia y el propósito comunicacional</td>
<td>Secciones 1 a 3</td></tr>
<tr><td><strong>2. Comprensión de los datos</strong></td>
<td>Perfilado de ambas fuentes, diagnóstico de calidad y detección del diseño muestral</td>
<td>Sección 5</td></tr>
<tr><td><strong>3. Preparación de los datos</strong></td>
<td>Limpieza, armonización de taxonomías e integración en un catálogo único</td>
<td>Sección 6 · <code>src/data_prep.py</code></td></tr>
<tr><td><strong>4. Modelado / Análisis</strong></td>
<td>Análisis exploratorio mediante visualizaciones y segmentación por cuadrantes</td>
<td>Secciones 7 y 8</td></tr>
<tr><td><strong>5. Evaluación</strong></td>
<td>Revisión crítica de la solución y de la validez de los hallazgos</td>
<td>Sección 11</td></tr>
<tr><td><strong>6. Despliegue</strong></td>
<td>Dashboard interactivo, narrativa visual e informe ejecutivo</td>
<td>Secciones 9 y 10</td></tr>
</tbody>
</table>

<div class="destacado verde">
<span class="et">Iteración documentada</span>
<p>La fase 4 obligó a retroceder a la fase 3. Al comparar géneros entre formatos se detectó que
las dos fuentes usaban <strong>taxonomías distintas</strong> —las películas separan «Action» y
«Adventure», las series los agrupan en «Action &amp; Adventure»—, lo que producía categorías
artificialmente exclusivas de un formato. Se volvió a la preparación de datos para armonizar
ambas taxonomías antes de continuar. Esta ida y vuelta es el comportamiento esperado en
CRISP-DM, no una desviación del método.</p>
</div>
</section>

<!-- ============ 5. FUENTES DE DATOS ============ -->
<section>
<h2><span class="num">5</span>Descripción de las fuentes de datos</h2>

<h3>5.1 Fuentes utilizadas</h3>
<p>Se trabajó con dos fuentes corporativas de catálogo, con estructura equivalente pero no
idéntica:</p>

<table>
<thead><tr><th style="width:36%">Archivo</th><th class="num">Registros</th>
<th class="num">Variables</th><th>Contenido</th></tr></thead>
<tbody>
<tr><td><code>netflix_movies_detailed_up_to_2025.csv</code></td>
<td class="num">{n(m['peliculas_total'])}</td><td class="num">18</td>
<td>Catálogo de películas con datos financieros</td></tr>
<tr><td><code>netflix_tv_shows_detailed_up_to_2025.csv</code></td>
<td class="num">{n(m['series_total'] + m['series_id_duplicados'])}</td><td class="num">16</td>
<td>Catálogo de series, sin datos financieros</td></tr>
</tbody>
</table>

<h3>5.2 Variables relevantes para el análisis</h3>
<table>
<thead><tr><th style="width:22%">Variable</th><th style="width:14%">Tipo</th>
<th>Rol en el análisis</th></tr></thead>
<tbody>
<tr><td><code>popularity</code></td><td>Numérica continua</td>
<td><strong>Eje de atención.</strong> Índice de interés reciente en el título</td></tr>
<tr><td><code>vote_average</code></td><td>Numérica continua (0-10)</td>
<td><strong>Eje de valoración.</strong> Calificación promedio de la audiencia</td></tr>
<tr><td><code>vote_count</code></td><td>Numérica discreta</td>
<td>Respaldo estadístico de la calificación; define qué títulos son evaluables</td></tr>
<tr><td><code>genres</code></td><td>Categórica múltiple</td>
<td>Segmentación temática del catálogo</td></tr>
<tr><td><code>language</code></td><td>Categórica</td>
<td>Mercado de origen del contenido</td></tr>
<tr><td><code>release_year</code></td><td>Temporal</td>
<td>Eje de evolución ({m['anio_min']}-{m['anio_max']})</td></tr>
<tr><td><code>budget</code> / <code>revenue</code></td><td>Numéricas continuas</td>
<td>Desempeño comercial; solo disponibles en películas</td></tr>
<tr><td><code>type</code></td><td>Categórica binaria</td>
<td>Formato: película o serie</td></tr>
</tbody>
</table>

<h3>5.3 Hallazgo estructural: el diseño muestral</h3>
<div class="destacado naranja">
<span class="et">Advertencia metodológica determinante</span>
<p>Ambas fuentes contienen <strong>exactamente {n(m['titulos_por_anio_formato'])} títulos por cada
año</strong> entre {m['anio_min']} y {m['anio_max']}. No se trata del catálogo completo sino de una
<strong>muestra estratificada por año</strong>. La consecuencia es directa y condiciona todo el
informe: <strong>el volumen anual es constante por diseño, por lo que este análisis no puede
—y no debe— sostener ninguna conclusión sobre crecimiento o contracción del catálogo en el
tiempo</strong>. Todas las comparaciones temporales de este informe son de <em>composición</em> y
<em>calidad</em>, nunca de volumen.</p>
</div>

<h3>5.4 Diagnóstico de calidad de los datos</h3>
<table>
<thead><tr><th style="width:30%">Hallazgo</th><th style="width:34%">Magnitud</th>
<th>Tratamiento aplicado</th></tr></thead>
<tbody>
<tr><td>Columna <code>rating</code> redundante</td>
<td>Idéntica a <code>vote_average</code> en el 100% de los registros</td>
<td>Eliminada</td></tr>
<tr><td>Columna <code>duration</code> sin información</td>
<td>100% nula en películas; valor constante «1 Seasons» en series</td>
<td>Eliminada</td></tr>
<tr><td>Calificaciones falsas en cero</td>
<td>{n(m['sin_calificar_peliculas'])} películas y {n(m['sin_calificar_series'])} series sin votos
figuraban con calificación 0,0</td>
<td>Convertidas a valor ausente: sin votos no es lo mismo que mala evaluación</td></tr>
<tr><td>Valores financieros enmascarados</td>
<td>{d(m['budget_ceros_pct'], 1)}% de presupuestos y {d(m['revenue_ceros_pct'], 1)}% de ingresos en cero</td>
<td>Tratados como dato faltante; el análisis financiero usa solo {n(m['peliculas_con_finanzas'])} películas</td></tr>
<tr><td>Identificadores duplicados</td>
<td>{m['series_id_duplicados']} series con <code>show_id</code> repetido</td>
<td>Deduplicadas</td></tr>
<tr><td>Taxonomías de género divergentes</td>
<td>11 géneros exclusivos de películas y 9 exclusivos de series</td>
<td>Armonizadas a una taxonomía única en español</td></tr>
<tr><td>Fecha de incorporación no confiable</td>
<td><code>date_added</code> cae siempre en el mismo año que <code>release_year</code></td>
<td>Descartada como eje temporal</td></tr>
<tr><td>Ausencias en metadatos de series</td>
<td>{d(m['director_nulos_series_pct'], 1)}% sin director; {d(m['descripcion_nulos_series_pct'], 1)}% sin sinopsis</td>
<td>Marcadas explícitamente; no se usan como variables de análisis</td></tr>
</tbody>
</table>

<p>Tras la depuración, el conjunto analítico reúne <strong>{n(m['titulos_total'])} títulos</strong>,
de los cuales <strong>{n(m['calificados'])} ({d(m['calificados_pct'], 1)}%) cuentan con
calificación válida</strong> y constituyen la base de todo análisis de valoración.</p>
</section>

<!-- ============ 6. PREPARACIÓN ============ -->
<section>
<h2><span class="num">6</span>Preparación e integración de los datos</h2>

<p>La preparación se implementó como un proceso reproducible en <code>src/data_prep.py</code>, que
parte de los archivos originales sin modificarlos y genera los conjuntos analíticos. Ejecutarlo
reconstruye el proyecto completo desde cero.</p>

<h3>6.1 Decisiones de transformación</h3>
<ul>
<li><strong>Distinguir ausencia de valor cero.</strong> Un título sin votos no tiene calificación
0,0: no tiene calificación. Promediarlos como ceros habría hundido artificialmente la media de las
series, donde el {d(m['sin_calificar_series'] / m['series_total'] * 100, 1)}% carece de votos.
Lo mismo aplica a presupuestos e ingresos en cero.</li>
<li><strong>Armonizar las taxonomías de género.</strong> Se unificaron ambas nomenclaturas en una
taxonomía única en español, fusionando categorías equivalentes y deduplicando los títulos que al
fusionarse quedaban asignados dos veces al mismo género resultante.</li>
<li><strong>Definir el umbral de evaluabilidad.</strong> Para los análisis de relación entre
popularidad y calidad se exige un mínimo de <strong>{m['umbral_votos']} votos</strong>. Una
calificación sostenida por dos o tres votos no es una señal, es ruido. El umbral reduce el universo
a {n(m['evaluables'])} títulos, a cambio de una base estadística confiable.</li>
<li><strong>Integrar sin perder especificidad.</strong> El catálogo unificado conserva solo las
variables comunes a ambos formatos; el análisis financiero se realiza sobre el conjunto de
películas, que es el único que posee esas variables.</li>
</ul>

<h3>6.2 Conjuntos analíticos generados</h3>
<table>
<thead><tr><th style="width:38%">Archivo</th><th class="num">Registros</th><th>Uso</th></tr></thead>
<tbody>
<tr><td><code>catalogo_unificado.csv</code></td><td class="num">{n(m['titulos_total'])}</td>
<td>Base común de películas y series</td></tr>
<tr><td><code>catalogo_generos.csv</code></td><td class="num">—</td>
<td>Tabla larga título-género, para análisis sin doble conteo</td></tr>
<tr><td><code>peliculas_limpio.csv</code></td><td class="num">{n(m['peliculas_total'])}</td>
<td>Análisis financiero y de retorno</td></tr>
<tr><td><code>series_limpio.csv</code></td><td class="num">{n(m['series_total'])}</td>
<td>Análisis específico del formato serie</td></tr>
<tr><td><code>metricas.json</code></td><td class="num">—</td>
<td>Cifras consolidadas que alimentan este informe y la presentación</td></tr>
</tbody>
</table>
</section>

<!-- ============ 7. ANÁLISIS EXPLORATORIO ============ -->
<section>
<h2><span class="num">7</span>Análisis exploratorio mediante visualizaciones</h2>

<h3>7.1 Composición del catálogo</h3>
{figura('01_composicion_generos', 1, 'Títulos por género y formato. Drama y Comedia dominan ambos formatos. Las categorías marcadas como no disponibles para series no indican ausencia de ese contenido, sino que la taxonomía de origen de las series no contempla esa categoría.')}

<p>La oferta está fuertemente concentrada: <strong>{m['generos_volumen'][0]['genero']}</strong>
encabeza el catálogo con {n(m['generos_volumen'][0]['titulos'])} títulos calificados, seguido de
{m['generos_volumen'][1]['genero']} ({n(m['generos_volumen'][1]['titulos'])}). Esta concentración
es el punto de partida: el catálogo apuesta por géneros masivos, y conviene contrastar esa apuesta
con la valoración que obtiene cada uno.</p>

<h3>7.2 Distribución de la calidad percibida</h3>
{figura('02_distribucion_calificaciones', 2, 'Distribución de calificaciones por formato, excluyendo títulos sin votos. Las líneas punteadas marcan la mediana de cada grupo.')}

<p>Las dos distribuciones no se superponen: las series se concentran en calificaciones
sistemáticamente más altas (mediana {d(m['calificacion_mediana_series'])}) que las películas
(mediana {d(m['calificacion_mediana_peliculas'])}). Trabajar con las distribuciones completas y no
solo con los promedios permite ver que no se trata de unos pocos casos extremos, sino de un
desplazamiento de toda la curva.</p>

<h3>7.3 Cómo se reparte la atención</h3>
{figura('03_distribucion_popularidad', 3, 'Distribución del índice de popularidad en escala logarítmica. En escala lineal, el 99% de los títulos colapsaría en la primera barra.')}

<p>La atención de la audiencia sigue una distribución de cola larga extrema: el título más popular
supera <strong>{n(m['ratio_max_mediana'])} veces</strong> al título mediano, y solo
{n(m['titulos_sobre_p99'])} títulos superan el percentil 99. Para la operación esto significa que
<strong>la enorme mayoría del catálogo vive con una exposición marginal</strong>, y que cualquier
mejora en el descubrimiento actúa sobre una base muy amplia de contenido infrautilizado.</p>

<h3>7.4 Hallazgo central: atención frente a valoración</h3>
{figura('04_popularidad_vs_calidad', 4, 'Popularidad frente a calificación, con cuadrantes definidos por las medianas de ambas variables. Solo títulos con al menos 50 votos.')}

<div class="hallazgo">
<h4>Hallazgo 1 · Popularidad y calidad son ejes independientes</h4>
<div class="linea"><b>Evidencia</b><span>La correlación entre ambas variables es de
{d(m['correlacion_pop_calidad_peliculas'])} en películas ({n(m['evaluables_peliculas'])} títulos) y
{d(m['correlacion_pop_calidad_series'])} en series ({n(m['evaluables_series'])}). Estadísticamente,
saber cuán popular es un título no permite anticipar cómo será calificado.</span></div>
<div class="linea"><b>Lectura</b><span>La nube de puntos no tiene pendiente: se extiende en
horizontal. Existe contenido muy popular con calificaciones bajas
({n(m['cuad_populares_mal_evaluados'])} títulos) y contenido muy bien evaluado que casi nadie ve
({n(m['cuad_calidad_sin_visibilidad'])} títulos).</span></div>
<div class="linea"><b>Implicancia</b><span>Gestionar el catálogo con una sola métrica es
inevitablemente incorrecto. Optimizar por popularidad degrada la satisfacción; optimizar por
calificación sacrifica tráfico. Son objetivos que requieren instrumentos separados.</span></div>
</div>

<div class="destacado naranja">
<span class="et">Decisión metodológica</span>
<p>El índice de popularidad <strong>no es comparable entre formatos</strong>: su mediana en series
({d(m['mediana_popularidad_series'], 1)}) cuadruplica la de las películas
({d(m['mediana_popularidad_peliculas'], 1)}), porque la fuente lo calcula de manera distinta según
el tipo de contenido. Por eso <strong>tanto la correlación como los cuadrantes se calculan dentro
de cada formato</strong>. Usar una mediana conjunta habría convertido el corte de popularidad en
un simple separador de formato —dejando, por ejemplo, un cuadrante entero sin una sola serie— y
habría producido una segmentación que mide el tipo de contenido en lugar de su visibilidad
relativa.</p>
</div>

<p>Los cuatro cuadrantes traducen esa nube en una segmentación operativa. Cada título se compara
contra la mediana de su propio formato, de modo que «baja visibilidad» significa baja respecto de
sus pares comparables:</p>
<table>
<thead><tr><th style="width:26%">Segmento</th><th class="num">Títulos</th>
<th style="width:26%">Qué es</th><th>Acción recomendada</th></tr></thead>
<tbody>
<tr><td><strong>Éxitos consolidados</strong></td><td class="num">{n(m['cuad_exitos'])}</td>
<td>Alta atención y alta valoración</td>
<td>Proteger: asegurar renovación de derechos y continuidad</td></tr>
<tr><td><strong>Calidad sin visibilidad</strong></td>
<td class="num">{n(m['cuad_calidad_sin_visibilidad'])}</td>
<td>Alta valoración, baja atención</td>
<td><strong>Promover: máxima prioridad, costo marginal cero</strong></td></tr>
<tr><td><strong>Populares mal evaluados</strong></td>
<td class="num">{n(m['cuad_populares_mal_evaluados'])}</td>
<td>Alta atención, baja valoración</td>
<td>Vigilar: generan tráfico pero erosionan la percepción de calidad</td></tr>
<tr><td><strong>Bajo rendimiento</strong></td><td class="num">{n(m['cuad_bajo_rendimiento'])}</td>
<td>Baja atención y baja valoración</td>
<td>Revisar: candidatos naturales a depuración del catálogo</td></tr>
</tbody>
</table>

<h3>7.5 Dónde invierte el catálogo y qué rinde mejor</h3>
{figura('05_generos_calidad_volumen', 5, 'Cada género según su volumen de títulos calificados y su calificación promedio. El tamaño de la burbuja representa la popularidad mediana; en verde, los géneros con calidad sobre la mediana y oferta bajo la mediana.')}

<div class="hallazgo">
<h4>Hallazgo 2 · Los géneros mejor evaluados son los menos representados</h4>
<div class="linea"><b>Evidencia</b><span>{gt[0]['genero']} ({d(gt[0]['calificacion'])}),
{gt[1]['genero']} ({d(gt[1]['calificacion'])}) y {gt[2]['genero']}
({d(gt[2]['calificacion'])}) lideran la valoración. En el extremo opuesto,
{gb[0]['genero']} ({d(gb[0]['calificacion'])}) y {gb[1]['genero']}
({d(gb[1]['calificacion'])}) acumulan {n(gb[0]['titulos'] + gb[1]['titulos'])} títulos
con las calificaciones más bajas del catálogo.</span></div>
<div class="linea"><b>Implicancia</b><span>Existe una franja de géneros de alto rendimiento y baja
presencia que constituye la oportunidad de crecimiento más clara del catálogo.</span></div>
</div>

<table>
<thead><tr><th>Género con calidad alta y oferta reducida</th><th class="num">Títulos calificados</th>
<th class="num">Calificación</th></tr></thead>
<tbody>{filas_oportunidad}</tbody>
</table>

<h3>7.6 Evolución temporal</h3>
{figura('06_evolucion_temporal', 6, 'Calificación promedio anual por formato. El panel inferior muestra la proporción de títulos sin calificar, que advierte sobre la menor madurez de votos en los años recientes. La zona sombreada marca el año con cobertura parcial.')}

<div class="hallazgo">
<h4>Hallazgo 3 · La ventaja de las series es estructural, no coyuntural</h4>
<div class="linea"><b>Evidencia</b><span>Las series superan a las películas en los
{m['anios_series_sobre_peliculas']} años analizados sin una sola excepción. La brecha media es de
{d(m['brecha_series_peliculas'])} puntos y nunca baja de {d(m['brecha_anual_minima'])}.</span></div>
<div class="linea"><b>Lectura</b><span>Ambos formatos mejoran de forma sostenida —las series pasan
de {d(m['calificacion_series_inicio'])} a {d(m['calificacion_series_fin'])} y las películas de
{d(m['calificacion_peliculas_inicio'])} a {d(m['calificacion_peliculas_fin'])}—, pero la distancia
entre ellos se mantiene.</span></div>
<div class="linea"><b>Control</b><span>Las series calificadas acumulan menos votos que las
películas, por lo que podría sospecharse que la ventaja es un artefacto. No lo es: al exigir un
mínimo de {m['umbral_votos']} votos a ambos formatos la brecha <strong>aumenta</strong> a
{d(m['brecha_series_peliculas_controlada'])} puntos y sigue siendo positiva en los
{m['anios_series_sobre_peliculas_controlada']} años, con un mínimo de
{d(m['brecha_anual_minima_controlada'])}.</span></div>
<div class="linea"><b>Cautela</b><span>El último año tiene una proporción de títulos sin calificar
muy superior al resto, por lo que su promedio se calcula sobre una fracción pequeña y no es
comparable con los anteriores.</span></div>
</div>

<h3>7.7 Estabilidad de la jerarquía entre géneros</h3>
{figura('09_heatmap_genero_ano', 7, 'Calificación promedio por género y año, con las filas ordenadas por calificación global. El color codifica la intensidad de la valoración.')}

<p>El mapa de calor revela dos patrones simultáneos: un <strong>verdeo progresivo de izquierda a
derecha</strong> —todos los géneros mejoran su valoración con el tiempo— y una
<strong>jerarquía vertical estable</strong>: el orden relativo entre géneros no cambia. Los
géneros mejor evaluados lo son durante los {m['anios_cubiertos']} años, y los peor evaluados
también. Para la planificación esto es una buena noticia: el desempeño por género es predecible.</p>

<h3>7.8 Mercados de origen</h3>
{figura('07_mercados_idiomas', 8, 'Calificación promedio por idioma original, en mercados con al menos 300 títulos calificados. Se mantiene la línea base en cero para no exagerar las diferencias entre mercados.')}

<div class="hallazgo">
<h4>Hallazgo 4 · La concentración del catálogo no coincide con la valoración</h4>
<div class="linea"><b>Evidencia</b><span>El inglés reúne {n(m['ingles_titulos'])} títulos
—el {d(m['ingles_pct_catalogo'], 1)}% del catálogo calificado— pero ocupa la posición
{m['ingles_posicion']} de {m['mercados_analizados']} en calificación promedio
({d(m['ingles_calificacion'])}).</span></div>
<div class="linea"><b>Contraste</b><span>El {mt[0]['idioma'].lower()} alcanza
{d(mt[0]['calificacion'])} con {n(mt[0]['titulos'])} títulos y el {mt[1]['idioma'].lower()}
{d(mt[1]['calificacion'])} con {n(mt[1]['titulos'])}: una ventaja de
{d(m['brecha_mejor_mercado_ingles'])} puntos sobre el mercado dominante.</span></div>
<div class="linea"><b>Implicancia</b><span>Existe margen para rebalancear la adquisición hacia
mercados que hoy tienen menor presencia y mejor recepción.</span></div>
</div>

<table>
<thead><tr><th>Mercado mejor evaluado</th><th class="num">Títulos calificados</th>
<th class="num">Calificación</th></tr></thead>
<tbody>{filas_mercados}</tbody>
</table>

<h3>7.9 Desempeño comercial de la inversión</h3>
{figura('08_financiero', 9, 'Presupuesto frente a ingresos en escala logarítmica, sobre las películas con dato financiero informado. La diagonal marca el punto de equilibrio: por encima hay retorno positivo.')}

<p>Sobre las {n(m['peliculas_con_finanzas'])} películas con información financiera confiable, el
<strong>{d(m['pct_rentables'], 1)}% supera su punto de equilibrio</strong>, con un retorno mediano
de {d(m['roi_mediano'])} veces lo invertido y un presupuesto mediano de
{d(m['presupuesto_mediano_millones'], 1)} millones de dólares.</p>

{figura('10_rentabilidad_escala', 10, 'Tasa de éxito comercial y retorno mediano por escala de presupuesto. La altura codifica la proporción de películas rentables; la etiqueta interior, el retorno mediano.')}

<div class="hallazgo">
<h4>Hallazgo 5 · El riesgo comercial no crece con el tamaño de la apuesta</h4>
<div class="linea"><b>Evidencia</b><span>La tasa de éxito aumenta con la escala de inversión:
{d(esc[0]['pct_rentables'], 1)}% en presupuestos bajos, {d(esc[1]['pct_rentables'], 1)}% en el
tramo medio, {d(esc[2]['pct_rentables'], 1)}% en el alto y {d(esc[3]['pct_rentables'], 1)}% en el
muy alto.</span></div>
<div class="linea"><b>Punto ciego</b><span>El peor desempeño no está en los extremos sino en el
<strong>tramo medio</strong>: {d(peor['pct_rentables'], 1)}% de éxito y un retorno mediano de
{d(peor['roi_mediano'])}x, por debajo incluso de las producciones de bajo presupuesto. Es el tramo
con mayor número de películas ({n(peor['peliculas'])}), es decir, donde se concentra el
riesgo.</span></div>
<div class="linea"><b>Cautela</b><span>Solo {d(m['peliculas_con_finanzas_pct'], 1)}% de las
películas informa datos financieros, y es plausible que las producciones que los reportan sean
las de mayor visibilidad comercial. La lectura debe tomarse como indicativa.</span></div>
</div>

<p>Una observación adicional refuerza el hallazgo central: los ingresos correlacionan fuertemente
con el presupuesto ({d(m['corr_presupuesto_ingreso'])}) y con el número de votos
({d(m['corr_votos_ingreso'])}) —es decir, con la escala de exposición— pero muy débilmente con la
calificación ({d(m['corr_calificacion_ingreso'])}). <strong>La taquilla mide alcance, no
calidad.</strong></p>

<h3>7.10 Rentabilidad por temática</h3>
{figura('13_roi_genero', 11, 'Retorno de inversión mediano por género, solo películas con dato financiero válido. En rojo, los tres géneros más rentables. Géneros ordenados de menor a mayor retorno; se excluyen los que registran menos de 30 películas con dato financiero.')}

<p>Además de la escala de inversión, la temática del contenido también predice el retorno.
{m['roi_genero_top'][0]['genero']} ({d(m['roi_genero_top'][0]['roi'])}x),
{m['roi_genero_top'][1]['genero'].lower()} ({d(m['roi_genero_top'][1]['roi'])}x) y
{m['roi_genero_top'][2]['genero'].lower()} ({d(m['roi_genero_top'][2]['roi'])}x) son las temáticas
que más retorno generan por dólar invertido, mientras que {m['roi_genero_bottom']['genero'].lower()}
es la única que en promedio no alcanza a recuperar su inversión
({d(m['roi_genero_bottom']['roi'])}x). Se usa la mediana y no el promedio porque el ROI tiene una
cola de outliers extrema —un puñado de éxitos de taquilla infla artificialmente el promedio de
varios géneros— y la mediana describe mejor el retorno de la producción típica.</p>
</section>

<!-- ============ 8. JUSTIFICACIÓN GRÁFICA ============ -->
<section>
<h2><span class="num">8</span>Justificación de las representaciones gráficas</h2>

<p>Las 12 figuras del informe se implementaron en <strong>Python con Matplotlib</strong>, a través
de un módulo de estilo propio (<code>src/estilo.py</code>) que centraliza paleta, tipografía y
reglas de diseño para que ninguna decisión visual se tome de forma aislada. El dashboard
interactivo de la sección 10 se implementó en <strong>Plotly</strong>. Ambas herramientas se
eligieron por ser librerías de código abierto que permiten control total sobre cada atributo
visual —color, escala, anotación— y porque generan salidas reproducibles desde los mismos scripts
que procesan los datos, sin pasos manuales entre el análisis y la figura final.</p>

<p>Cada representación se seleccionó a partir de la naturaleza de las variables y de la tarea de
lectura que debía habilitar, no por variedad visual.</p>

<table>
<thead><tr><th style="width:21%">Figura</th><th style="width:18%">Representación</th>
<th>Fundamento técnico</th></tr></thead>
<tbody>
<tr><td>1 · Composición</td><td>Barras horizontales agrupadas</td>
<td>Comparación de magnitudes entre categorías nominales. La longitud es el atributo visual que el
sistema perceptual decodifica con mayor precisión. La orientación horizontal evita rotar etiquetas
largas, reduciendo la carga cognitiva de lectura.</td></tr>
<tr><td>2 · Calificaciones</td><td>Histogramas superpuestos</td>
<td>Variable continua: interesa la forma completa de la distribución. Un gráfico de barras de
promedios habría ocultado que el desplazamiento afecta a toda la curva y no a casos extremos.</td></tr>
<tr><td>3 · Popularidad</td><td>Histograma en escala logarítmica</td>
<td>La variable abarca tres órdenes de magnitud. En escala lineal el 99% de los datos colapsa en
la primera barra: la escala log es condición necesaria para que el gráfico comunique.</td></tr>
<tr><td>4 · Atención vs. calidad</td><td>Dispersión con cuadrantes</td>
<td>Relación entre dos variables continuas: la posición conjunta es el único codificador que
permite ver —o descartar— la correlación. Los cuadrantes sobre las medianas traducen la nube en
cuatro decisiones accionables.</td></tr>
<tr><td>5 · Géneros</td><td>Dispersión con burbujas</td>
<td>Tres variables simultáneas: posición X e Y para las dos críticas (lectura precisa) y tamaño
para la tercera, que solo requiere comparación gruesa. Las etiquetas se ubican con un algoritmo de
prevención de colisiones para garantizar legibilidad.</td></tr>
<tr><td>6 · Evolución</td><td>Líneas con panel de contexto</td>
<td>La línea es el estándar para series temporales porque codifica continuidad y pendiente. El
panel inferior expone la limitación de los datos junto al gráfico, evitando lecturas
indebidas.</td></tr>
<tr><td>7 · Género × año</td><td>Mapa de calor</td>
<td>Dos dimensiones más una medida: el color permite leer la matriz completa de un vistazo, algo
imposible con doce líneas superpuestas. Las filas se ordenan por calificación para que el eje
vertical también comunique.</td></tr>
<tr><td>8 · Mercados</td><td>Barras horizontales ordenadas</td>
<td>En un ranking es el orden lo que comunica. Se conserva la línea base en cero: truncar el eje
habría exagerado visualmente diferencias de décimas.</td></tr>
<tr><td>9 · Financiero</td><td>Dispersión log-log con diagonal</td>
<td>Ambas variables cubren varios órdenes de magnitud. La diagonal de equilibrio convierte una
comparación numérica en una lectura posicional inmediata: por encima o por debajo.</td></tr>
<tr><td>10 · Rentabilidad</td><td>Barras verticales con doble codificación</td>
<td>Categorías ordinales (tramos de presupuesto) en su orden natural. La altura muestra la tasa de
éxito y la etiqueta interior el retorno, evitando que el lector deba cruzar dos gráficos.</td></tr>
<tr><td>11 · ROI por género</td><td>Barras horizontales ordenadas</td>
<td>Ranking de categorías nominales: el orden comunica, no el color. Se reserva el acento rojo
para los tres géneros de mayor retorno, y la mediana evita que un puñado de outliers financieros
distorsione la lectura del género típico.</td></tr>
<tr><td>12 · Joyas ocultas</td><td>Barras horizontales + barras agrupadas</td>
<td>Panel doble: ranking de géneros a la izquierda, comparación directa de calidad (joyas vs.
resto) por formato a la derecha. Separar ambas preguntas evita saturar un único gráfico.</td></tr>
<tr><td>13 · Momentum de género</td><td>Barras horizontales de variación</td>
<td>La variable es un cambio porcentual, no una magnitud absoluta: el eje centrado en cero y el
color (verde/rojo vs. gris) separan visualmente los géneros que ganan interés de los que lo
pierden.</td></tr>
</tbody>
</table>

<h3>8.1 Principios transversales de diseño</h3>
<ul>
<li><strong>Jerarquía por color.</strong> Un único acento rojo por figura, reservado al dato
protagonista; el resto en grises. La paleta categórica es segura para daltonismo.</li>
<li><strong>Titulares que afirman el hallazgo.</strong> El título de cada figura es su conclusión;
el subtítulo aporta el detalle técnico y el tamaño muestral.</li>
<li><strong>Reducción de carga cognitiva.</strong> Sin efectos tridimensionales, sin rejillas
redundantes, sin bordes innecesarios; etiquetado directo en lugar de leyendas cuando es
posible.</li>
<li><strong>Honestidad visual.</strong> Líneas base en cero en los gráficos de barras, escalas
logarítmicas declaradas explícitamente en los ejes y tamaños muestrales visibles en cada
figura.</li>
<li><strong>Convención local.</strong> Coma decimal y punto de miles en todo el proyecto, incluido
el dashboard.</li>
</ul>
</section>

<!-- ============ 9. NARRATIVA VISUAL ============ -->
<section>
<h2><span class="num">9</span>Desarrollo de la narrativa visual (Data Storytelling)</h2>

<p>La narrativa se estructuró sobre el arco clásico de <em>data storytelling</em> —contexto,
tensión, resolución— porque la audiencia principal no necesita un recorrido por los datos sino una
razón para cambiar una decisión.</p>

<ol class="pasos">
<li><strong>Contexto: el catálogo es amplio y su calidad mejora.</strong><br>
Se abre con la composición (Figura 1) y la distribución de calificaciones (Figura 2). Se establece
que no hay un problema evidente de calidad: el catálogo mejora año a año en ambos formatos.</li>

<li><strong>Tensión: la atención no se reparte, se concentra.</strong><br>
La Figura 3 introduce el desequilibrio: el título más popular supera {n(m['ratio_max_mediana'])}
veces al mediano. La audiencia está mirando una fracción mínima de lo que la plataforma
ofrece.</li>

<li><strong>Giro: lo que se mira no es lo que se valora.</strong><br>
La Figura 4 es el punto de inflexión del relato. Si popularidad y calidad coincidieran, la
concentración de atención sería eficiente. Con correlaciones de
{d(m['correlacion_pop_calidad_peliculas'])} y {d(m['correlacion_pop_calidad_series'])}, no lo es:
hay {n(m['cuad_calidad_sin_visibilidad'])} títulos bien evaluados que la audiencia no está
encontrando.</li>

<li><strong>Profundización: dónde está esa brecha.</strong><br>
Las Figuras 5 a 8 localizan el problema en dimensiones accionables —géneros infrarrepresentados,
mercados subexplotados— y confirman que el patrón es estable en el tiempo, no una
anomalía.</li>

<li><strong>Cierre económico: qué cuesta y qué rinde.</strong><br>
Las Figuras 9 a 11 aterrizan la discusión en términos de inversión, y muestran que ni la escala
del presupuesto ni la temática elegida garantizan por sí solas el retorno.</li>

<li><strong>Resolución: la acción de costo cero.</strong><br>
La narrativa cierra sobre una conclusión que no requiere presupuesto adicional: activar el
contenido de calidad que ya está en el catálogo.</li>
</ol>

<div class="destacado">
<span class="et">Adaptación del mensaje por audiencia</span>
<p>El mismo hallazgo se comunica en tres registros distintos. Al <strong>comité ejecutivo</strong>
se le presenta como oportunidad de eficiencia: valor ya pagado que no se está capturando. A la
<strong>Dirección de Contenidos</strong> se le entrega como segmentación operativa de cuatro
cuadrantes con acciones diferenciadas. Al <strong>equipo de producto</strong> se le ofrece el
dashboard para que identifique los títulos concretos sobre los que intervenir.</p>
</div>

<h3>Integración de recursos de comunicación oral, escrita y visual</h3>
<p>La narrativa se sostiene sobre tres canales que se refuerzan entre sí y no compiten por la
atención del receptor:</p>
<table>
<thead><tr><th style="width:16%">Recurso</th><th style="width:32%">Cómo se integra</th>
<th>Dónde ocurre</th></tr></thead>
<tbody>
<tr><td><strong>Oral</strong></td>
<td>Explicación en vivo del arco contexto-tensión-giro-resolución durante la defensa; cada
integrante narra el tramo del hallazgo que le corresponde y responde preguntas cruzadas sobre el
resto.</td>
<td>Defensa técnica (10 min de exposición + 5 min de preguntas)</td></tr>
<tr><td><strong>Escrita</strong></td>
<td>Titulares que afirman el hallazgo, subtítulos con el detalle técnico y tamaño muestral,
anotaciones dentro de cada figura, y el desarrollo argumentado de este informe.</td>
<td>Informe ejecutivo · rótulos de las Figuras 1 a 12</td></tr>
<tr><td><strong>Visual</strong></td>
<td>Paleta de acento único por figura, iconografía de color consistente para los cuatro
cuadrantes de negocio, y el dashboard interactivo para exploración en tiempo real.</td>
<td>Figuras del informe · Presentación ejecutiva · Dashboard</td></tr>
</tbody>
</table>
</section>

<!-- ============ 10. DASHBOARD ============ -->
<section>
<h2><span class="num">10</span>Diseño e implementación del dashboard</h2>

<p>El informe entrega conclusiones cerradas; el dashboard permite verificarlas y explorar casos
particulares. Se implementó en <strong>HTML con Plotly</strong>, en un único archivo autocontenido
que no requiere servidor ni instalación: se abre directamente en el navegador.</p>

<h3>10.1 Decisión técnica</h3>
<p>Se evaluaron herramientas de escritorio (Power BI, Tableau) y frameworks con servidor
(Streamlit, Dash). Se optó por HTML autocontenido porque es el único formato que
<strong>cualquier destinatario puede abrir sin licencia, sin instalación y sin ejecutar un
servidor</strong>, condición necesaria para que la solución circule dentro de la organización. Los
{n(m['registros_dashboard'])} registros se embeben en el archivo y el filtrado se resuelve en el
navegador, de modo que la interacción es inmediata y funciona sin conexión.</p>

<h3>10.2 Componentes implementados</h3>
<table>
<thead><tr><th style="width:24%">Componente</th><th>Implementación</th></tr></thead>
<tbody>
<tr><td><strong>Indicadores (KPI)</strong></td>
<td>Cuatro tarjetas —títulos en selección, calificación promedio, popularidad mediana y porcentaje
sin calificar— que se recalculan con cada filtro. Cada una incluye una línea de contexto que
explicita sobre qué base se calcula.</td></tr>
<tr><td><strong>Filtros</strong></td>
<td>Cinco filtros de aplicación cruzada y simultánea: formato, género principal, idioma original,
año de estreno desde y calificación mínima. Un botón de limpieza restablece el estado inicial.</td></tr>
<tr><td><strong>Navegación</strong></td>
<td>Cuatro pestañas temáticas: Visión general, Calidad vs. popularidad, Mercados y tendencia, y
Desempeño financiero. Los filtros persisten al cambiar de pestaña.</td></tr>
<tr><td><strong>Interacción</strong></td>
<td>Información contextual al pasar el cursor sobre cualquier marca, zoom y desplazamiento en los
gráficos de dispersión, recálculo instantáneo de todas las vistas y mensajes explícitos cuando una
combinación de filtros no arroja datos suficientes.</td></tr>
<tr><td><strong>Transparencia metodológica</strong></td>
<td>Cada gráfico declara su criterio de representación, y el pie del tablero advierte sobre el
diseño muestral y el tratamiento de valores ausentes.</td></tr>
</tbody>
</table>

<h3>10.3 Coherencia con el informe</h3>
<p>El dashboard comparte paleta, tipografía, convención numérica y criterios de representación con
las figuras de este informe. Un lector que pase del documento al tablero reconoce inmediatamente
los mismos gráficos, ahora explorables. Esa continuidad es deliberada: reduce el costo de
aprendizaje y refuerza la confianza en que ambos productos describen la misma realidad.</p>
</section>

<!-- ============ 11. EVALUACIÓN CRÍTICA ============ -->
<section>
<h2><span class="num">11</span>Evaluación crítica de la solución</h2>

<h3>11.1 Fortalezas</h3>
<ul>
<li><strong>Hallazgo central robusto.</strong> La independencia entre popularidad y calidad se
sostiene sobre {n(m['evaluables'])} títulos con respaldo de votos suficiente, y se mantiene al
segmentar por formato, género y año.</li>
<li><strong>Trazabilidad completa.</strong> Todo el proceso es reproducible desde los archivos
originales mediante cuatro scripts. Las cifras del informe se generan desde un archivo de métricas
calculado, no se transcriben manualmente.</li>
<li><strong>Tratamiento explícito de la calidad de datos.</strong> Se detectaron y documentaron
ocho problemas relevantes —incluido el diseño muestral, que invalida un tipo completo de
conclusión— antes de analizar.</li>
<li><strong>Coherencia visual verificable.</strong> Un único sistema de diseño gobierna informe,
figuras y dashboard.</li>
<li><strong>Accesibilidad de la herramienta.</strong> El dashboard funciona sin licencias,
instalación ni conexión.</li>
</ul>

<h3>11.2 Limitaciones</h3>
<div class="destacado naranja">
<span class="et">Limitación principal</span>
<p><strong>No se dispone de datos de usuarios.</strong> Las fuentes entregadas describen el
catálogo, no el comportamiento individual: no hay reproducciones, suscripciones, dispositivos,
sesiones ni cancelaciones. En consecuencia, este proyecto <strong>no puede medir retención ni
engagement reales</strong>. La variable <code>popularity</code> se emplea como aproximación de
atención, y la relación entre esa aproximación y la retención efectiva queda sin verificar.</p>
</div>

<ul>
<li><strong>El diseño muestral impide analizar volumen.</strong> Con {n(m['titulos_por_anio_formato'])}
títulos fijos por año, toda conclusión sobre crecimiento del catálogo sería un artefacto del
muestreo.</li>
<li><strong>Cobertura financiera parcial y probablemente sesgada.</strong> Solo
{d(m['peliculas_con_finanzas_pct'], 1)}% de las películas informa presupuesto e ingresos, y es
plausible que las que lo hacen sean las de mayor circulación comercial.</li>
<li><strong>Calificaciones de origen externo.</strong> Provienen de una comunidad de votantes que
no equivale a la base de suscriptores de la plataforma, y que tiende a sobrerrepresentar perfiles
cinéfilos.</li>
<li><strong>El umbral de evaluabilidad no afecta por igual a ambos formatos.</strong> El
{d(m['pct_supera_umbral_peliculas'], 1)}% de las películas calificadas alcanza los
{m['umbral_votos']} votos exigidos, frente a solo el {d(m['pct_supera_umbral_series'], 1)}% de las
series. En consecuencia, el universo evaluable queda compuesto en un
{d(m['pct_peliculas_en_evaluables'], 1)}% por películas, pese a que el catálogo se reparte casi
por mitades. Los recuentos absolutos por cuadrante están, por tanto, dominados por el formato
película, aunque la segmentación relativa dentro de cada formato sigue siendo válida.</li>
<li><strong>Sesgo de maduración de votos.</strong> Los títulos recientes acumulan menos votos, lo
que hace que el último año no sea comparable con los anteriores.</li>
<li><strong>Inconsistencias de unidad en los datos financieros.</strong> Algunos registros
declaran presupuestos de pocos cientos de dólares junto a ingresos millonarios, lo que sugiere
que la fuente mezcla unidades. Se mitiga usando medianas en lugar de promedios, pero los casos
de retorno extremo deben tomarse con reserva.</li>
<li><strong>Taxonomías de origen no del todo conciliables.</strong> Pese a la armonización, tres
géneros de películas no tienen equivalente en la clasificación de series.</li>
<li><strong>El dashboard usa el género principal.</strong> Para mantener el filtrado cruzado
eficiente se emplea un solo género por título, mientras que el informe analiza todos los géneros
asignados.</li>
</ul>

<h3>11.3 Oportunidades de mejora</h3>
<ol>
<li><strong>Incorporar datos de reproducción y suscripción</strong> para reemplazar la
aproximación de popularidad por métricas reales de consumo y medir el efecto sobre la
retención.</li>
<li><strong>Validar experimentalmente el hallazgo central</strong> mediante una prueba A/B que
promueva títulos del cuadrante de calidad sin visibilidad y mida su impacto en satisfacción y
renovación.</li>
<li><strong>Enriquecer con datos de costo de licenciamiento</strong> para pasar de un análisis de
calidad a uno de valor por unidad invertida.</li>
<li><strong>Automatizar la actualización</strong> del pipeline para que el tablero refleje el
catálogo vigente sin intervención manual.</li>
<li><strong>Segmentar por perfil de audiencia</strong>, dado que la calificación promedio oculta
diferencias relevantes entre públicos.</li>
</ol>

<h3>11.4 Justificación de las decisiones de diseño adoptadas</h3>
<table>
<thead><tr><th style="width:32%">Decisión</th><th>Justificación</th></tr></thead>
<tbody>
<tr><td>Excluir títulos sin votos de todo promedio</td>
<td>Tratar la ausencia de votos como calificación cero habría hundido artificialmente el promedio
de las series, donde afecta a una parte sustantiva de los registros.</td></tr>
<tr><td>Exigir {m['umbral_votos']} votos para el análisis de correlación</td>
<td>Una calificación sostenida por dos o tres votos es ruido. El umbral reduce el universo pero
entrega una base confiable.</td></tr>
<tr><td>Usar cuadrantes sobre medianas y no sobre promedios</td>
<td>Ambas variables tienen distribuciones muy asimétricas; la mediana divide el universo en partes
comparables, el promedio no.</td></tr>
<tr><td>Calcular medianas y correlaciones <strong>dentro de cada formato</strong></td>
<td>El índice de popularidad tiene escalas incompatibles entre películas y series. Agregarlos
convertía el corte en un separador de formato y producía un cuadrante sin una sola serie. La
corrección reasignó de cuadrante a un tercio de los títulos y confirmó que la correlación es aún
más débil de lo estimado inicialmente.</td></tr>
<tr><td>Escala logarítmica en popularidad</td>
<td>Sin ella, el 99% de los títulos resulta ilegible. Se declara explícitamente en cada eje para
no inducir a error.</td></tr>
<tr><td>Conservar la línea base en cero en los rankings</td>
<td>Truncar el eje habría magnificado visualmente diferencias de décimas de punto.</td></tr>
<tr><td>Dashboard en HTML autocontenido</td>
<td>Es el único formato que cualquier destinatario puede abrir sin licencia, instalación ni
servidor.</td></tr>
<tr><td>Armonizar taxonomías antes de comparar</td>
<td>Sin armonizar, la comparación por género producía categorías artificialmente exclusivas de un
formato y conclusiones falsas.</td></tr>
</tbody>
</table>
</section>

<!-- ============ 12. PROPUESTAS COMERCIALES ============ -->
<section>
<h2><span class="num">12</span>Propuestas comerciales: de hallazgos a decisiones</h2>

<p>Los hallazgos de la sección 7 no son solo diagnóstico: definen tres palancas concretas de
adquisición y retención que StreamView Analytics puede activar con el catálogo que ya posee, sin
comprometer presupuesto de licenciamiento. Las tres se apoyan exclusivamente en variables de
catálogo y recepción —popularidad, calificación, votos, género, formato y año—, sin asumir ni
interpretar datos financieros que este proyecto no posee.</p>

<h3>12.1 Programa Joyas Ocultas</h3>

<div class="destacado verde">
<span class="et">Estrategia prioritaria</span>
<p>Activar en el descubrimiento los <strong>{n(m['cuad_calidad_sin_visibilidad'])} títulos</strong>
que ya están en el catálogo, ya calificados por encima de la mediana de su propio formato, pero
con popularidad por debajo de ella. Es la única de las tres propuestas cuyo costo de adquisición
de contenido es cero: el activo ya está pagado.</p>
</div>

{figura('11_joyas_ocultas', 12, 'Caracterización del cuadrante «calidad sin visibilidad»: dónde se concentra por género (izquierda) y cuánto mejor califica la audiencia a estos títulos frente al resto del catálogo evaluable, por formato (derecha).')}

<p><strong>Hallazgo que la respalda.</strong> El segmento no es un accidente estadístico marginal:
representa el {d(m['pct_calidad_sin_visibilidad'], 1)}% del catálogo evaluable
({n(m['cuad_calidad_sin_visibilidad_peliculas'])} películas y
{n(m['cuad_calidad_sin_visibilidad_series'])} series) y su calidad promedio supera claramente al
resto del catálogo evaluable: {d(m['joyas_calificacion_media_peliculas'])} frente a
{d(m['resto_calificacion_media_peliculas'])} en películas, y {d(m['joyas_calificacion_media_series'])}
frente a {d(m['resto_calificacion_media_series'])} en series. Se concentra especialmente en
{m['joyas_top_generos'][0]['genero']} ({n(m['joyas_top_generos'][0]['titulos'])} títulos),
{m['joyas_top_generos'][1]['genero']} ({n(m['joyas_top_generos'][1]['titulos'])}) y
{m['joyas_top_generos'][2]['genero']} ({n(m['joyas_top_generos'][2]['titulos'])}), y en mercados
como el {m['joyas_top_idiomas'][1]['idioma'].lower()} y el
{m['joyas_top_idiomas'][2]['idioma'].lower()}, que en la sección 7.8 ya aparecían como
sistemáticamente mejor evaluados que el idioma dominante del catálogo.</p>

<table>
<thead><tr><th>Título de ejemplo</th><th>Formato</th><th class="num">Año</th>
<th>Género</th><th>Idioma</th><th class="num">Calificación</th></tr></thead>
<tbody>
{"".join(f"<tr><td>{e['title']}</td><td>{e['tipo']}</td><td class='num'>{e['anio']}</td>"
        f"<td>{e['genero']}</td><td>{e['idioma']}</td>"
        f"<td class='num'>{d(e['calificacion'])}</td></tr>" for e in m['joyas_ejemplos'])}
</tbody>
</table>
<p style="font-size:9pt; color:#6B6B6B; margin-top:-2mm">Un título por género, ordenados por
calificación dentro del segmento «calidad sin visibilidad». Ilustran el tipo de contenido que el
programa expondría, no una selección editorial curada a mano.</p>

<h4>Mecanismo de atracción</h4>
<p>Marketing editorial de nicho —"lo mejor calificado que nadie está viendo"— dirigido a audiencias
que valoran calidad sobre tendencia. Es un ángulo de adquisición de bajo costo que no compite por
el mismo público masivo que persiguen las campañas basadas en éxitos de taquilla, y que se apoya en
evidencia verificable (la calificación real de la audiencia) en lugar de en presupuesto de
marketing.</p>

<h4>Mecanismo de retención</h4>
<p>Una fila fija y renovada mensualmente en la pantalla de inicio ("Alta calificación, poco
vistas"), personalizada por el género favorito de cada usuario. Ataca directamente la
<strong>sensación de catálogo agotado</strong> —un antecedente habitual de cancelación— sin
requerir una sola incorporación de contenido nuevo.</p>

<h4>KPI sugerido</h4>
<p><strong>% de usuarios activos que reproducen al menos un título del segmento «calidad sin
visibilidad» por mes</strong>, junto con la calificación implícita de esas reproducciones (aceptada
vs. abandonada) frente al resto del consumo del usuario. Un aumento sostenido de este porcentaje
mide, con datos ya disponibles en la plataforma, si la exposición está funcionando.</p>

<h3>12.2 Radar de Momentum por Género</h3>

{figura('12_momentum_generos', 13, 'Variación porcentual de la popularidad mediana por género entre la ventana 2022-2024 y la ventana 2010-2018. En rojo, los tres géneros con mayor variación positiva.')}

<div class="destacado naranja">
<span class="et">Precisión metodológica</span>
<p>La correlación entre año de estreno y popularidad es prácticamente nula
({d(m['correlacion_anio_popularidad_peliculas'])} en películas,
{d(m['correlacion_anio_popularidad_series'])} en series): <strong>no existe una tendencia agregada
de popularidad creciente hacia 2024</strong>. Lo que sí es real y verificable es una
<strong>rotación de interés entre géneros</strong>: algunos ganan terreno relativo, otros lo
pierden. Esta propuesta se apoya en esa rotación, no en un crecimiento general que los datos no
sostienen.</p>
</div>

<p><strong>Hallazgo que la respalda.</strong> Entre ambas ventanas, {m['momentum_top_generos'][0]['genero']}
(+{d(m['momentum_top_generos'][0]['variacion_pct'], 1)}%), {m['momentum_top_generos'][1]['genero']}
(+{d(m['momentum_top_generos'][1]['variacion_pct'], 1)}%) y {m['momentum_top_generos'][2]['genero']}
(+{d(m['momentum_top_generos'][2]['variacion_pct'], 1)}%) muestran el mayor aumento relativo de
popularidad mediana, mientras que {m['momentum_bottom_generos'][2]['genero']}
({d(m['momentum_bottom_generos'][2]['variacion_pct'], 1)}%) y
{m['momentum_bottom_generos'][1]['genero']} ({d(m['momentum_bottom_generos'][1]['variacion_pct'], 1)}%)
retroceden.</p>

<h4>Mecanismo de atracción</h4>
<p>Campañas de adquisición segmentadas que usan el ranking de momentum como brief creativo: se
pauta sobre los géneros en alza relativa, no sobre el catálogo genérico. El indicador se recalcula
periódicamente y redefine qué género protagoniza la campaña del período siguiente.</p>

<h4>Mecanismo de retención</h4>
<p>El onboarding registra el género que motivó la conversión del usuario adquirido y prioriza ese
género en las primeras sesiones de recomendación, evitando la disonancia entre la promesa de la
campaña y la primera experiencia dentro de la plataforma.</p>

<h4>KPI sugerido</h4>
<p><strong>Variación trimestral de la popularidad mediana por género</strong> (gatillo de campaña),
junto con la <strong>tasa de finalización de la primera sesión</strong> dentro del género que
motivó la adquisición.</p>

<h3>12.3 Series como ancla de suscripción</h3>

<p><strong>Hallazgo que la respalda.</strong> Como se documentó en la sección 7.6, las series
superan a las películas en calificación los {m['anios_series_sobre_peliculas']} años analizados sin
excepción, con una brecha que <strong>aumenta</strong> a {d(m['brecha_series_peliculas_controlada'])}
puntos al controlar por número de votos. No es un artefacto de muestra: es una ventaja estructural
del formato episódico.</p>

<h4>Mecanismo de atracción</h4>
<p>Usar series del segmento de alta calificación como gancho de prueba —primer episodio gratuito—
en campañas de adquisición, capitalizando que el formato episódico recibe mejor recepción promedio
que el cine.</p>

<h4>Mecanismo de retención</h4>
<p>El formato episódico retiene por diseño: prioriza en el algoritmo de "continuar viendo" las
series de alta calificación sobre las de solo alta popularidad, apostando por construir el hábito
de retorno semanal en lugar del consumo de un evento único.</p>

<h4>KPI sugerido</h4>
<p><strong>Tasa de retorno semanal (WAU)</strong> segmentada según si el usuario inició con una
serie o con una película, y <strong>número de episodios completados</strong> en los primeros siete
días desde el registro.</p>

<h3>12.4 Síntesis</h3>
<table>
<thead><tr><th style="width:26%">Propuesta</th><th style="width:30%">Palanca principal</th>
<th>KPI</th></tr></thead>
<tbody>
<tr><td><strong>Joyas Ocultas</strong></td><td>Retención por descubrimiento, costo de contenido cero</td>
<td>% de usuarios que consumen el segmento al mes</td></tr>
<tr><td><strong>Momentum por Género</strong></td><td>Adquisición dirigida por rotación de interés</td>
<td>Variación trimestral de popularidad por género</td></tr>
<tr><td><strong>Series como Ancla</strong></td><td>Retención por hábito de consumo episódico</td>
<td>Retorno semanal y episodios completados en 7 días</td></tr>
</tbody>
</table>
</section>

<!-- ============ 13. CONCLUSIONES ============ -->
<section>
<h2><span class="num">13</span>Conclusiones y recomendaciones</h2>

<h3>12.1 Conclusiones</h3>
<ol>
<li><strong>Popularidad y calidad percibida son dimensiones independientes</strong>
(r = {d(m['correlacion_pop_calidad_peliculas'])} en películas y
{d(m['correlacion_pop_calidad_series'])} en series, sobre {n(m['evaluables'])} títulos evaluables).
Cualquier gestión del catálogo basada en una sola métrica optimiza un objetivo a costa del otro.</li>
<li><strong>El catálogo contiene {n(m['cuad_calidad_sin_visibilidad'])} títulos de alta calidad y
baja exposición</strong>: contenido ya adquirido cuyo valor no se está capturando.</li>
<li><strong>La ventaja de las series sobre las películas es estructural</strong>: se sostiene los
{m['anios_series_sobre_peliculas']} años analizados con una brecha media de
{d(m['brecha_series_peliculas'])} puntos.</li>
<li><strong>La concentración del catálogo en contenido en inglés no se corresponde con su
valoración relativa</strong>: {d(m['ingles_pct_catalogo'], 1)}% del catálogo, posición
{m['ingles_posicion']} de {m['mercados_analizados']} en calidad percibida.</li>
<li><strong>Los géneros mejor evaluados son los menos representados</strong>, lo que define una
oportunidad de crecimiento concreta y acotada.</li>
<li><strong>El riesgo comercial se concentra en el tramo medio de inversión</strong>
({d(peor['pct_rentables'], 1)}% de éxito frente a {d(mejor['pct_rentables'], 1)}% en el tramo muy
alto), no en las apuestas grandes.</li>
</ol>

<h3>12.2 Recomendaciones</h3>

<div class="destacado verde">
<span class="et">Recomendación 1 · Prioridad inmediata · Costo marginal cero</span>
<p><strong>Activar el contenido de calidad sin visibilidad.</strong> Incorporar los
{n(m['cuad_calidad_sin_visibilidad'])} títulos del cuadrante de alta calificación y baja atención
a las superficies de descubrimiento —carruseles de recomendación, colecciones temáticas
curadas—. Es contenido ya pagado: la intervención no requiere presupuesto de adquisición.
<br><em>Indicador de seguimiento:</em> evolución de la popularidad mediana de ese segmento y
variación en la satisfacción declarada.</p>
</div>

<div class="destacado">
<span class="et">Recomendación 2 · Adquisición</span>
<p><strong>Rebalancear la cartera hacia géneros y mercados de alto rendimiento y baja
presencia.</strong> Priorizar los géneros identificados en la sección 7.5 —encabezados por
{go[0]['genero'].lower()} y {go[1]['genero'].lower()}— y los mercados de la sección 7.8, liderados
por el contenido en {mt[0]['idioma'].lower()} y {mt[1]['idioma'].lower()}. Son segmentos con
valoración sobre la mediana y oferta por debajo de ella.</p>
</div>

<div class="destacado">
<span class="et">Recomendación 3 · Producción</span>
<p><strong>Reforzar la apuesta por el formato serie.</strong> La ventaja de
{d(m['brecha_series_peliculas'])} puntos sostenida durante {m['anios_series_sobre_peliculas']} años
consecutivos justifica desplazar capacidad de producción propia hacia formatos episódicos, que
además favorecen la permanencia del suscriptor entre períodos de facturación.</p>
</div>

<div class="destacado naranja">
<span class="et">Recomendación 4 · Inversión</span>
<p><strong>Revisar la política de inversión en el tramo medio.</strong> El segmento de
{peor['escala'].lower().replace('(', '').replace(')', '')} concentra {n(peor['peliculas'])}
películas con la menor tasa de éxito del catálogo ({d(peor['pct_rentables'], 1)}%). La evidencia
sugiere evaluar su polarización: o bien contener el presupuesto en el tramo bajo, o bien
consolidar recursos en apuestas de mayor escala.</p>
</div>

<div class="destacado">
<span class="et">Recomendación 5 · Gobierno del dato</span>
<p><strong>Incorporar datos de comportamiento de usuario.</strong> Todas las recomendaciones
anteriores se sostienen sobre una aproximación de atención, no sobre consumo real. Integrar
reproducciones, suscripciones y cancelaciones permitiría medir el impacto de estas decisiones
sobre la retención, que es el objetivo último de la organización.</p>
</div>

<h3>12.3 Cierre</h3>
<p>El análisis no identifica un déficit de catálogo. Identifica una <strong>brecha entre el valor
que StreamView Analytics ya tiene comprado y el valor que efectivamente pone frente a su
audiencia</strong>. Cerrar esa brecha es, de todas las palancas examinadas en este informe, la de
menor costo y mayor retorno esperado.</p>

<footer>
Informe ejecutivo elaborado bajo metodología CRISP-DM · Asignatura ADY1104 Visualización de Datos ·
Evaluaciones EP1 y EP2.<br>
Fuente: catálogo de contenidos {m['anio_min']}-{m['anio_max']} · muestra estratificada de
{n(m['titulos_por_anio_formato'])} títulos por año y formato · {n(m['titulos_total'])} registros analizados.<br>
Reproducible mediante <code>src/data_prep.py</code>, <code>src/metricas.py</code>,
<code>src/eda_visualizaciones.py</code>, <code>src/dashboard_build.py</code> e
<code>src/informe_build.py</code>.
</footer>
</section>

</div>
</body></html>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = json.loads((PROC / "metricas.json").read_text(encoding="utf-8"))
    html = construir(m)
    salida = OUT / "informe_ejecutivo.html"
    salida.write_text(html, encoding="utf-8")
    print(f"{salida}  ({salida.stat().st_size/1024/1024:.1f} MB)")
    print("Para obtener el PDF: abrir en el navegador y usar Ctrl+P > Guardar como PDF")


if __name__ == "__main__":
    main()
