# -*- coding: utf-8 -*-
"""
StreamView Analytics - Generador del dashboard interactivo (CRISP-DM Fase 6)

Compila los datos procesados en un unico archivo HTML autocontenido que no
requiere servidor ni instalacion: el dashboard se abre directamente en el
navegador. El filtrado es cruzado y se resuelve en el cliente, de modo que
KPIs y graficos se recalculan en conjunto ante cualquier combinacion.

Uso:  python src/dashboard_build.py
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np

PROC = Path("data/processed")
DASH = Path("dashboard")

PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StreamView Analytics · Inteligencia de Catálogo</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js"></script>
<style>
:root{
  --rojo:#E50914; --azul:#0072B2; --verde:#009E73; --naranja:#E69F00;
  --carbon:#221F1F; --gris:#B3B3B3; --grisclaro:#E8E8E8; --fondo:#FAFAFA;
  --texto2:#6B6B6B;
}
*{box-sizing:border-box}
body{margin:0;background:var(--fondo);color:var(--carbon);
  font-family:'Segoe UI',system-ui,-apple-system,sans-serif;font-size:14px}
header{background:var(--carbon);color:#fff;padding:20px 28px}
header h1{margin:0;font-size:21px;letter-spacing:-.3px}
header h1 span{color:var(--rojo)}
header p{margin:5px 0 0;font-size:13px;color:#B0B0B0}
.envoltorio{max-width:1400px;margin:0 auto;padding:0 20px 48px}

.filtros{background:#fff;border:1px solid var(--grisclaro);border-radius:10px;
  padding:16px 20px;margin:20px 0;display:flex;gap:22px;flex-wrap:wrap;align-items:flex-end}
.filtro{display:flex;flex-direction:column;gap:5px;min-width:150px;flex:1}
.filtro label{font-size:11px;font-weight:600;text-transform:uppercase;
  letter-spacing:.5px;color:var(--texto2)}
select,input[type=range]{padding:7px 9px;border:1px solid var(--gris);
  border-radius:6px;font-size:13px;font-family:inherit;background:#fff;color:var(--carbon)}
input[type=range]{padding:0;accent-color:var(--rojo)}
#limpiar{background:var(--carbon);color:#fff;border:0;border-radius:6px;
  padding:9px 16px;cursor:pointer;font-size:13px;font-family:inherit}
#limpiar:hover{background:var(--rojo)}
.anios{font-variant-numeric:tabular-nums;font-weight:600;font-size:13px}

.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:20px}
.kpi{background:#fff;border:1px solid var(--grisclaro);border-radius:10px;padding:16px 18px;
  border-left:4px solid var(--rojo)}
.kpi .et{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:var(--texto2);
  font-weight:600;margin-bottom:6px}
.kpi .val{font-size:27px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums}
.kpi .sub{font-size:11.5px;color:var(--texto2);margin-top:5px}
.kpi.azul{border-left-color:var(--azul)} .kpi.verde{border-left-color:var(--verde)}
.kpi.naranja{border-left-color:var(--naranja)}

nav{display:flex;gap:4px;border-bottom:2px solid var(--grisclaro);margin-bottom:18px;flex-wrap:wrap}
nav button{background:none;border:0;border-bottom:3px solid transparent;margin-bottom:-2px;
  padding:11px 17px;cursor:pointer;font-size:14px;font-family:inherit;color:var(--texto2);font-weight:500}
nav button:hover{color:var(--carbon)}
nav button.activo{color:var(--rojo);border-bottom-color:var(--rojo);font-weight:600}

.panel{display:none} .panel.activo{display:block}
.rejilla{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:16px}
.tarjeta{background:#fff;border:1px solid var(--grisclaro);border-radius:10px;padding:16px 18px}
.tarjeta.ancha{grid-column:1/-1}
.tarjeta h3{margin:0;font-size:15px}
.tarjeta .nota{margin:4px 0 10px;font-size:12px;color:var(--texto2)}
.gr{width:100%;height:340px} .gr.alto{height:430px}
.vacio{text-align:center;padding:44px 16px;color:var(--texto2);font-size:13px}
footer{margin-top:26px;padding-top:16px;border-top:1px solid var(--grisclaro);
  font-size:11.5px;color:var(--texto2);line-height:1.7}
@media(max-width:700px){.rejilla{grid-template-columns:1fr}.gr{height:290px}}
</style>
</head>
<body>
<header>
  <h1>StreamView <span>Analytics</span> · Inteligencia de Catálogo</h1>
  <p>Análisis exploratorio del catálogo de contenidos 2010-2025 · Dirección de Contenidos</p>
</header>

<div class="envoltorio">
  <div class="filtros">
    <div class="filtro"><label for="fTipo">Formato</label>
      <select id="fTipo"><option value="">Todos</option>
        <option value="0">Películas</option><option value="1">Series</option></select></div>
    <div class="filtro"><label for="fGenero">Género principal</label>
      <select id="fGenero"><option value="">Todos</option></select></div>
    <div class="filtro"><label for="fIdioma">Idioma original</label>
      <select id="fIdioma"><option value="">Todos</option></select></div>
    <div class="filtro"><label for="fAnio">Desde el año: <span id="etAnio" class="anios"></span></label>
      <input type="range" id="fAnio" min="__ANIO_MIN__" max="__ANIO_MAX__" value="__ANIO_MIN__" step="1"></div>
    <div class="filtro"><label for="fCalif">Calificación mínima: <span id="etCalif" class="anios">0,0</span></label>
      <input type="range" id="fCalif" min="0" max="9" value="0" step="0.5"></div>
    <button id="limpiar">Limpiar filtros</button>
  </div>

  <div class="kpis">
    <div class="kpi"><div class="et">Títulos en selección</div>
      <div class="val" id="kTitulos">-</div><div class="sub" id="kTitulosSub">-</div></div>
    <div class="kpi azul"><div class="et">Calificación promedio</div>
      <div class="val" id="kCalif">-</div><div class="sub" id="kCalifSub">-</div></div>
    <div class="kpi verde"><div class="et">Popularidad mediana</div>
      <div class="val" id="kPop">-</div><div class="sub" id="kPopSub">-</div></div>
    <div class="kpi naranja"><div class="et">Sin calificar</div>
      <div class="val" id="kSin">-</div><div class="sub" id="kSinSub">-</div></div>
  </div>

  <nav>
    <button class="activo" data-panel="p1">Visión general</button>
    <button data-panel="p2">Calidad vs. popularidad</button>
    <button data-panel="p3">Mercados y tendencia</button>
    <button data-panel="p4">Desempeño financiero</button>
  </nav>

  <section class="panel activo" id="p1"><div class="rejilla">
    <div class="tarjeta"><h3>Composición del catálogo</h3>
      <p class="nota">Títulos por género principal. Barras horizontales: permiten leer etiquetas largas sin rotarlas.</p>
      <div class="gr alto" id="g1"></div></div>
    <div class="tarjeta"><h3>Distribución de calificaciones</h3>
      <p class="nota">Histograma: muestra la forma completa de la distribución, no solo el promedio.</p>
      <div class="gr alto" id="g2"></div></div>
  </div></section>

  <section class="panel" id="p2"><div class="rejilla">
    <div class="tarjeta ancha"><h3>¿Lo más popular es lo mejor evaluado?</h3>
      <p class="nota">Dispersión con cuadrantes. Las medianas se calculan <strong>dentro de cada formato</strong>, porque el índice de popularidad no es comparable entre películas y series. Escala logarítmica: la variable abarca tres órdenes de magnitud.</p>
      <div class="gr alto" id="g3"></div></div>
    <div class="tarjeta ancha"><h3>Género: calidad frente a volumen de oferta</h3>
      <p class="nota">Burbujas: posición para las dos variables críticas, tamaño para la popularidad mediana.</p>
      <div class="gr alto" id="g4"></div></div>
  </div></section>

  <section class="panel" id="p3"><div class="rejilla">
    <div class="tarjeta"><h3>Calificación por idioma original</h3>
      <p class="nota">Ranking ordenado con línea base en cero, para no exagerar diferencias entre mercados.</p>
      <div class="gr alto" id="g5"></div></div>
    <div class="tarjeta"><h3>Evolución de la calificación</h3>
      <p class="nota">Serie temporal por formato. El año 2025 tiene cobertura parcial de votos.</p>
      <div class="gr alto" id="g6"></div></div>
  </div></section>

  <section class="panel" id="p4"><div class="rejilla">
    <div class="tarjeta ancha"><h3>Presupuesto frente a ingresos</h3>
      <p class="nota">Solo películas con dato financiero informado. Escala log-log; la diagonal marca el punto de equilibrio.</p>
      <div class="gr alto" id="g7"></div></div>
  </div></section>

  <footer>
    <strong>Fuente:</strong> catálogo Netflix 2010-2025 · muestra estratificada de 1.000 títulos por año y formato (31.991 registros).<br>
    <strong>Advertencias metodológicas:</strong> el volumen anual es constante por diseño del muestreo, por lo que no deben leerse tendencias de crecimiento del catálogo.
    Los títulos sin votos se excluyen de todo promedio de calificación. Los valores de presupuesto e ingreso en cero se tratan como dato faltante.
    El género mostrado es el principal de cada título. El índice de popularidad no es comparable entre formatos, por lo que los cuadrantes se calculan con umbrales propios de cada uno. El umbral de 50 votos lo supera el 81% de las películas pero solo el 26% de las series, de modo que los recuentos absolutos están dominados por el formato película.
  </footer>
</div>

<script>
const DATOS = __DATOS__;
const GENEROS = __GENEROS__;
const IDIOMAS = __IDIOMAS__;
const TIPOS = ["Películas","Series"];
const C = {rojo:"#E50914", azul:"#0072B2", verde:"#009E73", naranja:"#E69F00",
           gris:"#B3B3B3", carbon:"#221F1F", grisclaro:"#E8E8E8"};
// Indices de columna del arreglo compacto de datos
const TIPO=0, ANIO=1, GEN=2, IDI=3, POP=4, CAL=5, VOT=6, PRE=7, ING=8;

const BASE = {
  font:{family:"Segoe UI, system-ui, sans-serif", size:12, color:C.carbon},
  // Convencion numerica espanola: coma decimal, punto para los miles.
  separators:",.",
  margin:{l:60,r:24,t:16,b:50}, paper_bgcolor:"#fff", plot_bgcolor:"#fff",
  hoverlabel:{font:{family:"Segoe UI, sans-serif"}},
  xaxis:{gridcolor:C.grisclaro, zeroline:false},
  yaxis:{gridcolor:C.grisclaro, zeroline:false}
};
const CONF = {displayModeBar:false, responsive:true};

const nf0 = new Intl.NumberFormat("es-CL",{maximumFractionDigits:0});
const nf1 = new Intl.NumberFormat("es-CL",{minimumFractionDigits:1,maximumFractionDigits:1});
const nf2 = new Intl.NumberFormat("es-CL",{minimumFractionDigits:2,maximumFractionDigits:2});

function filtrar(){
  const t = document.getElementById("fTipo").value;
  const g = document.getElementById("fGenero").value;
  const i = document.getElementById("fIdioma").value;
  const a = +document.getElementById("fAnio").value;
  const c = +document.getElementById("fCalif").value;
  return DATOS.filter(f =>
    (t === "" || f[TIPO] === +t) &&
    (g === "" || f[GEN] === +g) &&
    (i === "" || f[IDI] === +i) &&
    f[ANIO] >= a &&
    (c === 0 || (f[CAL] !== null && f[CAL] >= c)));
}

function mediana(v){
  if(!v.length) return null;
  const s = [...v].sort((x,y)=>x-y), m = Math.floor(s.length/2);
  return s.length % 2 ? s[m] : (s[m-1]+s[m])/2;
}
function promedio(v){ return v.length ? v.reduce((a,b)=>a+b,0)/v.length : null; }
function vacio(id, msg){
  document.getElementById(id).innerHTML =
    '<div class="vacio">' + (msg || "Sin datos para esta combinación de filtros") + '</div>';
}

function pintarKpis(d){
  const cal = d.filter(f=>f[CAL]!==null).map(f=>f[CAL]);
  const pop = d.map(f=>f[POP]);
  const sin = d.length - cal.length;
  document.getElementById("kTitulos").textContent = nf0.format(d.length);
  document.getElementById("kTitulosSub").textContent =
    nf0.format(d.filter(f=>f[TIPO]===0).length) + " películas · " +
    nf0.format(d.filter(f=>f[TIPO]===1).length) + " series";
  document.getElementById("kCalif").textContent = cal.length ? nf2.format(promedio(cal)) : "–";
  document.getElementById("kCalifSub").textContent = cal.length
    ? "sobre " + nf0.format(cal.length) + " títulos calificados" : "sin títulos calificados";
  document.getElementById("kPop").textContent = pop.length ? nf1.format(mediana(pop)) : "–";
  document.getElementById("kPopSub").textContent = "índice de atención de la audiencia";
  document.getElementById("kSin").textContent = d.length
    ? nf1.format(sin/d.length*100) + "%" : "–";
  document.getElementById("kSinSub").textContent = nf0.format(sin) + " títulos sin votos registrados";
}

function g1_composicion(d){
  if(!d.length) return vacio("g1");
  const pel = {}, ser = {};
  d.forEach(f=>{ const m = f[TIPO]===0 ? pel : ser; m[f[GEN]] = (m[f[GEN]]||0)+1; });
  const tot = {};
  Object.keys(pel).concat(Object.keys(ser)).forEach(k=>{ tot[k]=(pel[k]||0)+(ser[k]||0); });
  const orden = Object.keys(tot).sort((a,b)=>tot[a]-tot[b]).slice(-12);
  const et = orden.map(k=>GENEROS[k]);
  Plotly.react("g1", [
    {type:"bar", orientation:"h", y:et, x:orden.map(k=>pel[k]||0), name:"Películas",
     marker:{color:C.rojo}, hovertemplate:"%{y}<br>%{x:,} películas<extra></extra>"},
    {type:"bar", orientation:"h", y:et, x:orden.map(k=>ser[k]||0), name:"Series",
     marker:{color:C.azul}, hovertemplate:"%{y}<br>%{x:,} series<extra></extra>"}
  ], Object.assign({}, BASE, {
    barmode:"group", margin:{l:150,r:24,t:10,b:44},
    legend:{orientation:"h", y:-0.14, x:0},
    xaxis:Object.assign({}, BASE.xaxis, {title:"Cantidad de títulos"}),
    yaxis:Object.assign({}, BASE.yaxis, {gridcolor:"rgba(0,0,0,0)"})
  }), CONF);
}

function g2_distribucion(d){
  const pel = d.filter(f=>f[TIPO]===0 && f[CAL]!==null).map(f=>f[CAL]);
  const ser = d.filter(f=>f[TIPO]===1 && f[CAL]!==null).map(f=>f[CAL]);
  if(!pel.length && !ser.length) return vacio("g2");
  const trazas = [];
  if(pel.length) trazas.push({type:"histogram", x:pel, name:"Películas", opacity:.68,
    marker:{color:C.rojo}, xbins:{start:0,end:10,size:0.4},
    hovertemplate:"Calificación %{x}<br>%{y} películas<extra></extra>"});
  if(ser.length) trazas.push({type:"histogram", x:ser, name:"Series", opacity:.68,
    marker:{color:C.azul}, xbins:{start:0,end:10,size:0.4},
    hovertemplate:"Calificación %{x}<br>%{y} series<extra></extra>"});
  Plotly.react("g2", trazas, Object.assign({}, BASE, {
    barmode:"overlay", legend:{orientation:"h", y:-0.16, x:0},
    xaxis:Object.assign({}, BASE.xaxis, {title:"Calificación de la audiencia", range:[0,10]}),
    yaxis:Object.assign({}, BASE.yaxis, {title:"Cantidad de títulos"})
  }), CONF);
}

function g3_cuadrantes(d){
  const v = d.filter(f=>f[CAL]!==null && f[VOT]>=50);
  if(v.length < 12) return vacio("g3", "Se requieren al menos 12 títulos con 50 votos o más");
  // El indice de popularidad no es comparable entre formatos: su mediana en
  // series cuadruplica la de peliculas. Los umbrales se calculan dentro de
  // cada formato presente en la seleccion; de lo contrario el corte separaria
  // formatos en vez de medir visibilidad relativa.
  const umbral = {};
  [0,1].forEach(t=>{
    const s = v.filter(f=>f[TIPO]===t);
    if(s.length) umbral[t] = {x:mediana(s.map(f=>f[POP])), y:mediana(s.map(f=>f[CAL]))};
  });
  const esJoya = f => f[POP] < umbral[f[TIPO]].x && f[CAL] > umbral[f[TIPO]].y;
  const esExito = f => f[POP] >= umbral[f[TIPO]].x && f[CAL] > umbral[f[TIPO]].y;
  const esSobre = f => f[POP] >= umbral[f[TIPO]].x && f[CAL] <= umbral[f[TIPO]].y;
  const joya = v.filter(esJoya);
  const resto = v.filter(f=>!esJoya(f));
  const unicoFormato = Object.keys(umbral).length === 1;
  const mx = unicoFormato ? umbral[Object.keys(umbral)[0]].x : null;
  const my = unicoFormato ? umbral[Object.keys(umbral)[0]].y : null;
  const pts = (s,col) => ({type:"scattergl", mode:"markers", x:s.map(f=>f[POP]),
    y:s.map(f=>f[CAL]), marker:{size:5, color:col, opacity:.34},
    text:s.map(f=>GENEROS[f[GEN]]+" · "+TIPOS[f[TIPO]]+" · "+f[ANIO]),
    hovertemplate:"%{text}<br>Popularidad %{x:.1f}<br>Calificación %{y:.1f}<extra></extra>",
    showlegend:false});
  Plotly.react("g3", [pts(resto,C.gris), pts(joya,C.verde)],
    Object.assign({}, BASE, {
      margin:{l:60,r:24,t:10,b:50},
      xaxis:Object.assign({}, BASE.xaxis, {title:"Popularidad (escala logarítmica)", type:"log"}),
      yaxis:Object.assign({}, BASE.yaxis, {title:"Calificación de la audiencia"}),
      // Las lineas de corte solo se dibujan cuando la seleccion contiene un
      // unico formato: con ambos hay dos umbrales distintos y una sola linea
      // daria a entender un corte comun que no existe.
      shapes: unicoFormato ? [
        {type:"line", x0:Math.log10(mx), x1:Math.log10(mx), xref:"x", yref:"paper",
         y0:0, y1:1, line:{color:C.carbon, width:1.2, dash:"dash"}},
        {type:"line", y0:my, y1:my, yref:"y", xref:"paper", x0:0, x1:1,
         line:{color:C.carbon, width:1.2, dash:"dash"}}] : [],
      annotations:[
        {x:0.01, y:0.99, xref:"paper", yref:"paper", xanchor:"left", yanchor:"top",
         text:"<b>CALIDAD SIN VISIBILIDAD</b><br>"+nf0.format(joya.length)+" títulos",
         showarrow:false, font:{color:C.verde, size:11}, align:"left",
         bgcolor:"rgba(255,255,255,.92)", bordercolor:C.verde, borderpad:5},
        {x:0.99, y:0.99, xref:"paper", yref:"paper", xanchor:"right", yanchor:"top",
         text:"<b>ÉXITOS CONSOLIDADOS</b><br>"+nf0.format(v.filter(esExito).length)+" títulos",
         showarrow:false, font:{color:C.rojo, size:11}, align:"left",
         bgcolor:"rgba(255,255,255,.92)", bordercolor:C.rojo, borderpad:5},
        {x:0.99, y:0.02, xref:"paper", yref:"paper", xanchor:"right", yanchor:"bottom",
         text:"<b>POPULARES MAL EVALUADOS</b><br>"+nf0.format(v.filter(esSobre).length)+" títulos",
         showarrow:false, font:{color:C.naranja, size:11}, align:"left",
         bgcolor:"rgba(255,255,255,.92)", bordercolor:C.naranja, borderpad:5},
        {x:0.01, y:0.02, xref:"paper", yref:"paper", xanchor:"left", yanchor:"bottom",
         text: unicoFormato ? "" :
           "Umbrales calculados dentro de cada formato<br>(filtra por formato para ver los cortes)",
         showarrow:false, font:{color:"#8A8A8A", size:9.5}, align:"left"}]
    }), CONF);
}

function g4_generos(d){
  const v = d.filter(f=>f[CAL]!==null);
  if(!v.length) return vacio("g4");
  const acc = {};
  v.forEach(f=>{ (acc[f[GEN]] = acc[f[GEN]] || {c:[], p:[]}); acc[f[GEN]].c.push(f[CAL]); acc[f[GEN]].p.push(f[POP]); });
  const ks = Object.keys(acc).filter(k=>acc[k].c.length >= 25);
  if(!ks.length) return vacio("g4", "Se requieren géneros con al menos 25 títulos calificados");
  const x = ks.map(k=>acc[k].c.length), y = ks.map(k=>promedio(acc[k].c));
  const pm = ks.map(k=>mediana(acc[k].p)), maxp = Math.max(...pm);
  const medc = mediana(y), medv = mediana(x);
  Plotly.react("g4", [{
    type:"scatter", mode:"markers+text", x:x, y:y, text:ks.map(k=>GENEROS[k]),
    textposition:"top center", textfont:{size:10.5},
    marker:{size:pm.map(p=>10+34*(p/maxp)), opacity:.55,
      color:y.map((c,i)=> c>medc ? (x[i]<medv ? C.verde : C.rojo) : C.gris),
      line:{color:"#fff", width:1.5}},
    customdata:pm,
    hovertemplate:"<b>%{text}</b><br>%{x:,} títulos<br>Calificación %{y:.2f}"+
      "<br>Popularidad mediana %{customdata:.1f}<extra></extra>"
  }], Object.assign({}, BASE, {
    margin:{l:60,r:30,t:26,b:50},
    xaxis:Object.assign({}, BASE.xaxis, {title:"Títulos calificados en el catálogo"}),
    yaxis:Object.assign({}, BASE.yaxis, {title:"Calificación promedio"}),
    shapes:[
      {type:"line", y0:medc, y1:medc, yref:"y", xref:"paper", x0:0, x1:1,
       line:{color:C.gris, width:1, dash:"dash"}},
      {type:"line", x0:medv, x1:medv, xref:"x", yref:"paper", y0:0, y1:1,
       line:{color:C.gris, width:1, dash:"dash"}}]
  }), CONF);
}

function g5_idiomas(d){
  const v = d.filter(f=>f[CAL]!==null);
  if(!v.length) return vacio("g5");
  const acc = {};
  v.forEach(f=>{ (acc[f[IDI]] = acc[f[IDI]] || []).push(f[CAL]); });
  const ks = Object.keys(acc).filter(k=>acc[k].length >= 30 && IDIOMAS[k] !== "Otro")
    .sort((a,b)=>promedio(acc[a])-promedio(acc[b]));
  if(!ks.length) return vacio("g5", "Se requieren mercados con al menos 30 títulos calificados");
  Plotly.react("g5", [{
    type:"bar", orientation:"h", y:ks.map(k=>IDIOMAS[k]), x:ks.map(k=>promedio(acc[k])),
    marker:{color:ks.map(k=>IDIOMAS[k]==="Inglés" ? C.rojo : C.gris)},
    text:ks.map(k=>nf2.format(promedio(acc[k]))), textposition:"outside",
    customdata:ks.map(k=>acc[k].length),
    hovertemplate:"<b>%{y}</b><br>Calificación %{x:.2f}<br>%{customdata:,} títulos<extra></extra>"
  }], Object.assign({}, BASE, {
    margin:{l:96,r:40,t:10,b:44},
    xaxis:Object.assign({}, BASE.xaxis, {title:"Calificación promedio", range:[0,10]}),
    yaxis:Object.assign({}, BASE.yaxis, {gridcolor:"rgba(0,0,0,0)"})
  }), CONF);
}

function g6_evolucion(d){
  const v = d.filter(f=>f[CAL]!==null);
  if(!v.length) return vacio("g6");
  const trazas = [0,1].map(t=>{
    const acc = {};
    v.filter(f=>f[TIPO]===t).forEach(f=>{ (acc[f[ANIO]] = acc[f[ANIO]] || []).push(f[CAL]); });
    const ys = Object.keys(acc).map(Number).sort((a,b)=>a-b);
    return ys.length ? {type:"scatter", mode:"lines+markers", x:ys,
      y:ys.map(a=>promedio(acc[a])), name:TIPOS[t],
      line:{color:t===0?C.rojo:C.azul, width:2.6}, marker:{size:5},
      hovertemplate:"%{x}<br>Calificación %{y:.2f}<extra>"+TIPOS[t]+"</extra>"} : null;
  }).filter(Boolean);
  if(!trazas.length) return vacio("g6");
  Plotly.react("g6", trazas, Object.assign({}, BASE, {
    legend:{orientation:"h", y:-0.16, x:0},
    xaxis:Object.assign({}, BASE.xaxis, {title:"Año de estreno", dtick:2}),
    yaxis:Object.assign({}, BASE.yaxis, {title:"Calificación promedio"})
  }), CONF);
}

function g7_financiero(d){
  // Mismo umbral que el informe: descarta registros con importes irrisorios,
  // que en la fuente reflejan unidades inconsistentes y no cifras reales.
  const v = d.filter(f=>f[PRE]!==null && f[ING]!==null && f[PRE]>0.001 && f[ING]>0.001);
  if(v.length < 10) return vacio("g7", "Sin películas con dato financiero para esta selección");
  const rent = v.filter(f=>f[ING] >= f[PRE]), perd = v.filter(f=>f[ING] < f[PRE]);
  const pts = (s,col,nom) => ({type:"scattergl", mode:"markers", name:nom,
    x:s.map(f=>f[PRE]), y:s.map(f=>f[ING]), marker:{size:6, color:col, opacity:.42},
    text:s.map(f=>GENEROS[f[GEN]]+" · "+f[ANIO]),
    hovertemplate:"%{text}<br>Presupuesto $%{x:,.0f}M<br>Ingresos $%{y:,.0f}M<extra></extra>"});
  const lo = Math.min(...v.map(f=>f[PRE])), hi = Math.max(...v.map(f=>f[PRE]));
  Plotly.react("g7", [
    pts(perd, C.gris, "Bajo el equilibrio"), pts(rent, C.rojo, "Sobre el equilibrio"),
    {type:"scatter", mode:"lines", x:[lo,hi], y:[lo,hi], showlegend:false,
     line:{color:C.carbon, width:1.6, dash:"dash"}, hoverinfo:"skip"}
  ], Object.assign({}, BASE, {
    legend:{orientation:"h", y:-0.16, x:0},
    xaxis:Object.assign({}, BASE.xaxis, {title:"Presupuesto (millones USD)", type:"log"}),
    yaxis:Object.assign({}, BASE.yaxis, {title:"Ingresos (millones USD)", type:"log"}),
    annotations:[{x:0.5, y:1.02, xref:"paper", yref:"paper", showarrow:false,
      text:nf1.format(rent.length/v.length*100)+"% de las películas supera su punto de equilibrio",
      font:{size:12, color:C.carbon}}]
  }), CONF);
}

function actualizar(){
  const d = filtrar();
  pintarKpis(d);
  g1_composicion(d); g2_distribucion(d); g3_cuadrantes(d);
  g4_generos(d); g5_idiomas(d); g6_evolucion(d); g7_financiero(d);
}

function iniciar(){
  const sg = document.getElementById("fGenero");
  GENEROS.map((n,i)=>[n,i]).sort((a,b)=>a[0].localeCompare(b[0],"es"))
    .forEach(([n,i])=>{ const o=document.createElement("option"); o.value=i; o.textContent=n; sg.appendChild(o); });
  const si = document.getElementById("fIdioma");
  IDIOMAS.map((n,i)=>[n,i]).sort((a,b)=>a[0].localeCompare(b[0],"es"))
    .forEach(([n,i])=>{ const o=document.createElement("option"); o.value=i; o.textContent=n; si.appendChild(o); });

  const ea = document.getElementById("etAnio"), fa = document.getElementById("fAnio");
  const ec = document.getElementById("etCalif"), fc = document.getElementById("fCalif");
  const etiquetas = () => { ea.textContent = fa.value; ec.textContent = nf1.format(+fc.value); };
  etiquetas();

  ["fTipo","fGenero","fIdioma","fAnio","fCalif"].forEach(id=>
    document.getElementById(id).addEventListener("input", ()=>{ etiquetas(); actualizar(); }));

  document.getElementById("limpiar").addEventListener("click", ()=>{
    document.getElementById("fTipo").value = "";
    sg.value = ""; si.value = ""; fa.value = fa.min; fc.value = 0;
    etiquetas(); actualizar();
  });

  document.querySelectorAll("nav button").forEach(b=>b.addEventListener("click", ()=>{
    document.querySelectorAll("nav button").forEach(x=>x.classList.remove("activo"));
    document.querySelectorAll(".panel").forEach(x=>x.classList.remove("activo"));
    b.classList.add("activo");
    document.getElementById(b.dataset.panel).classList.add("activo");
    // Plotly necesita recalcular el tamano de los graficos recien visibles
    document.querySelectorAll("#"+b.dataset.panel+" .gr").forEach(g=>Plotly.Plots.resize(g));
  }));

  actualizar();
}
iniciar();
</script>
</body>
</html>
"""


