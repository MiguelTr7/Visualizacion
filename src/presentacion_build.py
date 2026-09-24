# -*- coding: utf-8 -*-
"""
StreamView Analytics - Generador de la presentacion ejecutiva

Compone el deck de defensa en formato 16:9, listo para exportar a PDF desde
el navegador. Toma las cifras desde data/processed/metricas.json y las
figuras desde images/, de modo que la presentacion nunca se desincroniza del
informe.

Uso:  python src/presentacion_build.py
"""
from pathlib import Path
import base64
import json

PROC = Path("data/processed")
IMG = Path("images")
OUT = Path("reports/informe_ejecutivo")


def n(x):
    return f"{int(round(float(x))):,}".replace(",", ".")


def d(x, c=2):
    return f"{float(x):.{c}f}".replace(".", ",")


def img(nombre):
    b64 = base64.b64encode((IMG / f"{nombre}.png").read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


CSS = """
@page { size: 330mm 186mm; margin: 0; }
:root{
  --rojo:#E50914; --azul:#0072B2; --verde:#009E73; --naranja:#E69F00;
  --carbon:#1A1818; --gris:#6B6B6B; --linea:#E2DEDE; --fondo:#FAF9F8;
}
*{box-sizing:border-box}
body{margin:0; background:#3A3A3A; color:var(--carbon);
  font-family:"Segoe UI","Helvetica Neue",Arial,sans-serif;}

.diapo{
  width:330mm; height:186mm; background:#fff; margin:0 auto 6mm;
  padding:14mm 18mm 12mm; position:relative; overflow:hidden;
  page-break-after:always; display:flex; flex-direction:column;
}
.diapo:last-child{page-break-after:auto}

.et{font-size:9.5pt; text-transform:uppercase; letter-spacing:1.6px;
  color:var(--rojo); font-weight:700; margin-bottom:3mm}
.diapo h2{font-size:26pt; line-height:1.16; margin:0 0 4mm; letter-spacing:-.6px;
  max-width:88%}
.diapo h3{font-size:14pt; margin:0 0 3mm; color:var(--gris); font-weight:500}
.diapo p{font-size:12.5pt; line-height:1.55; margin:0 0 3mm; max-width:170mm}
.num-diapo{position:absolute; right:12mm; bottom:7mm; font-size:9pt;
  color:#B8B4B4; font-variant-numeric:tabular-nums}
.marca{position:absolute; left:18mm; bottom:7mm; font-size:9pt; color:#B8B4B4;
  letter-spacing:.4px}
.marca b{color:var(--rojo)}
.cuerpo{flex:1; display:flex; gap:9mm; min-height:0}
.col{flex:1; min-width:0; display:flex; flex-direction:column; justify-content:center}
.fig{flex:1; min-height:0; display:flex; align-items:center; justify-content:center}
.fig img{max-width:100%; max-height:100%; object-fit:contain}

/* ---- portada ---- */
.portada{background:var(--carbon); color:#fff; justify-content:space-between}
.portada h1{font-size:46pt; line-height:1.06; margin:0 0 5mm; letter-spacing:-1.4px}
.portada .bajada{font-size:17pt; color:#C9C5C5; font-weight:300; line-height:1.4;
  max-width:150mm}
.portada .marca-top{font-size:14pt; font-weight:700; letter-spacing:.6px}
.portada .marca-top span{color:var(--rojo)}
.portada .pie{font-size:10.5pt; color:#8E8A8A; display:flex; gap:12mm;
  border-top:1px solid #3A3636; padding-top:4mm}
.portada .pie b{color:#fff; font-weight:600; display:block; font-size:9pt;
  text-transform:uppercase; letter-spacing:1px; margin-bottom:1mm}

/* ---- cifras ---- */
.cifras{display:grid; grid-template-columns:repeat(4,1fr); gap:5mm; margin:4mm 0}
.cifra{border-top:4px solid var(--rojo); padding:4mm 0 0}
.cifra .v{font-size:32pt; font-weight:700; line-height:1;
  font-variant-numeric:tabular-nums; letter-spacing:-1px}
.cifra .e{font-size:10pt; color:var(--gris); margin-top:2.5mm; line-height:1.35}
.cifra.a{border-top-color:var(--azul)} .cifra.v2{border-top-color:var(--verde)}
.cifra.n{border-top-color:var(--naranja)}

.gigante{font-size:86pt; font-weight:800; line-height:.92; letter-spacing:-3px;
  color:var(--rojo); font-variant-numeric:tabular-nums}
.gigante-pie{font-size:14pt; color:var(--gris); margin-top:4mm; line-height:1.45}

/* ---- listas ---- */
.puntos{list-style:none; padding:0; margin:2mm 0}
.puntos li{font-size:12.5pt; line-height:1.5; padding-left:9mm; margin-bottom:4mm;
  position:relative}
.puntos li::before{content:""; position:absolute; left:0; top:2.4mm;
  width:4mm; height:4mm; background:var(--rojo)}
.puntos li b{display:block; font-size:13pt; margin-bottom:.8mm}

.cuadros{display:grid; grid-template-columns:repeat(2,1fr); gap:5mm; margin-top:3mm}
.cuadro{border:1px solid var(--linea); border-left:4px solid var(--gris);
  padding:4mm 5mm; background:var(--fondo)}
.cuadro .t{font-size:11.5pt; font-weight:700; margin-bottom:1.5mm}
.cuadro .c{font-size:22pt; font-weight:700; font-variant-numeric:tabular-nums;
  line-height:1; margin-bottom:2mm}
.cuadro .x{font-size:10pt; color:var(--gris); line-height:1.4}
.cuadro.verde{border-left-color:var(--verde)} .cuadro.verde .c{color:var(--verde)}
.cuadro.rojo{border-left-color:var(--rojo)} .cuadro.rojo .c{color:var(--rojo)}
.cuadro.naranja{border-left-color:var(--naranja)} .cuadro.naranja .c{color:var(--naranja)}

table{width:100%; border-collapse:collapse; font-size:11pt}
th{background:var(--carbon); color:#fff; text-align:left; padding:2.5mm 3mm;
  font-size:9.5pt; text-transform:uppercase; letter-spacing:.5px}
td{padding:2.4mm 3mm; border-bottom:1px solid var(--linea)}
td.num{text-align:right; font-variant-numeric:tabular-nums}

.franja{background:var(--carbon); color:#fff; margin:0 -18mm; padding:6mm 18mm}
.franja p{font-size:15pt; margin:0; max-width:none; line-height:1.45}
.franja b{color:#fff}

.cierre{background:var(--carbon); color:#fff; justify-content:center; text-align:left}
.cierre h2{font-size:34pt; color:#fff; max-width:200mm; line-height:1.18}
.cierre p{font-size:15pt; color:#C9C5C5; max-width:180mm}

@media screen{
  body{padding:8mm 0; overflow-x:hidden}
  .diapo{box-shadow:0 3px 20px rgba(0,0,0,.35)}
  .aviso{max-width:330mm; margin:0 auto 6mm; background:#FFF6D6; border:1px solid #E6C84A;
    padding:3mm 6mm; font-size:10pt; border-radius:4px}
  /* Las diapositivas tienen ancho fijo porque deben imprimirse en 16:9.
     En pantallas mas angostas se escalan en bloque para que nunca aparezca
     desplazamiento horizontal. */
  #pila{transform-origin:top center; margin:0 auto}
}
@media print{
  .aviso{display:none} body{background:#fff; padding:0}
  .diapo{box-shadow:none; margin:0}
  #pila{transform:none !important; height:auto !important}
}
"""


def construir(m):
    gt, gb, go = m["generos_top"], m["generos_bajos"], m["generos_oportunidad"]
    mt = m["mercados_top"]
    esc = m["rentabilidad_por_escala"]
    peor = min(esc, key=lambda e: e["pct_rentables"])
    mejor = max(esc, key=lambda e: e["pct_rentables"])

    filas_op = "".join(
        f"<tr><td>{g['genero']}</td><td class='num'>{n(g['titulos'])}</td>"
        f"<td class='num'>{d(g['calificacion'])}</td></tr>" for g in go[:5])
    filas_mk = "".join(
        f"<tr><td>{x['idioma']}</td><td class='num'>{n(x['titulos'])}</td>"
        f"<td class='num'>{d(x['calificacion'])}</td></tr>" for x in mt)

    def diapo(num, contenido, clase=""):
        return (f'<div class="diapo {clase}">{contenido}'
                f'<div class="marca">Stream<b>View</b> Analytics</div>'
                f'<div class="num-diapo">{num}</div></div>')

    s = []

    # 1 ---------------------------------------------------------------
    s.append(f"""<div class="diapo portada">
  <div class="marca-top">StreamView <span>Analytics</span></div>
  <div>
    <h1>Inteligencia<br>de Catálogo</h1>
    <p class="bajada">Qué mira la audiencia, qué valora,<br>y por qué no son lo mismo</p>
  </div>
  <div class="pie">
    <div><b>Metodología</b>CRISP-DM · Fases 1 a 6</div>
    <div><b>Alcance</b>{n(m['titulos_total'])} títulos · {m['anio_min']}–{m['anio_max']}</div>
    <div><b>Destinatario</b>Dirección de Contenidos</div>
    <div><b>Asignatura</b>ADY1104 Visualización de Datos</div>
  </div>
  <div class="num-diapo" style="color:#5A5555">1</div>
</div>""")

    # 2 ---------------------------------------------------------------
    s.append(diapo(2, f"""
  <div class="et">El encargo</div>
  <h2>La Dirección de Contenidos decide qué comprar, qué producir<br>y qué promover. Hoy lo hace sin evidencia integrada.</h2>
  <div class="cuerpo">
    <div class="col">
      <ul class="puntos">
        <li><b>El problema</b>No existe una lectura que distinga el contenido que genera
            tráfico del que genera satisfacción.</li>
        <li><b>Por qué importa</b>El tráfico sostiene el consumo del mes; la satisfacción
            sostiene la renovación de la suscripción.</li>
        <li><b>La pregunta</b>¿Qué concentra la atención, qué concentra la valoración,
            y qué decisiones se desprenden de la diferencia?</li>
      </ul>
    </div>
    <div class="col">
      <table>
        <thead><tr><th>Audiencia</th><th>Qué decide</th></tr></thead>
        <tbody>
          <tr><td><b>Dirección de Contenidos</b><br><span style="color:#6B6B6B">principal</span></td>
              <td>Qué adquirir, producir y renovar</td></tr>
          <tr><td><b>Comité ejecutivo</b></td><td>Asignación de presupuesto</td></tr>
          <tr><td><b>Producto y curatoría</b></td><td>Qué promover y cómo ordenar el descubrimiento</td></tr>
        </tbody>
      </table>
      <p style="margin-top:4mm; font-size:11.5pt; color:#6B6B6B">El propósito no es describir
      el catálogo: es cambiar una decisión.</p>
    </div>
  </div>"""))

    # 3 ---------------------------------------------------------------
    s.append(diapo(3, f"""
  <div class="et">Metodología</div>
  <h2>CRISP-DM: la pregunta de negocio primero, los datos después</h2>
  <div class="cuerpo"><div class="col">
    <table>
      <thead><tr><th style="width:26%">Fase</th><th>Qué se hizo</th></tr></thead>
      <tbody>
        <tr><td><b>1 · Negocio</b></td><td>Problema, audiencia y propósito comunicacional</td></tr>
        <tr><td><b>2 · Datos</b></td><td>Perfilado y diagnóstico de calidad de ambas fuentes</td></tr>
        <tr><td><b>3 · Preparación</b></td><td>Limpieza, armonización de taxonomías e integración</td></tr>
        <tr><td><b>4 · Análisis</b></td><td>Exploración visual y segmentación por cuadrantes</td></tr>
        <tr><td><b>5 · Evaluación</b></td><td>Revisión crítica de la validez de los hallazgos</td></tr>
        <tr><td><b>6 · Despliegue</b></td><td>Dashboard, narrativa visual e informe ejecutivo</td></tr>
      </tbody>
    </table>
  </div></div>
  <div class="franja"><p><b>El método es iterativo y lo usamos así:</b> la fase 4 nos obligó a
  volver a la fase 3 al descubrir que películas y series usaban taxonomías de género distintas.</p></div>"""))

    # 4 ---------------------------------------------------------------
    s.append(diapo(4, f"""
  <div class="et">Comprensión de los datos</div>
  <h2>Antes de analizar: qué nos permiten y qué no nos permiten decir estos datos</h2>
  <div class="cuerpo">
    <div class="col">
      <div class="gigante">{n(m['titulos_por_anio_formato'])}</div>
      <p class="gigante-pie">títulos <b>exactos</b> por cada año, en ambas fuentes.<br>
      No es el catálogo: es una <b>muestra estratificada</b>.</p>
      <p style="margin-top:5mm; font-size:12pt"><b>Consecuencia:</b> el volumen anual es constante
      por diseño. Este análisis no puede sostener ninguna conclusión sobre crecimiento del catálogo.</p>
    </div>
    <div class="col">
      <table>
        <thead><tr><th>Hallazgo de calidad</th><th>Tratamiento</th></tr></thead>
        <tbody>
          <tr><td>{n(m['sin_calificar'])} títulos sin votos figuraban con calificación 0,0</td>
              <td>Convertidos a dato ausente</td></tr>
          <tr><td>{d(m['budget_ceros_pct'], 1)}% de presupuestos en cero</td>
              <td>Tratados como faltantes</td></tr>
          <tr><td><code>rating</code> idéntica a <code>vote_average</code></td><td>Eliminada</td></tr>
          <tr><td><code>duration</code> nula o constante</td><td>Eliminada</td></tr>
          <tr><td>Taxonomías de género divergentes</td><td>Armonizadas</td></tr>
          <tr><td>{m['series_id_duplicados']} identificadores duplicados</td><td>Deduplicados</td></tr>
        </tbody>
      </table>
    </div>
  </div>"""))

    # 5 ---------------------------------------------------------------
    s.append(diapo(5, f"""
  <div class="et">Contexto · 1 de 2</div>
  <h2>El catálogo está concentrado en géneros masivos</h2>
  <div class="cuerpo"><div class="fig"><img src="{img('01_composicion_generos')}" alt=""></div></div>"""))

    # 6 ---------------------------------------------------------------
    s.append(diapo(6, f"""
  <div class="et">Contexto · 2 de 2</div>
  <h2>Y su calidad mejora año a año. No hay un problema evidente.</h2>
  <div class="cuerpo"><div class="fig"><img src="{img('06_evolucion_temporal')}" alt=""></div></div>"""))

    # 7 ---------------------------------------------------------------
    s.append(diapo(7, f"""
  <div class="et">Narrativa visual (Data Storytelling) · Tensión</div>
  <h2>Pero la atención no se reparte: se concentra en una minoría</h2>
  <div class="cuerpo">
    <div class="col" style="flex:0 0 62mm">
      <div class="gigante">{n(m['ratio_max_mediana'])}×</div>
      <p class="gigante-pie">El título más popular supera<br>{n(m['ratio_max_mediana'])} veces al título mediano.</p>
      <p style="font-size:11.5pt; margin-top:4mm">Solo <b>{n(m['titulos_sobre_p99'])} títulos</b>
      superan el percentil 99.<br><br>La mayoría del catálogo vive con exposición marginal.</p>
    </div>
    <div class="fig"><img src="{img('03_distribucion_popularidad')}" alt=""></div>
  </div>"""))

    # 8 ---------------------------------------------------------------
    s.append(diapo(8, f"""
  <div class="et">El giro · Hallazgo central</div>
  <h2>Lo más popular no es lo mejor evaluado</h2>
  <div class="cuerpo"><div class="fig"><img src="{img('04_popularidad_vs_calidad')}" alt=""></div></div>
  <div class="franja"><p>Correlación de <b>{d(m['correlacion_pop_calidad_peliculas'])}</b> en películas y
  <b>{d(m['correlacion_pop_calidad_series'])}</b> en series. Saber cuán popular es un título
  <b>no permite anticipar</b> cómo será calificado.</p></div>"""))

    # 9 ---------------------------------------------------------------
    s.append(diapo(9, f"""
  <div class="et">Consecuencia operativa</div>
  <h2>Ese hallazgo divide el catálogo en cuatro decisiones distintas</h2>
  <div class="cuerpo"><div class="col">
    <div class="cuadros">
      <div class="cuadro verde"><div class="t">Calidad sin visibilidad</div>
        <div class="c">{n(m['cuad_calidad_sin_visibilidad'])}</div>
        <div class="x"><b>Promover.</b> Máxima prioridad: contenido ya pagado que la audiencia
        valora, pero que no está encontrando. Costo marginal cero.</div></div>
      <div class="cuadro rojo"><div class="t">Éxitos consolidados</div>
        <div class="c">{n(m['cuad_exitos'])}</div>
        <div class="x"><b>Proteger.</b> Asegurar renovación de derechos y continuidad.</div></div>
      <div class="cuadro naranja"><div class="t">Populares mal evaluados</div>
        <div class="c">{n(m['cuad_populares_mal_evaluados'])}</div>
        <div class="x"><b>Vigilar.</b> Generan tráfico, pero erosionan la percepción de calidad.</div></div>
      <div class="cuadro"><div class="t">Bajo rendimiento</div>
        <div class="c">{n(m['cuad_bajo_rendimiento'])}</div>
        <div class="x"><b>Revisar.</b> Candidatos naturales a depuración del catálogo.</div></div>
    </div>
  </div></div>"""))

    # 10 --------------------------------------------------------------
    s.append(diapo(10, f"""
  <div class="et">Dónde está la oportunidad · 1 de 2</div>
  <h2>Los géneros mejor evaluados son los menos representados</h2>
  <div class="cuerpo">
    <div class="fig" style="flex:1.45"><img src="{img('05_generos_calidad_volumen')}" alt=""></div>
    <div class="col" style="flex:0 0 74mm">
      <table>
        <thead><tr><th>Género</th><th class="num">Títulos</th><th class="num">Calif.</th></tr></thead>
        <tbody>{filas_op}</tbody>
      </table>
      <p style="font-size:11pt; margin-top:4mm; color:#6B6B6B">Calidad sobre la mediana,
      oferta por debajo de ella. En el extremo opuesto, {gb[0]['genero']}
      ({d(gb[0]['calificacion'])}) y {gb[1]['genero']} ({d(gb[1]['calificacion'])}) suman
      {n(gb[0]['titulos'] + gb[1]['titulos'])} títulos con las peores calificaciones.</p>
    </div>
  </div>"""))

    # 11 --------------------------------------------------------------
    s.append(diapo(11, f"""
  <div class="et">Dónde está la oportunidad · 2 de 2</div>
  <h2>El inglés domina el catálogo, pero no la calidad percibida</h2>
  <div class="cuerpo">
    <div class="fig" style="flex:1.45"><img src="{img('07_mercados_idiomas')}" alt=""></div>
    <div class="col" style="flex:0 0 74mm">
      <div class="cifra" style="margin-bottom:6mm">
        <div class="v">{d(m['ingles_pct_catalogo'], 1)}%</div>
        <div class="e">del catálogo calificado está en inglés…</div></div>
      <div class="cifra n">
        <div class="v">{m['ingles_posicion']}º<span style="font-size:18pt"> de {m['mercados_analizados']}</span></div>
        <div class="e">…pero ocupa ese lugar en calificación promedio</div></div>
      <table style="margin-top:6mm">
        <thead><tr><th>Mercado</th><th class="num">Títulos</th><th class="num">Calif.</th></tr></thead>
        <tbody>{filas_mk}</tbody>
      </table>
    </div>
  </div>"""))

    # 12 --------------------------------------------------------------
    s.append(diapo(12, f"""
  <div class="et">Riesgo comercial</div>
  <h2>El riesgo no está en las apuestas grandes: está en el tramo medio</h2>
  <div class="cuerpo">
    <div class="fig" style="flex:1.5"><img src="{img('10_rentabilidad_escala')}" alt=""></div>
    <div class="col" style="flex:0 0 68mm">
      <p style="font-size:12pt"><b>Contra la intuición:</b> la tasa de éxito comercial
      <b>crece</b> con la escala de inversión.</p>
      <p style="font-size:12pt">El peor desempeño está en el tramo medio
      ({d(peor['pct_rentables'], 1)}%), por debajo incluso de las producciones de bajo presupuesto
      — y es donde se concentra el mayor número de películas ({n(peor['peliculas'])}).</p>
      <p style="font-size:10.5pt; color:#6B6B6B; margin-top:4mm"><b>Cautela:</b> solo
      {d(m['peliculas_con_finanzas_pct'], 1)}% de las películas informa datos financieros.
      Lectura indicativa.</p>
    </div>
  </div>"""))

    # 13 --------------------------------------------------------------
    s.append(diapo(13, f"""
  <div class="et">La herramienta</div>
  <h2>Un dashboard para verificar y explorar, sin depender del equipo analítico</h2>
  <div class="cuerpo"><div class="col">
    <ul class="puntos">
      <li><b>Indicadores</b>Cuatro KPI que se recalculan con cada filtro, cada uno declarando
          sobre qué base se calcula.</li>
      <li><b>Filtros cruzados</b>Formato, género, idioma, año desde y calificación mínima,
          aplicables de forma simultánea.</li>
      <li><b>Navegación</b>Cuatro pestañas temáticas; los filtros persisten al cambiar de vista.</li>
      <li><b>Interacción</b>Detalle al pasar el cursor, zoom en las dispersiones y aviso
          explícito cuando una combinación no arroja datos suficientes.</li>
    </ul>
  </div><div class="col">
    <div class="cuadro" style="border-left-color:var(--rojo)">
      <div class="t">Decisión técnica: HTML autocontenido</div>
      <div class="x" style="font-size:11pt">Se evaluaron Power BI, Tableau, Streamlit y Dash.
      Se optó por un archivo HTML único con Plotly porque es el <b>único formato que cualquier
      destinatario puede abrir sin licencia, sin instalación y sin levantar un servidor</b>.
      Los {n(m['registros_dashboard'])} registros se embeben en el archivo: el filtrado ocurre en
      el navegador y funciona sin conexión.</div></div>
    <p style="font-size:11pt; color:#6B6B6B; margin-top:5mm">Todo el proyecto se construyó en
    Python: <b>Matplotlib</b> para las 12 figuras estáticas del informe y <b>Plotly</b> para este
    dashboard, ambos gobernados por el mismo módulo de estilo — comparten paleta, tipografía y
    convención numérica, así que quien pasa del documento al tablero reconoce los mismos
    gráficos, ahora explorables.</p>
  </div></div>"""))

    # 14 --------------------------------------------------------------
    s.append(diapo(14, f"""
  <div class="et">Evaluación crítica</div>
  <h2>Qué sostiene esta solución y qué no puede afirmar</h2>
  <div class="cuerpo">
    <div class="col">
      <h3 style="color:var(--verde)">Fortalezas</h3>
      <ul class="puntos" style="font-size:11.5pt">
        <li><b>Hallazgo robusto</b>Se sostiene sobre {n(m['evaluables'])} títulos y se mantiene al
            segmentar por formato, género y año.</li>
        <li><b>Trazabilidad completa</b>Reproducible desde los archivos originales; las cifras
            se generan, no se transcriben.</li>
        <li><b>Calidad de datos explícita</b>Ocho problemas detectados y documentados antes de analizar.</li>
      </ul>
    </div>
    <div class="col">
      <h3 style="color:var(--naranja)">Limitaciones</h3>
      <ul class="puntos" style="font-size:11.5pt">
        <li><b>Sin datos de usuarios</b>No hay reproducciones, suscripciones ni cancelaciones:
            <b>no podemos medir retención ni engagement reales</b>. Usamos popularidad como
            aproximación de atención.</li>
        <li><b>Cobertura financiera parcial</b>Solo {d(m['peliculas_con_finanzas_pct'], 1)}% de
            las películas informa presupuesto e ingresos, probablemente las de mayor circulación.</li>
        <li><b>Calificaciones externas</b>Provienen de una comunidad que no equivale a la base
            de suscriptores.</li>
        <li><b>El umbral de votos sesga la muestra</b>Lo supera el {d(m['pct_supera_umbral_peliculas'], 1)}%
            de las películas pero solo el {d(m['pct_supera_umbral_series'], 1)}% de las series: los
            recuentos por cuadrante están dominados por películas.</li>
      </ul>
    </div>
  </div>"""))

    # 15 --------------------------------------------------------------
    s.append(diapo(15, f"""
  <div class="et">De hallazgos a decisiones comerciales</div>
  <h2>Tres palancas para atraer y retener, sin tocar presupuesto de contenido</h2>
  <div class="cuerpo"><div class="col">
    <div class="cuadros" style="grid-template-columns:repeat(3,1fr)">
      <div class="cuadro verde"><div class="t">1 · Joyas Ocultas</div>
        <div class="c">{n(m['cuad_calidad_sin_visibilidad'])}</div>
        <div class="x"><b>Hallazgo:</b> títulos ya en catálogo, bien evaluados, con baja
        visibilidad.<br><b>Atracción:</b> marketing editorial de nicho.<br>
        <b>Retención:</b> fila fija de descubrimiento.<br>
        <b>KPI:</b> % de usuarios que los consumen al mes.</div></div>
      <div class="cuadro rojo"><div class="t">2 · Momentum por Género</div>
        <div class="c">+{d(m['momentum_top_generos'][0]['variacion_pct'], 0)}%</div>
        <div class="x"><b>Hallazgo:</b> rotación real de interés entre géneros (no crecimiento
        agregado).<br><b>Atracción:</b> campañas segmentadas por género en alza.<br>
        <b>Retención:</b> onboarding anclado al género de entrada.<br>
        <b>KPI:</b> variación trimestral de popularidad por género.</div></div>
      <div class="cuadro" style="border-left-color:var(--azul)"><div class="t">3 · Series como Ancla</div>
        <div class="c">+{d(m['brecha_series_peliculas_controlada'])}</div>
        <div class="x"><b>Hallazgo:</b> ventaja estructural de series sobre películas, 16 años
        sin excepción.<br><b>Atracción:</b> primer episodio gratuito.<br>
        <b>Retención:</b> hábito de consumo episódico.<br>
        <b>KPI:</b> retorno semanal y episodios en 7 días.</div></div>
    </div>
    <p style="font-size:10.5pt; color:#6B6B6B; margin-top:5mm">Ninguna propuesta usa variables
    financieras: las tres se apoyan solo en popularidad, calificación, votos, género, formato y
    año — las mismas variables que sostienen el resto de este análisis.</p>
  </div></div>"""))

    # 16 --------------------------------------------------------------
    joyas_ej = m['joyas_ejemplos'][:4]
    filas_joyas = "".join(
        f"<tr><td>{e['title']}</td><td>{e['tipo']}</td><td>{e['genero']}</td>"
        f"<td class='num'>{d(e['calificacion'])}</td></tr>" for e in joyas_ej)
    s.append(diapo(16, f"""
  <div class="et">Propuesta prioritaria</div>
  <h2>Programa Joyas Ocultas: el contenido ya está pagado, falta exponerlo</h2>
  <div class="cuerpo">
    <div class="fig" style="flex:1.5"><img src="{img('11_joyas_ocultas')}" alt=""></div>
    <div class="col" style="flex:0 0 78mm">
      <div class="cifra v2" style="margin-bottom:5mm">
        <div class="v">{d(m['pct_calidad_sin_visibilidad'], 1)}%</div>
        <div class="e">del catálogo evaluable: {n(m['cuad_calidad_sin_visibilidad_peliculas'])}
        películas y {n(m['cuad_calidad_sin_visibilidad_series'])} series</div></div>
      <p style="font-size:11pt">Califican en promedio
      <b>{d(m['joyas_calificacion_media_peliculas'])}</b> (películas) y
      <b>{d(m['joyas_calificacion_media_series'])}</b> (series) — por encima del resto del
      catálogo evaluable ({d(m['resto_calificacion_media_peliculas'])} y
      {d(m['resto_calificacion_media_series'])}).</p>
      <table style="margin-top:4mm">
        <thead><tr><th>Ejemplo</th><th>Formato</th><th>Género</th><th class="num">Calif.</th></tr></thead>
        <tbody>{filas_joyas}</tbody>
      </table>
      <p style="font-size:10pt; color:#6B6B6B; margin-top:3mm">Costo de adquisición de
      contenido: <b>cero</b>. La palanca es exposición, no compra.</p>
    </div>
  </div>"""))

    # 17 --------------------------------------------------------------
    s.append(diapo(17, f"""
  <div class="et">Recomendaciones</div>
  <h2>Cinco decisiones, ordenadas por costo de implementación</h2>
  <div class="cuerpo"><div class="col">
    <table>
      <thead><tr><th style="width:5%">#</th><th style="width:26%">Recomendación</th>
        <th>Fundamento</th><th style="width:17%">Costo</th></tr></thead>
      <tbody>
        <tr><td><b>1</b></td><td><b>Activar la calidad sin visibilidad</b></td>
            <td>{n(m['cuad_calidad_sin_visibilidad'])} títulos bien evaluados sin exposición: contenido ya pagado</td>
            <td style="color:var(--verde)"><b>Marginal cero</b></td></tr>
        <tr><td><b>2</b></td><td><b>Rebalancear la adquisición</b></td>
            <td>Géneros como {go[0]['genero'].lower()} y mercados como el {mt[0]['idioma'].lower()}:
            alta valoración, baja presencia</td><td>Medio</td></tr>
        <tr><td><b>3</b></td><td><b>Reforzar el formato serie</b></td>
            <td>Ventaja de {d(m['brecha_series_peliculas'])} puntos sostenida
            {m['anios_series_sobre_peliculas']} años sin excepción</td><td>Alto</td></tr>
        <tr><td><b>4</b></td><td><b>Revisar el tramo medio de inversión</b></td>
            <td>{d(peor['pct_rentables'], 1)}% de éxito frente a {d(mejor['pct_rentables'], 1)}%
            en el tramo muy alto</td><td>Reasignación</td></tr>
        <tr><td><b>5</b></td><td><b>Incorporar datos de usuario</b></td>
            <td>Permitiría medir el efecto real sobre la retención</td><td>Proyecto</td></tr>
      </tbody>
    </table>
  </div></div>"""))

    # 18 --------------------------------------------------------------
    s.append(f"""<div class="diapo cierre">
  <div class="et">Conclusión</div>
  <h2>StreamView Analytics no tiene un problema de catálogo.<br>Tiene un problema de visibilidad.</h2>
  <p>El contenido que su audiencia mejor valora ya está comprado.<br>
  Solo no se está mostrando.</p>
  <p style="margin-top:8mm; font-size:13pt; color:#8E8A8A">
  De todas las palancas examinadas, cerrar esa brecha es la de menor costo y mayor retorno esperado.</p>
  <p style="margin-top:12mm; font-size:10pt; color:#6B6B6B; max-width:200mm">
  Esta narrativa se sostuvo en tres canales: <b style="color:#B8B4B4">oral</b> durante la defensa,
  <b style="color:#B8B4B4">escrita</b> en el informe ejecutivo, y <b style="color:#B8B4B4">visual</b>
  en estas diapositivas y en el dashboard interactivo.</p>
  <div class="marca" style="color:#5A5555">Stream<b>View</b> Analytics</div>
  <div class="num-diapo" style="color:#5A5555">18</div>
</div>""")

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>Inteligencia de Catálogo · Presentación ejecutiva</title>
<style>{CSS}</style></head>
<body>
<div class="aviso"><strong>Para exportar a PDF:</strong> Ctrl+P (o Cmd+P) →
<strong>Guardar como PDF</strong> → orientación <strong>horizontal</strong>, márgenes
<strong>ninguno</strong> y <strong>Gráficos de fondo</strong> activado. Este aviso no se imprime.</div>
<div id="pila">{''.join(s)}</div>
<script>
(function(){{
  var pila = document.getElementById("pila");
  function ajustar(){{
    pila.style.transform = "none";
    pila.style.height = "auto";
    var ancho = pila.getBoundingClientRect().width;
    var escala = Math.min(1, (window.innerWidth - 20) / ancho);
    if(escala < 1){{
      pila.style.transform = "scale(" + escala + ")";
      pila.style.height = (pila.scrollHeight * escala) + "px";
    }}
  }}
  window.addEventListener("resize", ajustar);
  window.addEventListener("beforeprint", function(){{
    pila.style.transform = "none"; pila.style.height = "auto";
  }});
  window.addEventListener("afterprint", ajustar);
  ajustar();
}})();
</script>
</body></html>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    m = json.loads((PROC / "metricas.json").read_text(encoding="utf-8"))
    salida = OUT / "presentacion_ejecutiva.html"
    salida.write_text(construir(m), encoding="utf-8")
    print(f"{salida}  ({salida.stat().st_size/1024/1024:.1f} MB)")
    print("18 diapositivas · exportar con Ctrl+P > Guardar como PDF (horizontal)")


if __name__ == "__main__":
    main()
