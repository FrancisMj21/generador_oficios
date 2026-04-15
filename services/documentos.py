from datetime import datetime
from pathlib import Path
from zipfile import ZipFile
import zipfile

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.exceptions import PackageNotFoundError
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from config import GENERATED_DIR, TEMPLATES_DOCX_DIR
from services.personas import actualizar_estado_generado
from utils.texto import normalizar_texto, slugify


def nombre_archivo_oficio(persona):
    return f"oficio_{persona['id']}_{slugify(persona.get('nombre'))}.docx"


def ruta_archivo_generado(persona):
    return GENERATED_DIR / nombre_archivo_oficio(persona)


def obtener_lineas_periodos(persona):
    periodos = normalizar_texto(persona.get("periodos"))
    if not periodos:
        return []
    return [linea.strip() for linea in periodos.splitlines() if linea.strip()]


def obtener_fecha_actual():
    meses = {
        1: "enero",
        2: "febrero",
        3: "marzo",
        4: "abril",
        5: "mayo",
        6: "junio",
        7: "julio",
        8: "agosto",
        9: "septiembre",
        10: "octubre",
        11: "noviembre",
        12: "diciembre",
    }
    ahora = datetime.now()
    return f"{ahora.day} de {meses[ahora.month]} de {ahora.year}"


def numero_oficio(persona):
    return ""


def tipo_template(persona):
    return "docente.docx"


def plantilla_disponible(persona):
    candidate = TEMPLATES_DOCX_DIR / tipo_template(persona)
    if candidate.exists() and candidate.stat().st_size > 0:
        return candidate

    fallback = TEMPLATES_DOCX_DIR / "docente.docx"
    if fallback.exists() and fallback.stat().st_size > 0:
        return fallback

    return None


def plantilla_es_docx_valida(ruta_plantilla):
    if not ruta_plantilla or not ruta_plantilla.exists():
        return False

    if not zipfile.is_zipfile(ruta_plantilla):
        return False

    try:
        with ZipFile(ruta_plantilla) as archivo_zip:
            nombres = set(archivo_zip.namelist())
            return "[Content_Types].xml" in nombres and "word/document.xml" in nombres
    except (OSError, ValueError, KeyError):
        return False


def reemplazar_en_parrafos(parrafos, reemplazos):
    for parrafo in parrafos:
        texto = parrafo.text
        nuevo = texto
        for origen, destino in reemplazos.items():
            if origen in nuevo:
                nuevo = nuevo.replace(origen, destino)
        if nuevo != texto:
            for run in parrafo.runs:
                run.text = ""
            if parrafo.runs:
                parrafo.runs[0].text = nuevo
            else:
                parrafo.add_run(nuevo)


def reemplazar_en_tablas(tablas, reemplazos):
    for tabla in tablas:
        for fila in tabla.rows:
            for celda in fila.cells:
                reemplazar_en_parrafos(celda.paragraphs, reemplazos)
                reemplazar_en_tablas(celda.tables, reemplazos)


def aplicar_reemplazos(documento, reemplazos):
    reemplazar_en_parrafos(documento.paragraphs, reemplazos)
    reemplazar_en_tablas(documento.tables, reemplazos)

    for section in documento.sections:
        reemplazar_en_parrafos(section.header.paragraphs, reemplazos)
        reemplazar_en_tablas(section.header.tables, reemplazos)
        reemplazar_en_parrafos(section.footer.paragraphs, reemplazos)
        reemplazar_en_tablas(section.footer.tables, reemplazos)


def obtener_tratamiento(persona):
    sexo = normalizar_texto(persona.get("sexo")).lower()
    return "SEÑORA" if sexo == "femenino" else "SEÑOR"


