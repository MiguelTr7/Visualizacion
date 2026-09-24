# -*- coding: utf-8 -*-
"""
StreamView Analytics - Generador de la presentacion ejecutiva en PowerPoint

Traduce el mismo contenido de presentacion_build.py (version HTML) a un
archivo .pptx nativo de 18 diapositivas, leyendo las cifras desde
data/processed/metricas.json y las figuras desde images/, para que las dos
versiones de la presentacion digan exactamente lo mismo.

Uso:  python src/presentacion_pptx.py
"""
from pathlib import Path
import json

from PIL import Image
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE

PROC = Path("data/processed")
IMG = Path("images")
OUT = Path("reports/informe_ejecutivo")

# --------------------------------------------------------------- paleta --
ROJO = RGBColor(0xE5, 0x09, 0x14)
AZUL = RGBColor(0x00, 0x72, 0xB2)
VERDE = RGBColor(0x00, 0x9E, 0x73)
NARANJA = RGBColor(0xE6, 0x9F, 0x00)
CARBON = RGBColor(0x1A, 0x18, 0x18)
GRIS = RGBColor(0x6B, 0x6B, 0x6B)
LINEA = RGBColor(0xE2, 0xDE, 0xDE)
FONDO = RGBColor(0xFA, 0xF9, 0xF8)
BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
GRIS_CLARO = RGBColor(0xB8, 0xB4, 0xB4)   # texto secundario sobre fondo oscuro
GRIS_MED = RGBColor(0x8E, 0x8A, 0x8A)
DIVISOR_OSCURO = RGBColor(0x3A, 0x36, 0x36)

HEAD = "Cambria"
BODY = "Calibri"

SW, SH = Inches(13.333), Inches(7.5)
MX = Inches(0.55)
CONTENT_TOP = Inches(1.62)
CONTENT_BOTTOM = Inches(6.85)


def acortar(texto, maximo=34):
    if len(texto) <= maximo:
        return texto
    corte = texto[:maximo].rsplit(" ", 1)[0]
    return corte + "…"


def n(x):
    return f"{int(round(float(x))):,}".replace(",", ".")


def d(x, c=2):
    return f"{float(x):.{c}f}".replace(".", ",")


# --------------------------------------------------------------- helpers --
_ASPECT = {}


def aspecto(nombre):
    if nombre not in _ASPECT:
        im = Image.open(IMG / f"{nombre}.png")
        _ASPECT[nombre] = im.size[0] / im.size[1]
    return _ASPECT[nombre]


def add_imagen_fit(slide, nombre, left, top, box_w, box_h):
    ar = aspecto(nombre)
    box_ar = box_w / box_h
    if ar > box_ar:
        w = int(box_w)
        h = int(w / ar)
    else:
        h = int(box_h)
        w = int(h * ar)
    x = int(left + (box_w - w) / 2)
    y = int(top + (box_h - h) / 2)
    slide.shapes.add_picture(str(IMG / f"{nombre}.png"), x, y, width=w, height=h)


def nueva_diapositiva(prs, dark=False):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    bg.fill.solid()
    bg.fill.fore_color.rgb = CARBON if dark else BLANCO
    bg.line.fill.background()
    bg.shadow.inherit = False
    spTree = slide.shapes._spTree
    spTree.remove(bg._element)
    spTree.insert(2, bg._element)
    return slide


def rect(slide, left, top, width, height, color, line=False):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background() if not line else None
    sh.shadow.inherit = False
    return sh


def add_text(slide, text, left, top, width, height, size=14, color=CARBON,
             bold=False, italic=False, font=BODY, align=PP_ALIGN.LEFT,
             anchor=MSO_ANCHOR.TOP, line_spacing=1.0, wrap=True):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    if line_spacing:
        p.line_spacing = line_spacing
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.name = font
    r.font.color.rgb = color
    return box


def add_richtext(slide, left, top, width, height, paragraphs,
                  anchor=MSO_ANCHOR.TOP, wrap=True):
    """paragraphs: lista de dicts con 'runs': [(texto, opts_dict), ...]"""
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = para.get("align", PP_ALIGN.LEFT)
        if "line_spacing" in para:
            p.line_spacing = para["line_spacing"]
        if "space_after" in para:
            p.space_after = Pt(para["space_after"])
        if "space_before" in para:
            p.space_before = Pt(para["space_before"])
        for text, opts in para["runs"]:
            r = p.add_run()
            r.text = text
            r.font.size = Pt(opts.get("size", 12))
            r.font.bold = opts.get("bold", False)
            r.font.italic = opts.get("italic", False)
            r.font.name = opts.get("font", BODY)
            r.font.color.rgb = opts.get("color", CARBON)
    return box