def main():
    DASH.mkdir(exist_ok=True)
    catalogo = pd.read_csv(PROC / "catalogo_unificado.csv")
    peliculas = pd.read_csv(PROC / "peliculas_limpio.csv",
                            usecols=["show_id", "budget", "revenue"])

    d = catalogo.merge(peliculas, on="show_id", how="left")
    d = d[d["genero_principal"].notna()]

    generos = sorted(d["genero_principal"].unique())
    idiomas = sorted(d["idioma"].unique())
    gi = {g: i for i, g in enumerate(generos)}
    ii = {v: i for i, v in enumerate(idiomas)}

    def opcional(v, escala=1.0, cifras=2):
        return None if pd.isna(v) else round(float(v) / escala, cifras)

    filas = [
        [0 if r.tipo == "Película" else 1,
         int(r.release_year),
         gi[r.genero_principal],
         ii[r.idioma],
         round(float(r.popularity), 1),
         opcional(r.vote_average),
         int(r.vote_count),
         opcional(r.budget, 1e6),
         opcional(r.revenue, 1e6)]
        for r in d.itertuples()
    ]

    html = (PLANTILLA
            .replace("__DATOS__", json.dumps(filas, separators=(",", ":")))
            .replace("__GENEROS__", json.dumps(generos, ensure_ascii=False))
            .replace("__IDIOMAS__", json.dumps(idiomas, ensure_ascii=False))
            .replace("__ANIO_MIN__", str(int(d["release_year"].min())))
            .replace("__ANIO_MAX__", str(int(d["release_year"].max()))))

    salida = DASH / "dashboard.html"
    salida.write_text(html, encoding="utf-8")
    print(f"dashboard/dashboard.html  ({salida.stat().st_size/1024:.0f} KB)")
    print(f"  registros embebidos : {len(filas):,}")
    print(f"  generos             : {len(generos)}")
    print(f"  idiomas             : {len(idiomas)}")


if __name__ == "__main__":
    main()