def construir_reemplazos(persona):
    nombre = normalizar_texto(persona.get("nombre")).upper()
    condicion = normalizar_texto(persona.get("condicion")).upper()
    cargo_actual = normalizar_texto(persona.get("cargo_actual"))
    if not cargo_actual:
        tipo = normalizar_texto(persona.get("tipo_persona")).upper()
        cargo_actual = f"{tipo} {condicion}".strip()

    centro = normalizar_texto(persona.get("centro_trabajo")).upper()
    direccion = normalizar_texto(persona.get("direccion"))
    provincia = normalizar_texto(persona.get("provincia")) or "TACNA"
    telefono = normalizar_texto(persona.get("telefono"))
    correo = normalizar_texto(persona.get("correo"))
    solicita = normalizar_texto(persona.get("solicita"))
    tratamiento = obtener_tratamiento(persona)
    fecha = obtener_fecha_actual()
    return {
        "{{FECHA}}": fecha,
        "{{OFICIO}}": "",
        "{{NOMBRE}}": nombre,
        "{{CARGO}}": cargo_actual.upper(),
        "{{CENTRO_TRABAJO}}": centro,
        "{{DIRECCION}}": direccion,
        "{{PROVINCIA}}": provincia,
        "{{TELEFONO}}": telefono,
        "{{CORREO}}": correo,
        "{{SOLICITA}}": solicita,
        "{{TRATAMIENTO}}": tratamiento,
        "Tacna, ": f"Tacna, {fecha}",
        "KARINA PAREDES NINAJA": nombre,
        "PROFESOR NOMBRADO": cargo_actual.upper(),
        "I.E. JUAN VELASCO ALVARADO": centro,
        "DIRECCION: CPM Leguia Mz 28 Lte 15.": f"DIRECCION: {direccion}.",
        "Tacna/Tacna/Tacna": f"{provincia}/{provincia}/{provincia}",
        "995968988": telefono,
        "karinaparedes529@gmail.com": correo,
        "reconocimiento de aÃ±os de servicio": solicita,
        "OFICIO NÂ°      - 2026-UFESC-URRHH/UGEL.T/GOB.REG.TACNA": f"OFICIO NÂ° -UFESC-URRHH/UGEL.T/GOB.REG.TACNA",
        "SEÃ‘OR:": f"{tratamiento}:",
        "SEÃ‘OR": tratamiento,
        "OFICIO NÂ°": f"OFICIO NÂ° ",
    }


def documento_tiene_placeholders(documento):
    contenido = "\n".join(parrafo.text for parrafo in documento.paragraphs)
    return "{{" in contenido and "}}" in contenido


def limpiar_numeracion_oficio(documento):
    texto_objetivo = "OFICIO N°      -UFESC-URRHH/UGEL.T/GOB.REG.TACNA"

    for parrafo in documento.paragraphs:
        if "OFICIO" not in parrafo.text.upper():
            continue

        if "UGEL.T/GOB.REG.TACNA" not in parrafo.text.upper():
            continue

        for run in parrafo.runs:
            run.text = ""

        if parrafo.runs:
            parrafo.runs[0].text = texto_objetivo
        else:
            parrafo.add_run(texto_objetivo)


def configurar_documento_oficio(documento):
    seccion = documento.sections[0]
    seccion.top_margin = Cm(1.6)
    seccion.bottom_margin = Cm(1.6)
    seccion.left_margin = Cm(1.7)
    seccion.right_margin = Cm(1.7)

    estilo = documento.styles["Normal"]
    estilo.font.name = "Times New Roman"
    estilo._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    estilo.font.size = Pt(9)


def agregar_borde_parrafo(parrafo, posicion="bottom"):
    p_pr = parrafo._p.get_or_add_pPr()
    bordes = p_pr.find(qn("w:pBdr"))
    if bordes is None:
        bordes = OxmlElement("w:pBdr")
        p_pr.append(bordes)

    borde = bordes.find(qn(f"w:{posicion}"))
    if borde is None:
        borde = OxmlElement(f"w:{posicion}")
        bordes.append(borde)

    borde.set(qn("w:val"), "single")
    borde.set(qn("w:sz"), "8")
    borde.set(qn("w:space"), "1")
    borde.set(qn("w:color"), "000000")


def agregar_texto(parrafo, texto, bold=False, size=9, underline=False):
    run = parrafo.add_run(texto)
    run.bold = bold
    run.underline = underline
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    return run