def marcador(slide, left, top, color=ROJO, size=Inches(0.1)):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, size, size)
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def lista_puntos(slide, left, top, width, items, size=12.5, gap=None):
    """items: lista de (label, descripcion). Cada item lleva un marcador
    cuadrado de color junto al texto, replicando la lista con vinetas
    coloreadas del deck HTML."""
    y = top
    for label, desc in items:
        marcador(slide, left, y + Inches(0.03), color=ROJO)
        paras = [
            {"runs": [(label, {"size": size + 0.5, "bold": True, "color": CARBON})],
             "space_after": 2},
            {"runs": [(desc, {"size": size, "color": CARBON})],
             "line_spacing": 1.12},
        ]
        alto_item = Inches(0.34) + Inches(0.24) * (1 + len(desc) // 62)
        add_richtext(slide, left + Inches(0.24), y, width - Inches(0.24), alto_item, paras)
        y = y + alto_item + (gap or Inches(0.14))
    return y


def sin_estilo_tabla(table):
    tblPr = table._tbl.tblPr
    for child in list(tblPr):
        tblPr.remove(child)


def add_tabla(slide, left, top, width, height, headers, rows,
              col_widths=None, align_right=set(), font_size=11.5,
              header_size=9.5, row_h=None):
    n_rows = len(rows) + 1
    n_cols = len(headers)
    gshape = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    tbl = gshape.table
    tbl.first_row = False
    tbl.horz_banding = False
    sin_estilo_tabla(tbl)
    if col_widths:
        for i, w in enumerate(col_widths):
            tbl.columns[i].width = w
    if row_h:
        for r in tbl.rows:
            r.height = row_h

    for j, htext in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = CARBON
        cell.margin_left = cell.margin_right = Pt(7)
        cell.margin_top = cell.margin_bottom = Pt(3)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.RIGHT if j in align_right else PP_ALIGN.LEFT
        r = p.add_run()
        r.text = htext.upper()
        r.font.size = Pt(header_size)
        r.font.bold = True
        r.font.name = BODY
        r.font.color.rgb = BLANCO

    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = FONDO if i % 2 == 1 else BLANCO
            cell.margin_left = cell.margin_right = Pt(7)
            cell.margin_top = cell.margin_bottom = Pt(3)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.RIGHT if j in align_right else PP_ALIGN.LEFT
            if isinstance(val, tuple):
                text, opts = val
            else:
                text, opts = val, {}
            r = p.add_run()
            r.text = str(text)
            r.font.size = Pt(opts.get("size", font_size))
            r.font.bold = opts.get("bold", False)
            r.font.name = BODY
            r.font.color.rgb = opts.get("color", CARBON)
    return gshape


def pie(slide, num, dark=False):
    color = GRIS_MED if dark else GRIS_CLARO
    add_richtext(slide, MX, Inches(7.08), Inches(4), Inches(0.3), [
        {"runs": [("Stream", {"size": 9, "color": color, "bold": True}),
                  ("View", {"size": 9, "color": ROJO, "bold": True}),
                  (" Analytics", {"size": 9, "color": color, "bold": True})]},
    ])
    add_text(slide, str(num), Inches(12.55), Inches(7.08), Inches(0.35), Inches(0.3),
              size=9, color=color, align=PP_ALIGN.RIGHT)


def eyebrow(slide, text, color=ROJO):
    add_text(slide, text.upper(), MX, Inches(0.48), Inches(11.5), Inches(0.32),
             size=11, bold=True, color=color, font=BODY)


def titulo(slide, text, size=25, color=CARBON, width=Inches(11.6), top=Inches(0.86)):
    add_text(slide, text, MX, top, width, Inches(1.15), size=size, bold=True,
             color=color, font=HEAD, line_spacing=1.04)


def franja(slide, runs_paras, top=Inches(5.85), height=Inches(1.0)):
    rect(slide, 0, top, SW, height, CARBON)
    add_richtext(slide, MX, top, SW - 2 * MX, height, runs_paras,
                 anchor=MSO_ANCHOR.MIDDLE)


def cifra(slide, left, top, width, valor, etiqueta, color=ROJO,
          valor_size=30, et_size=10):
    rect(slide, left, top, width, Inches(0.04), color)
    add_text(slide, valor, left, top + Inches(0.1), width, Inches(0.55),
             size=valor_size, bold=True, color=color, font=HEAD)
    add_text(slide, etiqueta, left, top + Inches(0.68), width, Inches(0.55),
             size=et_size, color=GRIS, line_spacing=1.15)


def gigante(slide, left, top, width, valor, pie_html, valor_size=64):
    add_text(slide, valor, left, top, width, Inches(1.0), size=valor_size,
             bold=True, color=ROJO, font=HEAD)
    add_richtext(slide, left, top + Inches(0.95), width, Inches(0.9), [
        {"runs": [(pie_html, {"size": 12.5, "color": GRIS})], "line_spacing": 1.2},
    ])


def notas(slide, texto):
    slide.notes_slide.notes_text_frame.text = texto


def cuadro(slide, left, top, width, height, titulo_txt, valor, desc_runs,
           color=GRIS, valor_size=28):
    rect(slide, left, top, width, height, FONDO)
    pad = Inches(0.18)
    add_text(slide, titulo_txt, left + pad, top + Inches(0.14), width - 2 * pad,
             Inches(0.3), size=11.5, bold=True, color=CARBON)
    add_text(slide, valor, left + pad, top + Inches(0.46), width - 2 * pad,
             Inches(0.5), size=valor_size, bold=True, color=color, font=HEAD)
    add_richtext(slide, left + pad, top + Inches(1.02), width - 2 * pad,
                 height - Inches(1.14), desc_runs, wrap=True)


def tarjeta_texto(slide, left, top, width, height, titulo_txt, desc_runs, color=ROJO):
    rect(slide, left, top, width, height, FONDO)
    pad = Inches(0.2)
    add_text(slide, titulo_txt, left + pad, top + Inches(0.16), width - 2 * pad,
             Inches(0.4), size=13, bold=True, color=color)
    add_richtext(slide, left + pad, top + Inches(0.68), width - 2 * pad,
                 height - Inches(0.85), desc_runs, wrap=True)


# ==========================================================================
def main():
    m = json.loads((PROC / "metricas.json").read_text(encoding="utf-8"))
    gt, gb, go = m["generos_top"], m["generos_bajos"], m["generos_oportunidad"]
    mt = m["mercados_top"]
    esc = m["rentabilidad_por_escala"]
    peor = min(esc, key=lambda e: e["pct_rentables"])
    mejor = max(esc, key=lambda e: e["pct_rentables"])

    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH

    # ---------------- 1. Portada ----------------------------------------
    s = nueva_diapositiva(prs, dark=True)
    add_richtext(s, MX, Inches(0.55), Inches(6), Inches(0.4), [
        {"runs": [("StreamView ", {"size": 15, "bold": True, "color": BLANCO, "font": BODY}),
                  ("Analytics", {"size": 15, "bold": True, "color": ROJO, "font": BODY})]},
    ])
    add_text(s, "Inteligencia de Catálogo", MX, Inches(2.55), Inches(11.5), Inches(1.7),
             size=48, bold=True, color=BLANCO, font=HEAD, line_spacing=1.02)
    add_text(s, "Qué mira la audiencia, qué valora, y por qué no son lo mismo",
             MX, Inches(3.95), Inches(9.5), Inches(0.9), size=17, color=GRIS_CLARO,
             line_spacing=1.25)
    rect(s, MX, Inches(6.35), SW - 2 * MX, Pt(1), DIVISOR_OSCURO)
    meta = [
        ("Metodología", "CRISP-DM · Fases 1 a 6"),
        ("Alcance", f"{n(m['titulos_total'])} títulos · {m['anio_min']}–{m['anio_max']}"),
        ("Destinatario", "Dirección de Contenidos"),
        ("Asignatura", "ADY1104 Visualización de Datos"),
    ]
    colw = (SW - 2 * MX) // 4
    for i, (lab, val) in enumerate(meta):
        x = MX + colw * i
        add_richtext(s, x, Inches(6.55), colw - Inches(0.2), Inches(0.7), [
            {"runs": [(lab.upper(), {"size": 8, "bold": True, "color": GRIS_MED})],
             "space_after": 2},
            {"runs": [(val, {"size": 10.5, "color": BLANCO})], "line_spacing": 1.15},
        ])
    add_text(s, "1", Inches(12.55), Inches(7.08), Inches(0.35), Inches(0.3),
             size=9, color=GRIS_MED, align=PP_ALIGN.RIGHT)

    # ---------------- 2. El encargo ---------------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "El encargo")
    titulo(s, "La Dirección de Contenidos decide qué comprar, qué producir y qué "
              "promover. Hoy lo hace sin evidencia integrada.", size=22,
           top=Inches(0.82))
    colw = (SW - 2 * MX - Inches(0.5)) // 2
    lista_puntos(s, MX, Inches(2.35), colw, [
        ("El problema", "No existe una lectura que distinga el contenido que genera "
                        "tráfico del que genera satisfacción."),
        ("Por qué importa", "El tráfico sostiene el consumo del mes; la satisfacción "
                            "sostiene la renovación de la suscripción."),
        ("La pregunta", "¿Qué concentra la atención, qué concentra la valoración, y "
                        "qué decisiones se desprenden de la diferencia?"),
    ])
    x2 = MX + colw + Inches(0.5)
    add_tabla(s, x2, Inches(2.35), colw, Inches(1.7),
              ["Audiencia", "Qué decide"],
              [[("Dirección de Contenidos (principal)", {"bold": True}), "Qué adquirir, producir y renovar"],
               ["Comité ejecutivo", "Asignación de presupuesto"],
               ["Producto y curatoría", "Qué promover y ordenar el descubrimiento"]],
              col_widths=[int(colw * 0.42), int(colw * 0.58)], font_size=11)
    add_text(s, "El propósito no es describir el catálogo: es cambiar una decisión.",
             x2, Inches(4.35), colw, Inches(0.6), size=12, italic=True, color=GRIS,
             line_spacing=1.2)
    pie(s, 2)

    # ---------------- 3. Metodología --------------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Metodología")
    titulo(s, "CRISP-DM: la pregunta de negocio primero, los datos después")
    fases = [
        ("1 · Negocio", "Problema, audiencia y propósito comunicacional"),
        ("2 · Datos", "Perfilado y diagnóstico de calidad de ambas fuentes"),
        ("3 · Preparación", "Limpieza, armonización de taxonomías e integración"),
        ("4 · Análisis", "Exploración visual y segmentación por cuadrantes"),
        ("5 · Evaluación", "Revisión crítica de la validez de los hallazgos"),
        ("6 · Despliegue", "Dashboard, narrativa visual e informe ejecutivo"),
    ]
    add_tabla(s, MX, Inches(2.15), SW - 2 * MX, Inches(3.3),
              ["Fase", "Qué se hizo"],
              [[(f, {"bold": True}), q] for f, q in fases],
              col_widths=[Inches(2.6), Inches(9.0)], font_size=13, row_h=Inches(0.52))
    franja(s, [
        {"runs": [("El método es iterativo y lo usamos así: ", {"size": 14.5, "bold": True, "color": BLANCO}),
                  ("la fase 4 nos obligó a volver a la fase 3 al descubrir que películas y "
                   "series usaban taxonomías de género distintas.", {"size": 14.5, "color": BLANCO})],
         "line_spacing": 1.3}], top=Inches(6.05), height=Inches(0.85))
    pie(s, 3)

    # ---------------- 4. Comprensión de los datos --------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Comprensión de los datos")
    titulo(s, "Antes de analizar: qué nos permiten y qué no nos permiten decir "
              "estos datos", size=22)
    colw = (SW - 2 * MX - Inches(0.5)) // 2
    gigante(s, MX, Inches(2.3), colw,
            n(m["titulos_por_anio_formato"]),
            "títulos EXACTOS por cada año, en ambas fuentes. No es el catálogo: "
            "es una muestra estratificada.")
    add_richtext(s, MX, Inches(4.35), colw, Inches(1.3), [
        {"runs": [("Consecuencia: ", {"size": 13, "bold": True, "color": CARBON}),
                  ("el volumen anual es constante por diseño. Este análisis no puede "
                   "sostener ninguna conclusión sobre crecimiento del catálogo.",
                   {"size": 13, "color": CARBON})],
         "line_spacing": 1.3}])
    x2 = MX + colw + Inches(0.5)
    filas_calidad = [
        [f"{n(m['sin_calificar'])} títulos sin votos figuraban con calificación 0,0", "Convertidos a dato ausente"],
        [f"{d(m['budget_ceros_pct'], 1)}% de presupuestos en cero", "Tratados como faltantes"],
        ["“rating” idéntica a “vote_average”", "Eliminada"],
        ["“duration” nula o constante", "Eliminada"],
        ["Taxonomías de género divergentes", "Armonizadas"],
        [f"{m['series_id_duplicados']} identificadores duplicados", "Deduplicados"],
    ]
    add_tabla(s, x2, Inches(2.3), colw, Inches(3.6),
              ["Hallazgo de calidad", "Tratamiento"], filas_calidad,
              col_widths=[int(colw * 0.66), int(colw * 0.34)], font_size=10.5,
              row_h=Inches(0.5))
    pie(s, 4)

    # ---------------- 5. Contexto 1/2 --------------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Contexto · 1 de 2")
    titulo(s, "El catálogo está concentrado en géneros masivos")
    add_imagen_fit(s, "01_composicion_generos", MX, CONTENT_TOP, SW - 2 * MX,
                   CONTENT_BOTTOM - CONTENT_TOP)
    pie(s, 5)

    # ---------------- 6. Contexto 2/2 --------------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Contexto · 2 de 2")
    titulo(s, "Y su calidad mejora año a año. No hay un problema evidente.")
    add_imagen_fit(s, "06_evolucion_temporal", MX, CONTENT_TOP, SW - 2 * MX,
                   CONTENT_BOTTOM - CONTENT_TOP)
    pie(s, 6)

    # ---------------- 7. Tensión --------------------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Narrativa visual (Data Storytelling) · Tensión")
    titulo(s, "Pero la atención no se reparte: se concentra en una minoría", size=23)
    colw = Inches(3.7)
    gigante(s, MX, Inches(2.35), colw, f"{n(m['ratio_max_mediana'])}×",
            "El título más popular supera " + n(m["ratio_max_mediana"]) +
            " veces al título mediano.", valor_size=58)
    add_richtext(s, MX, Inches(4.25), colw, Inches(1.6), [
        {"runs": [("Solo ", {"size": 12.5, "color": CARBON}),
                  (f"{n(m['titulos_sobre_p99'])} títulos", {"size": 12.5, "bold": True, "color": CARBON}),
                  (" superan el percentil 99.", {"size": 12.5, "color": CARBON})],
         "space_after": 8, "line_spacing": 1.25},
        {"runs": [("La mayoría del catálogo vive con exposición marginal.",
                   {"size": 12.5, "color": CARBON})], "line_spacing": 1.25},
    ])
    add_imagen_fit(s, "03_distribucion_popularidad", MX + colw + Inches(0.4),
                   CONTENT_TOP, SW - MX - (MX + colw + Inches(0.4)),
                   CONTENT_BOTTOM - CONTENT_TOP)
    pie(s, 7)

    # ---------------- 8. El giro / hallazgo central --------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "El giro · Hallazgo central")
    titulo(s, "Lo más popular no es lo mejor evaluado")
    add_imagen_fit(s, "04_popularidad_vs_calidad", MX, Inches(1.85), SW - 2 * MX,
                   Inches(4.35))
    franja(s, [
        {"runs": [("Correlación de ", {"size": 14.5, "color": BLANCO}),
                  (d(m["correlacion_pop_calidad_peliculas"]), {"size": 14.5, "bold": True, "color": BLANCO}),
                  (" en películas y ", {"size": 14.5, "color": BLANCO}),
                  (d(m["correlacion_pop_calidad_series"]), {"size": 14.5, "bold": True, "color": BLANCO}),
                  (" en series. Saber cuán popular es un título ", {"size": 14.5, "color": BLANCO}),
                  ("no permite anticipar", {"size": 14.5, "bold": True, "color": BLANCO}),
                  (" cómo será calificado.", {"size": 14.5, "color": BLANCO})],
         "line_spacing": 1.3}], top=Inches(6.28), height=Inches(0.68))
    pie(s, 8)

    # ---------------- 9. Consecuencia operativa (4 cuadrantes) --------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Consecuencia operativa")
    titulo(s, "Ese hallazgo divide el catálogo en cuatro decisiones distintas")
    cw = (SW - 2 * MX - Inches(0.35)) // 2
    ch = Inches(2.25)
    top1, top2 = Inches(2.3), Inches(2.3) + ch + Inches(0.3)
    cuadro(s, MX, top1, cw, ch, "Calidad sin visibilidad", n(m["cuad_calidad_sin_visibilidad"]),
           [{"runs": [("Promover. ", {"size": 11, "bold": True, "color": CARBON}),
                      ("Máxima prioridad: contenido ya pagado que la audiencia valora, "
                       "pero que no está encontrando. Costo marginal cero.",
                       {"size": 11, "color": GRIS})], "line_spacing": 1.25}],
           color=VERDE)
    cuadro(s, MX + cw + Inches(0.35), top1, cw, ch, "Éxitos consolidados", n(m["cuad_exitos"]),
           [{"runs": [("Proteger. ", {"size": 11, "bold": True, "color": CARBON}),
                      ("Asegurar renovación de derechos y continuidad.",
                       {"size": 11, "color": GRIS})], "line_spacing": 1.25}],
           color=ROJO)
    cuadro(s, MX, top2, cw, ch, "Populares mal evaluados", n(m["cuad_populares_mal_evaluados"]),
           [{"runs": [("Vigilar. ", {"size": 11, "bold": True, "color": CARBON}),
                      ("Generan tráfico, pero erosionan la percepción de calidad.",
                       {"size": 11, "color": GRIS})], "line_spacing": 1.25}],
           color=NARANJA)
    cuadro(s, MX + cw + Inches(0.35), top2, cw, ch, "Bajo rendimiento", n(m["cuad_bajo_rendimiento"]),
           [{"runs": [("Revisar. ", {"size": 11, "bold": True, "color": CARBON}),
                      ("Candidatos naturales a depuración del catálogo.",
                       {"size": 11, "color": GRIS})], "line_spacing": 1.25}],
           color=GRIS)
    pie(s, 9)

    # ---------------- 10. Oportunidad género --------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Dónde está la oportunidad · 1 de 2")
    titulo(s, "Los géneros mejor evaluados son los menos representados", size=23)
    imgw = Inches(7.1)
    add_imagen_fit(s, "05_generos_calidad_volumen", MX, CONTENT_TOP, imgw,
                   CONTENT_BOTTOM - CONTENT_TOP)
    x2 = MX + imgw + Inches(0.35)
    colw = SW - MX - x2
    add_tabla(s, x2, CONTENT_TOP, colw, Inches(2.4),
              ["Género", "Títulos", "Calif."],
              [[g["genero"], n(g["titulos"]), d(g["calificacion"])] for g in go[:5]],
              col_widths=[int(colw * 0.5), int(colw * 0.25), int(colw * 0.25)],
              align_right={1, 2}, font_size=11, row_h=Inches(0.42))
    add_text(s, "Calidad sobre la mediana, oferta por debajo de ella. En el extremo "
                f"opuesto, {gb[0]['genero']} ({d(gb[0]['calificacion'])}) y "
                f"{gb[1]['genero']} ({d(gb[1]['calificacion'])}) suman "
                f"{n(gb[0]['titulos'] + gb[1]['titulos'])} títulos con las peores "
                "calificaciones.", x2, Inches(4.75), colw, Inches(1.9), size=11,
             color=GRIS, line_spacing=1.3)
    pie(s, 10)

    # ---------------- 11. Oportunidad mercado -------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Dónde está la oportunidad · 2 de 2")
    titulo(s, "El inglés domina el catálogo, pero no la calidad percibida", size=23)
    imgw = Inches(7.1)
    add_imagen_fit(s, "07_mercados_idiomas", MX, CONTENT_TOP, imgw,
                   CONTENT_BOTTOM - CONTENT_TOP)
    x2 = MX + imgw + Inches(0.35)
    colw = SW - MX - x2
    cifra(s, x2, CONTENT_TOP, colw, f"{d(m['ingles_pct_catalogo'], 1)}%",
          "del catálogo calificado está en inglés…", color=CARBON, valor_size=26)
    cifra(s, x2, CONTENT_TOP + Inches(1.0), colw,
          f"{m['ingles_posicion']}º de {m['mercados_analizados']}",
          "…pero ocupa ese lugar en calificación promedio", color=NARANJA,
          valor_size=24)
    add_tabla(s, x2, CONTENT_TOP + Inches(2.15), colw, Inches(1.3),
              ["Mercado", "Títulos", "Calif."],
              [[x["idioma"], n(x["titulos"]), d(x["calificacion"])] for x in mt],
              col_widths=[int(colw * 0.44), int(colw * 0.28), int(colw * 0.28)],
              align_right={1, 2}, font_size=10.5, row_h=Inches(0.4))
    pie(s, 11)

    # ---------------- 12. Riesgo comercial ----------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Riesgo comercial")
    titulo(s, "El riesgo no está en las apuestas grandes: está en el tramo medio",
           size=22)
    imgw = Inches(7.6)
    add_imagen_fit(s, "10_rentabilidad_escala", MX, CONTENT_TOP, imgw,
                   CONTENT_BOTTOM - CONTENT_TOP)
    x2 = MX + imgw + Inches(0.4)
    colw = SW - MX - x2
    add_richtext(s, x2, CONTENT_TOP + Inches(0.1), colw, Inches(3.4), [
        {"runs": [("Contra la intuición: ", {"size": 13, "bold": True, "color": CARBON}),
                  ("la tasa de éxito comercial ", {"size": 13, "color": CARBON}),
                  ("crece", {"size": 13, "bold": True, "color": CARBON}),
                  (" con la escala de inversión.", {"size": 13, "color": CARBON})],
         "space_after": 12, "line_spacing": 1.3},
        {"runs": [(f"El peor desempeño está en el tramo medio "
                   f"({d(peor['pct_rentables'], 1)}%), por debajo incluso de las "
                   "producciones de bajo presupuesto — y es donde se concentra el "
                   f"mayor número de películas ({n(peor['peliculas'])}).",
                   {"size": 13, "color": CARBON})], "line_spacing": 1.3, "space_after": 16},
        {"runs": [("Cautela: ", {"size": 10.5, "bold": True, "color": GRIS}),
                  (f"solo {d(m['peliculas_con_finanzas_pct'], 1)}% de las películas "
                   "informa datos financieros. Lectura indicativa.",
                   {"size": 10.5, "color": GRIS})], "line_spacing": 1.3},
    ])
    pie(s, 12)

    # ---------------- 13. La herramienta (dashboard) ------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "La herramienta")
    titulo(s, "Un dashboard para verificar y explorar, sin depender del equipo "
              "analítico", size=22)
    colw = (SW - 2 * MX - Inches(0.5)) // 2
    lista_puntos(s, MX, Inches(2.3), colw, [
        ("Indicadores", "Cuatro KPI que se recalculan con cada filtro, cada uno "
                        "declarando sobre qué base se calcula."),
        ("Filtros cruzados", "Formato, género, idioma, año desde y calificación "
                             "mínima, aplicables de forma simultánea."),
        ("Navegación", "Cuatro pestañas temáticas; los filtros persisten al "
                       "cambiar de vista."),
        ("Interacción", "Detalle al pasar el cursor, zoom en las dispersiones y "
                        "aviso explícito cuando una combinación no arroja datos "
                        "suficientes."),
    ])
    x2 = MX + colw + Inches(0.5)
    tarjeta_texto(s, x2, Inches(2.3), colw, Inches(2.55), "Decisión técnica: HTML autocontenido", [
        {"runs": [("Se evaluaron Power BI, Tableau, Streamlit y Dash. Se optó por un "
                   "archivo HTML único con Plotly porque es el ", {"size": 11.5, "color": GRIS}),
                  ("único formato que cualquier destinatario puede abrir sin licencia, "
                   "sin instalación y sin levantar un servidor", {"size": 11.5, "bold": True, "color": CARBON}),
                  (f". Los {n(m['registros_dashboard'])} registros se embeben en el "
                   "archivo: el filtrado ocurre en el navegador y funciona sin conexión.",
                   {"size": 11.5, "color": GRIS})], "line_spacing": 1.3}])
    add_richtext(s, x2, Inches(5.1), colw, Inches(1.5), [
        {"runs": [("Todo el proyecto se construyó en Python: ", {"size": 11.5, "color": GRIS}),
                  ("Matplotlib", {"size": 11.5, "bold": True, "color": CARBON}),
                  (" para las 12 figuras estáticas del informe y ", {"size": 11.5, "color": GRIS}),
                  ("Plotly", {"size": 11.5, "bold": True, "color": CARBON}),
                  (" para este dashboard, ambos gobernados por el mismo módulo de estilo: "
                   "quien pasa del documento al tablero reconoce los mismos gráficos, "
                   "ahora explorables.", {"size": 11.5, "color": GRIS})], "line_spacing": 1.3},
    ])
    pie(s, 13)

    # ---------------- 14. Evaluación crítica --------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Evaluación crítica")
    titulo(s, "Qué sostiene esta solución y qué no puede afirmar")
    colw = (SW - 2 * MX - Inches(0.5)) // 2
    add_text(s, "Fortalezas", MX, Inches(2.1), colw, Inches(0.4), size=15, bold=True,
             color=VERDE, font=HEAD)
    lista_puntos(s, MX, Inches(2.62), colw, [
        ("Hallazgo robusto", f"Se sostiene sobre {n(m['evaluables'])} títulos y se "
                            "mantiene al segmentar por formato, género y año."),
        ("Trazabilidad completa", "Reproducible desde los archivos originales; las "
                                  "cifras se generan, no se transcriben."),
        ("Calidad de datos explícita", "Ocho problemas detectados y documentados "
                                       "antes de analizar."),
    ], size=11.5)
    x2 = MX + colw + Inches(0.5)
    add_text(s, "Limitaciones", x2, Inches(2.1), colw, Inches(0.4), size=15, bold=True,
             color=NARANJA, font=HEAD)
    lista_puntos(s, x2, Inches(2.62), colw, [
        ("Sin datos de usuarios", "No hay reproducciones, suscripciones ni "
                                  "cancelaciones: no podemos medir retención ni "
                                  "engagement reales. Usamos popularidad como "
                                  "aproximación de atención."),
        ("Cobertura financiera parcial", f"Solo {d(m['peliculas_con_finanzas_pct'], 1)}%"
                                        " de las películas informa presupuesto e "
                                        "ingresos, probablemente las de mayor "
                                        "circulación."),
        ("Calificaciones externas", "Provienen de una comunidad que no equivale a "
                                    "la base de suscriptores."),
        ("El umbral de votos sesga la muestra", f"Lo supera el "
                                                f"{d(m['pct_supera_umbral_peliculas'], 1)}% de las "
                                                f"películas pero solo el {d(m['pct_supera_umbral_series'], 1)}%"
                                                " de las series."),
    ], size=11.5)
    pie(s, 14)

    # ---------------- 15. Tres palancas comerciales -------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "De hallazgos a decisiones comerciales")
    titulo(s, "Tres palancas para atraer y retener, sin tocar presupuesto de "
              "contenido", size=21)
    cw = (SW - 2 * MX - Inches(0.7)) // 3
    ch = Inches(3.9)
    top = Inches(2.15)
    cuadro(s, MX, top, cw, ch, "1 · Joyas Ocultas", n(m["cuad_calidad_sin_visibilidad"]), [
        {"runs": [("Hallazgo: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("títulos ya en catálogo, bien evaluados, con baja visibilidad.",
                   {"size": 10.5, "color": GRIS})], "space_after": 6, "line_spacing": 1.25},
        {"runs": [("Atracción: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("marketing editorial de nicho.", {"size": 10.5, "color": GRIS})],
         "space_after": 6, "line_spacing": 1.25},
        {"runs": [("Retención: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("fila fija de descubrimiento.", {"size": 10.5, "color": GRIS})],
         "space_after": 6, "line_spacing": 1.25},
        {"runs": [("KPI: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("% de usuarios que los consumen al mes.", {"size": 10.5, "color": GRIS})],
         "line_spacing": 1.25},
    ], color=VERDE, valor_size=32)
    cuadro(s, MX + cw + Inches(0.35), top, cw, ch, "2 · Momentum por Género",
           f"+{d(m['momentum_top_generos'][0]['variacion_pct'], 0)}%", [
        {"runs": [("Hallazgo: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("rotación real de interés entre géneros (no crecimiento agregado).",
                   {"size": 10.5, "color": GRIS})], "space_after": 6, "line_spacing": 1.25},
        {"runs": [("Atracción: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("campañas segmentadas por género en alza.", {"size": 10.5, "color": GRIS})],
         "space_after": 6, "line_spacing": 1.25},
        {"runs": [("Retención: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("onboarding anclado al género de entrada.", {"size": 10.5, "color": GRIS})],
         "space_after": 6, "line_spacing": 1.25},
        {"runs": [("KPI: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("variación trimestral de popularidad por género.", {"size": 10.5, "color": GRIS})],
         "line_spacing": 1.25},
    ], color=ROJO, valor_size=32)
    cuadro(s, MX + 2 * (cw + Inches(0.35)), top, cw, ch, "3 · Series como Ancla",
           f"+{d(m['brecha_series_peliculas_controlada'])}", [
        {"runs": [("Hallazgo: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("ventaja estructural de series sobre películas, 16 años sin excepción.",
                   {"size": 10.5, "color": GRIS})], "space_after": 6, "line_spacing": 1.25},
        {"runs": [("Atracción: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("primer episodio gratuito.", {"size": 10.5, "color": GRIS})],
         "space_after": 6, "line_spacing": 1.25},
        {"runs": [("Retención: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("hábito de consumo episódico.", {"size": 10.5, "color": GRIS})],
         "space_after": 6, "line_spacing": 1.25},
        {"runs": [("KPI: ", {"size": 10.5, "bold": True, "color": CARBON}),
                  ("retorno semanal y episodios en 7 días.", {"size": 10.5, "color": GRIS})],
         "line_spacing": 1.25},
    ], color=AZUL, valor_size=32)
    add_text(s, "Ninguna propuesta usa variables financieras: las tres se apoyan solo "
                "en popularidad, calificación, votos, género, formato y año — las "
                "mismas variables que sostienen el resto de este análisis.",
             MX, top + ch + Inches(0.25), SW - 2 * MX, Inches(0.5), size=10.5,
             color=GRIS, line_spacing=1.25)
    pie(s, 15)

    # ---------------- 16. Programa Joyas Ocultas (foco) ---------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Propuesta prioritaria")
    titulo(s, "Programa Joyas Ocultas: el contenido ya está pagado, falta "
              "exponerlo", size=22)
    imgw = Inches(7.5)
    add_imagen_fit(s, "11_joyas_ocultas", MX, CONTENT_TOP, imgw,
                   CONTENT_BOTTOM - CONTENT_TOP)
    x2 = MX + imgw + Inches(0.35)
    colw = SW - MX - x2
    cifra(s, x2, CONTENT_TOP, colw, f"{d(m['pct_calidad_sin_visibilidad'], 1)}%",
          f"del catálogo evaluable: {n(m['cuad_calidad_sin_visibilidad_peliculas'])} "
          f"películas y {n(m['cuad_calidad_sin_visibilidad_series'])} series",
          color=VERDE, valor_size=28)
    add_richtext(s, x2, CONTENT_TOP + Inches(1.05), colw, Inches(1.0), [
        {"runs": [("Califican en promedio ", {"size": 10.5, "color": CARBON}),
                  (d(m["joyas_calificacion_media_peliculas"]), {"size": 10.5, "bold": True, "color": CARBON}),
                  (" (películas) y ", {"size": 10.5, "color": CARBON}),
                  (d(m["joyas_calificacion_media_series"]), {"size": 10.5, "bold": True, "color": CARBON}),
                  (" (series) — por encima del resto del catálogo evaluable "
                   f"({d(m['resto_calificacion_media_peliculas'])} y "
                   f"{d(m['resto_calificacion_media_series'])}).",
                   {"size": 10.5, "color": CARBON})], "line_spacing": 1.3},
    ])
    joyas_ej = m["joyas_ejemplos"][:4]
    add_tabla(s, x2, CONTENT_TOP + Inches(2.15), colw, Inches(1.6),
              ["Ejemplo", "Formato", "Calif."],
              [[acortar(e["title"]), e["tipo"], d(e["calificacion"])] for e in joyas_ej],
              col_widths=[int(colw * 0.58), int(colw * 0.24), int(colw * 0.18)],
              align_right={2}, font_size=9.5, row_h=Inches(0.4))
    add_text(s, "Costo de adquisición de contenido: cero. La palanca es exposición, "
                "no compra.", x2, Inches(6.55), colw, Inches(0.4), size=10,
             color=GRIS, italic=True, line_spacing=1.2)
    pie(s, 16)

    # ---------------- 17. Recomendaciones -----------------------------------
    s = nueva_diapositiva(prs)
    eyebrow(s, "Recomendaciones")
    titulo(s, "Cinco decisiones, ordenadas por costo de implementación")
    filas_rec = [
        ["1", ("Activar la calidad sin visibilidad", {"bold": True}),
         f"{n(m['cuad_calidad_sin_visibilidad'])} títulos bien evaluados sin exposición: contenido ya pagado",
         ("Marginal cero", {"bold": True, "color": VERDE})],
        ["2", ("Rebalancear la adquisición", {"bold": True}),
         f"Géneros como {go[0]['genero'].lower()} y mercados como el {mt[0]['idioma'].lower()}: alta valoración, baja presencia",
         "Medio"],
        ["3", ("Reforzar el formato serie", {"bold": True}),
         f"Ventaja de {d(m['brecha_series_peliculas'])} puntos sostenida {m['anios_series_sobre_peliculas']} años sin excepción",
         "Alto"],
        ["4", ("Revisar el tramo medio de inversión", {"bold": True}),
         f"{d(peor['pct_rentables'], 1)}% de éxito frente a {d(mejor['pct_rentables'], 1)}% en el tramo muy alto",
         "Reasignación"],
        ["5", ("Incorporar datos de usuario", {"bold": True}),
         "Permitiría medir el efecto real sobre la retención", "Proyecto"],
    ]
    add_tabla(s, MX, Inches(2.05), SW - 2 * MX, Inches(4.2),
              ["#", "Recomendación", "Fundamento", "Costo"], filas_rec,
              col_widths=[Inches(0.5), Inches(2.9), Inches(6.8), Inches(1.9)],
              font_size=12, row_h=Inches(0.72))
    pie(s, 17)

    # ---------------- 18. Cierre ---------------------------------------------
    s = nueva_diapositiva(prs, dark=True)
    eyebrow(s, "Conclusión")
    add_text(s, "StreamView Analytics no tiene un problema de catálogo.\n"
                "Tiene un problema de visibilidad.", MX, Inches(2.2), Inches(11.8),
             Inches(2.0), size=32, bold=True, color=BLANCO, font=HEAD,
             line_spacing=1.15)
    add_text(s, "El contenido que su audiencia mejor valora ya está comprado. "
                "Solo no se está mostrando.", MX, Inches(4.05), Inches(10.5),
             Inches(1.0), size=15, color=GRIS_CLARO, line_spacing=1.35)
    add_text(s, "De todas las palancas examinadas, cerrar esa brecha es la de "
                "menor costo y mayor retorno esperado.", MX, Inches(4.85),
             Inches(10.5), Inches(0.7), size=13, color=GRIS_MED, line_spacing=1.3)
    add_richtext(s, MX, Inches(5.85), Inches(11), Inches(0.7), [
        {"runs": [("Esta narrativa se sostuvo en tres canales: ", {"size": 10, "color": GRIS}),
                  ("oral", {"size": 10, "bold": True, "color": GRIS_CLARO}),
                  (" durante la defensa, ", {"size": 10, "color": GRIS}),
                  ("escrita", {"size": 10, "bold": True, "color": GRIS_CLARO}),
                  (" en el informe ejecutivo, y ", {"size": 10, "color": GRIS}),
                  ("visual", {"size": 10, "bold": True, "color": GRIS_CLARO}),
                  (" en estas diapositivas y en el dashboard interactivo.",
                   {"size": 10, "color": GRIS})], "line_spacing": 1.3},
    ])
    pie(s, 18, dark=True)

    # ---------------- Guion de defensa (notas del orador) -------------------
    # Se agrega como notas de PowerPoint (Vista de moderador) para que el
    # guion viaje siempre junto a las diapositivas que respalda. Los tiempos
    # son orientativos para calzar en los 10 minutos de exposicion del EP2.
    guion = [
        "(~20 s) Buenos días/tardes. Somos el equipo consultor a cargo de "
        f"Inteligencia de Catálogo para StreamView Analytics, una plataforma de "
        f"streaming que necesita entender su catálogo de {n(m['titulos_total'])} "
        f"títulos, entre {m['anio_min']} y {m['anio_max']}, para tomar mejores "
        "decisiones de contenido. Trabajamos bajo metodología CRISP-DM y nuestro "
        "destinatario principal es la Dirección de Contenidos.",

        "(~40 s) El problema que nos encargaron no es de falta de datos: es de "
        "falta de una lectura integrada. Hoy StreamView no distingue entre el "
        "contenido que genera tráfico y el que genera satisfacción real — y eso "
        "importa, porque el tráfico sostiene el consumo del mes, pero la "
        "satisfacción sostiene la renovación de la suscripción. La pregunta que "
        "guía todo nuestro trabajo es: ¿qué concentra la atención, qué concentra "
        "la valoración, y qué decisiones se desprenden de esa diferencia? "
        "Diseñamos la solución para tres audiencias: la Dirección de Contenidos, "
        "que decide qué adquirir y producir; el comité ejecutivo, que asigna "
        "presupuesto; y el equipo de producto, que decide qué promover.",

        "(~30 s) Trabajamos con CRISP-DM, las seis fases clásicas de minería de "
        "datos. Quiero destacar algo: el método fue realmente iterativo. En la "
        "fase de análisis descubrimos que películas y series usaban taxonomías "
        "de género distintas, y tuvimos que volver a la fase de preparación "
        "para armonizarlas antes de seguir.",

        "(~40 s) Antes de sacar cualquier conclusión hicimos un diagnóstico "
        "riguroso de los datos, y encontramos algo clave: ambas fuentes tienen "
        f"exactamente {n(m['titulos_por_anio_formato'])} títulos por año, sin "
        "excepción. Eso no es el catálogo real: es una muestra estratificada, "
        "así que nunca vamos a decir que el catálogo 'creció', porque el diseño "
        "del muestreo lo impide. También corregimos calificaciones en cero que "
        "en realidad eran ausencia de votos, columnas redundantes, y "
        "armonizamos las taxonomías de género entre ambos formatos.",

        "(~25 s) Partimos por entender la composición del catálogo. Drama y "
        "Comedia concentran la oferta, tanto en películas como en series: es "
        "una apuesta bastante concentrada en géneros masivos.",

        "(~25 s) Y en cuanto a calidad, la noticia es buena: mejora "
        "sostenidamente año a año en ambos formatos. No hay, a priori, un "
        "problema de calidad del contenido.",

        "(~35 s) Pero aquí aparece la primera tensión del relato: la atención "
        "de la audiencia no se reparte parejo, se concentra en muy pocos "
        f"títulos. El título más popular supera {n(m['ratio_max_mediana'])} veces "
        f"al título mediano, y solo {n(m['titulos_sobre_p99'])} títulos superan "
        "el percentil 99. La inmensa mayoría del catálogo vive con una "
        "exposición marginal.",

        "(~45 s) Y acá viene el giro de toda nuestra narrativa: si la atención "
        "se concentra en pocos títulos, uno esperaría que al menos esos "
        "títulos sean los mejor evaluados. No es así. Calculamos la "
        "correlación entre popularidad y calificación por separado en cada "
        "formato, porque el índice de popularidad no es comparable entre "
        f"películas y series. El resultado: {d(m['correlacion_pop_calidad_peliculas'])} "
        f"en películas, {d(m['correlacion_pop_calidad_series'])} en series. "
        "Prácticamente cero. Saber que un título es popular no nos dice nada "
        "sobre si es bueno. Esto divide el catálogo en cuatro cuadrantes de "
        "decisión.",

        "(~40 s) Esos cuatro cuadrantes son accionables: los éxitos "
        f"consolidados, {n(m['cuad_exitos'])} títulos, hay que protegerlos. Los "
        f"populares mal evaluados, {n(m['cuad_populares_mal_evaluados'])} "
        "títulos, hay que vigilarlos porque generan tráfico pero erosionan la "
        "percepción de calidad. Los de bajo rendimiento son candidatos a "
        "depuración. Y el cuadrante que más nos importa: calidad sin "
        f"visibilidad, {n(m['cuad_calidad_sin_visibilidad'])} títulos. Es "
        "contenido que la audiencia valora, pero que hoy no está encontrando. "
        "Ese va a ser el corazón de nuestra propuesta comercial.",

        "(~30 s) Si miramos por género, el patrón se repite: los géneros mejor "
        "evaluados —documental, infantil, musical— son justamente los menos "
        "representados en el catálogo. En el extremo opuesto, terror y "
        f"suspenso concentran casi {n(gb[0]['titulos']+gb[1]['titulos'])} "
        "títulos con las peores calificaciones.",

        "(~30 s) Lo mismo pasa con los mercados de origen. El inglés concentra "
        f"casi la mitad del catálogo calificado, un {d(m['ingles_pct_catalogo'],0)}%, "
        f"pero ocupa el lugar {m['ingles_posicion']} de {m['mercados_analizados']} "
        "en calificación promedio. Hay mercados como el japonés o el chino que "
        "rinden mejor y están subrepresentados.",

        "(~35 s) En lo financiero encontramos algo contraintuitivo: la tasa de "
        "éxito comercial efectivamente crece con la escala de inversión, pero "
        "el peor desempeño no está en las apuestas chicas, está en el tramo "
        f"medio de presupuesto: solo {d(peor['pct_rentables'],1)}% de éxito, por "
        "debajo incluso del tramo bajo. Y es justamente donde se concentra el "
        f"mayor número de películas, {n(peor['peliculas'])}.",

        "(~35 s) Todo este análisis lo hicimos explorable en un dashboard "
        "interactivo, construido en Python con Plotly. Tiene KPIs que se "
        "recalculan en vivo, cinco filtros cruzados, cuatro pestañas de "
        "navegación e interacción completa. Lo construimos en HTML "
        "autocontenido a propósito: para que cualquier persona en la "
        "organización lo pueda abrir sin instalar nada.",

        "(~35 s) Somos igual de rigurosos con nuestras propias limitaciones. "
        "La principal: no tenemos datos de comportamiento real de usuarios, ni "
        "reproducciones, ni suscripciones, ni cancelaciones. Usamos "
        "popularidad como aproximación de atención, pero no podemos medir "
        "retención real. Eso condiciona cómo hay que leer nuestras "
        "recomendaciones.",

        "(~30 s) A partir de estos hallazgos proponemos tres palancas "
        "comerciales concretas, ninguna basada en variables financieras: "
        "Joyas Ocultas, Momentum por Género, y Series como Ancla de "
        "suscripción. Cada una con su mecanismo de atracción, de retención, y "
        "su KPI.",

        "(~40 s) Nos detenemos en la primera porque es la más importante: "
        f"Programa Joyas Ocultas. Son {n(m['cuad_calidad_sin_visibilidad'])} "
        "títulos que ya están en el catálogo, ya pagados, con calificaciones "
        f"de {d(m['joyas_calificacion_media_peliculas'])} en películas y "
        f"{d(m['joyas_calificacion_media_series'])} en series, por encima del "
        "resto del catálogo. La propuesta es simple: exponerlos mejor en el "
        "descubrimiento, con una fila editorial dedicada. El costo de "
        "adquisición de contenido es cero. La palanca es exposición, no "
        "compra.",

        "(~30 s) Cerramos con cinco recomendaciones priorizadas por costo de "
        "implementación: desde activar la calidad sin visibilidad —costo "
        "marginal cero— hasta incorporar datos de usuario a futuro, que es la "
        "recomendación de mayor alcance pero también la de mayor inversión.",

        "(~25 s) Y la conclusión que queremos dejarles es esta: StreamView "
        "Analytics no tiene un problema de catálogo, tiene un problema de "
        "visibilidad. El contenido que su audiencia mejor valora ya está "
        "comprado. Solo no se está mostrando. Muchas gracias, quedamos atentos "
        "a sus preguntas.",
    ]
    for slide, texto in zip(prs.slides, guion):
        notas(slide, texto)

    OUT.mkdir(parents=True, exist_ok=True)
    salida = OUT / "presentacion_ejecutiva.pptx"
    n_slides = len(prs.slides)
    prs.save(str(salida))
    print(f"{salida}  ({salida.stat().st_size/1024/1024:.1f} MB)  ·  {n_slides} diapositivas")


if __name__ == "__main__":
    main()
