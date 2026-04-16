from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt
from docx.oxml.ns import qn

LOGO_PATH = Path("img/logo.png")

MARGEN_SUPERIOR = Cm(1.40)
MARGEN_INFERIOR = Cm(0.11)
MARGEN_IZQUIERDO = Cm(2.75)
MARGEN_DERECHO = Cm(2.93)

FUENTE_NOMBRE = "Bookman Old Style"
FUENTE_TAMANIO_NORMAL = Pt(9)
FUENTE_TAMANIO_LEMA = Pt(7)

ANCHO_COLUMNA_LOGO = Cm(5.6)
ANCHO_COLUMNA_LEMA = Cm(11.4)
ANCHO_LOGO = Cm(4.2)

LEMA_1 = '"Decenio de la igualdad de oportunidades para mujeres y hombres"'
LEMA_2 = '"Año de la Esperanza y el Fortalecimiento de la Democracia"'

PIE_LINEA_1 = "Unidad de Gestión Educativa Local Tacna - Asociación Los Begoñas Mz. I, Lt. 02-A"
PIE_LINEA_2 = "Distrito Gregorio Albarracín Lanchipa"
PIE_LINEA_3 = "Web: www.ugeltacna.edu.pe"
PIE_LINEA_4 = "Tacna - Perú"


def configurar_documento(doc):
    """Configura márgenes y fuente base del documento."""
    seccion = doc.sections[0]
    seccion.top_margin = MARGEN_SUPERIOR
    seccion.bottom_margin = MARGEN_INFERIOR
    seccion.left_margin = MARGEN_IZQUIERDO
    seccion.right_margin = MARGEN_DERECHO

    estilo = doc.styles["Normal"]
    estilo.font.name = FUENTE_NOMBRE
    estilo._element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE_NOMBRE)
    estilo.font.size = FUENTE_TAMANIO_NORMAL