def agregar_linea_campo(documento, etiqueta, valor, subrayado=False):
    parrafo = documento.add_paragraph()
    parrafo.paragraph_format.space_after = Pt(0)
    parrafo.paragraph_format.space_before = Pt(0)
    parrafo.paragraph_format.line_spacing = 1
    agregar_texto(parrafo, f"{etiqueta}: ", bold=True, size=9)
    agregar_texto(parrafo, valor, bold=False, size=9, underline=subrayado)
    return parrafo


def agregar_encabezado_oficio(documento):
    tabla = documento.add_table(rows=1, cols=2)
    tabla.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabla.autofit = False
    tabla.columns[0].width = Cm(5)
    tabla.columns[1].width = Cm(11)

    for celda in tabla.rows[0].cells:
        tc_pr = celda._tc.get_or_add_tcPr()
        for borde in ("top", "left", "bottom", "right"):
            elem = OxmlElement(f"w:{borde}")
            elem.set(qn("w:val"), "nil")
            tc_borders = tc_pr.first_child_found_in("w:tcBorders")
            if tc_borders is None:
                tc_borders = OxmlElement("w:tcBorders")
                tc_pr.append(tc_borders)
            tc_borders.append(elem)

    izquierda = tabla.cell(0, 0).paragraphs[0]
    izquierda.alignment = WD_ALIGN_PARAGRAPH.LEFT
    agregar_texto(izquierda, "TACNA\n", bold=True, size=16)
    agregar_texto(izquierda, "UGEL TACNA", bold=True, size=8)

    derecha = tabla.cell(0, 1).paragraphs[0]
    derecha.alignment = WD_ALIGN_PARAGRAPH.CENTER
    agregar_texto(
        derecha,
        '"Decenio de la igualdad de oportunidades para mujeres y hombres"\n',
        size=7,
    )
    agregar_texto(
        derecha,
        '"AÃ±o de la recuperaciÃ³n y consolidaciÃ³n de la educaciÃ³n pÃºblica"',
        size=7,
    )

    separador = documento.add_paragraph()
    separador.paragraph_format.space_before = Pt(2)
    separador.paragraph_format.space_after = Pt(4)
    agregar_borde_parrafo(separador)


def agregar_pie_oficio(documento):
    pie = documento.add_paragraph()
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pie.paragraph_format.space_before = Pt(10)
    agregar_borde_parrafo(pie, "top")
    agregar_texto(
        pie,
        "Unidad de GestiÃ³n Educativa Local Tacna - AsociaciÃ³n Los BegoÃ±ias Mz. I, Lt. 02-A\n",
        size=6,
    )
    agregar_texto(pie, "Distrito Gregorio AlbarracÃ­n Lanchipa\n", size=6)
    agregar_texto(pie, "Web: www.ugelgtacna.edu.pe\n", size=6)
    agregar_texto(pie, "Tacna - PerÃº", size=6)


