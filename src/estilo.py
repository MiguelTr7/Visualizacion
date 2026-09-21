"""
StreamView Analytics - Estandar visual del proyecto.

Centraliza paleta, tipografia y reglas de diseno para que todas las
visualizaciones del informe y del dashboard sean coherentes entre si.

Criterios aplicados (percepcion visual):
- Un unico color de acento (ROJO) reservado para el dato protagonista de
  cada grafico; el resto en grises para no competir por la atencion.
- Paleta categorica segura para daltonismo (basada en Okabe-Ito).
- Eliminacion de chartjunk: sin bordes superiores/derechos, sin rejilla
  vertical, sin efectos 3D, sin leyendas cuando es posible etiquetar directo.
"""
import matplotlib.pyplot as plt
import matplotlib as mpl

ROJO = "#E50914"       # acento: el dato que importa
CARBON = "#221F1F"     # texto principal
GRIS = "#B3B3B3"       # datos de contexto
GRIS_CLARO = "#E8E8E8" # rejilla y fondos
AZUL = "#0072B2"       # segunda serie
NARANJA = "#E69F00"    # tercera serie
VERDE = "#009E73"      # positivo

TIPO_COLOR = {"Película": ROJO, "Serie": AZUL}


def miles(valor):
    """Formato numerico en convencion espanola: 12345 -> '12.345'."""
    return f"{int(round(valor)):,}".replace(",", ".")


def decimal(valor, cifras=2):
    """Formato decimal en convencion espanola: 7.48 -> '7,48'."""
    return f"{valor:.{cifras}f}".replace(".", ",")


def aplicar_estilo():
    mpl.rcParams.update({
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": GRIS,
        "axes.labelcolor": CARBON,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.titlecolor": CARBON,
        "axes.titlelocation": "left",
        "axes.titlepad": 14,
        "axes.labelsize": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRIS_CLARO,
        "grid.linewidth": 0.8,
        "xtick.color": CARBON,
        "ytick.color": CARBON,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "text.color": CARBON,
        "legend.frameon": False,
        "legend.fontsize": 10,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
    })


def titular(ax, titulo, subtitulo=None):
    """Titulo que afirma el hallazgo + subtitulo que da el detalle tecnico."""
    ax.set_title(titulo, pad=26 if subtitulo else 14)
    if subtitulo:
        ax.text(0, 1.02, subtitulo, transform=ax.transAxes,
                fontsize=10.5, color="#6B6B6B", va="bottom")


def fuente(fig, texto=("Fuente: catálogo Netflix 2010-2025 · muestra estratificada "
                       "de 1.000 títulos por año y formato")):
    fig.text(0.005, -0.02, texto, fontsize=8.5, color="#8A8A8A", ha="left")


def solo_eje_x(ax):
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)


def solo_eje_y(ax):
    ax.grid(axis="x", visible=False)
    ax.grid(axis="y", visible=True)