def construir_documento_desde_cero(persona):
    documento = Document()

    fecha = obtener_fecha_actual()
    nombre = normalizar_texto(persona.get("nombre")).upper()
    condicion = normalizar_texto(persona.get("condicion")).upper()
    tipo = normalizar_texto(persona.get("tipo_persona")).upper()
    cargo_actual = normalizar_texto(persona.get("cargo_actual")) or f"{tipo} {condicion}"
    centro = normalizar_texto(persona.get("centro_trabajo")).upper()
    direccion = normalizar_texto(persona.get("direccion"))
    provincia = normalizar_texto(persona.get("provincia")) or "TACNA"
    telefono = normalizar_texto(persona.get("telefono"))
    correo = normalizar_texto(persona.get("correo"))
    solicita = normalizar_texto(persona.get("solicita"))
    periodos = obtener_lineas_periodos(persona)
    tratamiento = obtener_tratamiento(persona)

    documento.add_paragraph(f"Tacna, {fecha}")
    documento.add_paragraph("")
    documento.add_paragraph(f"OFICIO NÂ°     -UFESC-URRHH/UGEL.T/GOB.REG.TACNA")
    documento.add_paragraph("")
    documento.add_paragraph(f"{tratamiento}:")
    documento.add_paragraph(nombre)
    documento.add_paragraph(cargo_actual.upper())
    documento.add_paragraph(centro)
    documento.add_paragraph(f"DIRECCIÃ“N: {direccion}")
    documento.add_paragraph(f"{provincia}/{provincia}/{provincia}")
    documento.add_paragraph(f"TelÃ©fono: {telefono}")
    documento.add_paragraph(f"Correo electrÃ³nico: {correo}")
    documento.add_paragraph("")
    documento.add_paragraph("ASUNTO: FORMULO RESPUESTA")
    documento.add_paragraph("REFERENCIA: CUD. NÂ° __________")
    documento.add_paragraph("")

    documento.add_paragraph(
        "Tengo el agrado de dirigirme a usted, para expresarle mi cordial saludo y a la vez "
        f"brindar la debida atenciÃ³n al documento de la referencia, mediante el cual solicita {solicita}."
    )
    documento.add_paragraph(
        "Al respecto, se procediÃ³ a evaluar el expediente de la referencia, en el que se pudo "
        "verificar que falta presentar la documentaciÃ³n sustentatoria de los periodos indicados. "
        "Por lo que se exhorta cumplir con la subsanaciÃ³n correspondiente para continuar con el "
        "procedimiento administrativo, bajo su responsabilidad."
    )

    if periodos:
        documento.add_paragraph("Periodos observados:")
        for periodo in periodos:
            documento.add_paragraph(periodo, style="List Bullet")

    documento.add_paragraph("")
    documento.add_paragraph(
        "Sin otro particular, hago propicia la oportunidad para reiterarle las muestras de mi "
        "especial consideraciÃ³n y estima personal."
    )
    documento.add_paragraph("")
    documento.add_paragraph("Atentamente,")
    documento.add_paragraph("")
    documento.add_paragraph("GOBIERNO REGIONAL DE TACNA")
    documento.add_paragraph("____________________________________________")
    documento.add_paragraph("JEFE DE LA UNIDAD DE RECURSOS HUMANOS")
    documento.add_paragraph("UGEL TACNA")

    return documento


def construir_documento_formateado(persona):
    documento = Document()
    configurar_documento_oficio(documento)

    fecha = obtener_fecha_actual()
    oficio = numero_oficio(persona)
    nombre = normalizar_texto(persona.get("nombre")).upper()
    condicion = normalizar_texto(persona.get("condicion")).upper()
    tipo = normalizar_texto(persona.get("tipo_persona")).upper()
    cargo_actual = normalizar_texto(persona.get("cargo_actual")) or f"{tipo} {condicion}"
    centro = normalizar_texto(persona.get("centro_trabajo")).upper()
    direccion = normalizar_texto(persona.get("direccion"))
    provincia = normalizar_texto(persona.get("provincia")) or "TACNA"
    telefono = normalizar_texto(persona.get("telefono"))
    correo = normalizar_texto(persona.get("correo"))
    solicita = normalizar_texto(persona.get("solicita"))
    periodos = obtener_lineas_periodos(persona)
    tratamiento = obtener_tratamiento(persona)

    agregar_encabezado_oficio(documento)

    fecha_parrafo = documento.add_paragraph()
    fecha_parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fecha_parrafo.paragraph_format.space_after = Pt(2)
    agregar_texto(fecha_parrafo, f"Tacna, {fecha}", bold=True, size=9)

    oficio_parrafo = documento.add_paragraph()
    oficio_parrafo.paragraph_format.space_after = Pt(1)
    agregar_texto(oficio_parrafo, f"OFICIO N°            -2026-UFESC-URRHH/UGEL.T/GOB.REG.TACNA", bold=True, size=9, underline=True)

    agregar_linea_campo(documento, tratamiento, "")
    nombre_p = documento.add_paragraph()
    nombre_p.paragraph_format.space_after = Pt(0)
    agregar_texto(nombre_p, nombre, bold=True, size=9)

    cargo_p = documento.add_paragraph()
    cargo_p.paragraph_format.space_after = Pt(0)
    agregar_texto(cargo_p, cargo_actual.upper(), bold=True, size=9)

    centro_p = documento.add_paragraph()
    centro_p.paragraph_format.space_after = Pt(0)
    agregar_texto(centro_p, centro, bold=True, size=9)

    agregar_linea_campo(documento, "DIRECCIÃ“N", direccion, subrayado=True)
    agregar_linea_campo(documento, "Tacna/Tacna", provincia, subrayado=True)
    agregar_linea_campo(documento, "TelÃ©fono", telefono, subrayado=True)
    agregar_linea_campo(documento, "Correo", correo, subrayado=True)

    asunto = documento.add_paragraph()
    asunto.paragraph_format.space_before = Pt(4)
    asunto.paragraph_format.space_after = Pt(0)
    agregar_texto(asunto, "ASUNTO", bold=True, size=9)
    agregar_texto(asunto, " : FORMULO RESPUESTA", bold=True, size=9)

    referencia = documento.add_paragraph()
    referencia.paragraph_format.space_after = Pt(4)
    agregar_texto(referencia, "REFERENCIA", bold=True, size=9)
    agregar_texto(referencia, " : CUD. NÂ° 1016344/23/02/2026", bold=True, size=9)

    separador = documento.add_paragraph()
    separador.paragraph_format.space_after = Pt(5)
    agregar_borde_parrafo(separador)

    saludo = documento.add_paragraph()
    saludo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    saludo.paragraph_format.first_line_indent = Cm(1)
    saludo.paragraph_format.space_after = Pt(4)
    saludo.paragraph_format.line_spacing = 1
    agregar_texto(
        saludo,
        "Tengo el agrado de dirigirme a usted, para expresarle mi cordial saludo y a la vez "
        f"brindar la debida atenciÃ³n al documento de la referencia, mediante el cual solicita {solicita}.",
        size=9,
    )

    cuerpo = documento.add_paragraph()
    cuerpo.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cuerpo.paragraph_format.first_line_indent = Cm(1)
    cuerpo.paragraph_format.space_after = Pt(4)
    cuerpo.paragraph_format.line_spacing = 1
    agregar_texto(
        cuerpo,
        "Al respecto, se deberÃ¡ tener presente que el literal l) del artÃ­culo 41Â° de la Ley NÂ° 29944, "
        "Ley de Reforma Magisterial, reconoce el derecho al cÃ³mputo del tiempo de servicios efectivos; "
        "asimismo, para el reconocimiento por tiempo de servicios se consideran los periodos prestados "
        "bajo los regÃ­menes seÃ±alados por la normativa vigente, incluyendo servicios en condiciÃ³n de contratado.",
        size=9,
    )

    sustento = documento.add_paragraph()
    sustento.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    sustento.paragraph_format.first_line_indent = Cm(1)
    sustento.paragraph_format.space_after = Pt(4)
    sustento.paragraph_format.line_spacing = 1
    agregar_texto(
        sustento,
        'De acuerdo con la R.V.M. NÂ° 112-2023-MINEDU, se regulan los procedimientos tÃ©cnicos del '
        "EscalafÃ³n Magisterial, precisÃ¡ndose que el profesor puede solicitar el reconocimiento del tiempo "
        "de servicios prestados en instituciones educativas pÃºblicas adjuntando sus resoluciones y documentos "
        "de sustento correspondientes.",
        size=9,
    )

    cierre_revision = documento.add_paragraph()
    cierre_revision.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    cierre_revision.paragraph_format.first_line_indent = Cm(1)
    cierre_revision.paragraph_format.space_after = Pt(2)
    cierre_revision.paragraph_format.line_spacing = 1
    agregar_texto(
        cierre_revision,
        "Por ello, luego de la revisiÃ³n del expediente, se advierte que aÃºn falta documentaciÃ³n sustentatoria "
        "para continuar con el procedimiento administrativo. Bajo su responsabilidad, deberÃ¡ efectuar la "
        "subsanaciÃ³n correspondiente.",
        size=9,
    )

    if periodos:
        periodo_titulo = documento.add_paragraph()
        periodo_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        periodo_titulo.paragraph_format.space_before = Pt(2)
        periodo_titulo.paragraph_format.space_after = Pt(1)
        agregar_texto(periodo_titulo, "Periodo(s)", bold=True, size=9)

        for periodo in periodos:
            item = documento.add_paragraph()
            item.alignment = WD_ALIGN_PARAGRAPH.CENTER
            item.paragraph_format.space_after = Pt(0)
            agregar_texto(item, f"- {periodo}", size=9)

    despedida = documento.add_paragraph()
    despedida.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    despedida.paragraph_format.first_line_indent = Cm(1)
    despedida.paragraph_format.space_before = Pt(5)
    despedida.paragraph_format.space_after = Pt(6)
    agregar_texto(
        despedida,
        "Sin otro particular, hago propicia la oportunidad para reiterarle las muestras de mi especial "
        "consideraciÃ³n y estima personal.",
        size=9,
    )

    atentamente = documento.add_paragraph()
    atentamente.alignment = WD_ALIGN_PARAGRAPH.CENTER
    atentamente.paragraph_format.space_after = Pt(10)
    agregar_texto(atentamente, "Atentamente,", bold=True, size=9)

    firma = documento.add_paragraph()
    firma.alignment = WD_ALIGN_PARAGRAPH.CENTER
    firma.paragraph_format.space_after = Pt(1)
    agregar_texto(firma, "GOBIERNO REGIONAL DE TACNA", bold=True, size=9)

    firma_linea = documento.add_paragraph()
    firma_linea.alignment = WD_ALIGN_PARAGRAPH.CENTER
    firma_linea.paragraph_format.space_after = Pt(1)
    agregar_texto(firma_linea, "__________________________________________", bold=True, size=9)

    firma_nombre = documento.add_paragraph()
    firma_nombre.alignment = WD_ALIGN_PARAGRAPH.CENTER
    firma_nombre.paragraph_format.space_after = Pt(0)
    agregar_texto(firma_nombre, "ABOG. EDICA CARINA CANQUI ATENCIO", bold=True, size=9)

    firma_cargo = documento.add_paragraph()
    firma_cargo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    firma_cargo.paragraph_format.space_after = Pt(0)
    agregar_texto(firma_cargo, "JEFE DE LA UNIDAD DE RECURSOS HUMANOS", bold=True, size=9)

    firma_ugel = documento.add_paragraph()
    firma_ugel.alignment = WD_ALIGN_PARAGRAPH.CENTER
    firma_ugel.paragraph_format.space_after = Pt(2)
    agregar_texto(firma_ugel, "UGEL TACNA", bold=True, size=9)

    visto = documento.add_paragraph()
    visto.paragraph_format.space_before = Pt(6)
    visto.paragraph_format.space_after = Pt(0)
    agregar_texto(visto, "ECCA/UGRH", size=7)

    archivo = documento.add_paragraph()
    archivo.paragraph_format.space_after = Pt(2)
    agregar_texto(archivo, "MLBR/AAJPG", size=7)

    agregar_pie_oficio(documento)
    return documento


def poblar_documento(documento, persona):
    reemplazos = construir_reemplazos(persona)
    aplicar_reemplazos(documento, reemplazos)

    periodos = obtener_lineas_periodos(persona)
    if periodos:
        documento.add_paragraph("")
        documento.add_paragraph("Periodos observados:")
        for periodo in periodos:
            documento.add_paragraph(periodo, style="List Bullet")

    return documento


def generar_documento_persona(persona):
    plantilla = plantilla_disponible(persona)

    if plantilla:
        if plantilla_es_docx_valida(plantilla):
            try:
                documento = Document(str(plantilla))
                if documento_tiene_placeholders(documento):
                    aplicar_reemplazos(documento, construir_reemplazos(persona))
                else:
                    documento = poblar_documento(documento, persona)
            except (PackageNotFoundError, KeyError, ValueError):
                documento = construir_documento_formateado(persona)
        else:
            documento = construir_documento_formateado(persona)
    else:
        documento = construir_documento_formateado(persona)

    limpiar_numeracion_oficio(documento)
    salida = ruta_archivo_generado(persona)
    documento.save(str(salida))
    return salida


def generar_y_marcar(persona):
    archivo = generar_documento_persona(persona)
    actualizar_estado_generado(persona["id"])
    return archivo
