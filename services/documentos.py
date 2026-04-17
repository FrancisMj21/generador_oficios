from datetime import datetime
from pathlib import Path

from docx import Document

from config import GENERATED_DIR
from services.cargos import obtener_cargo_persona, obtener_tratamiento
from services.documento_layout import configurar_documento
from services.documento_partes import (
    agregar_cuerpo_oficio,
    agregar_encabezado_oficio,
    agregar_pie_oficio,
    agregar_seccion_info,
)
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


def preparar_datos_persona(persona):
    nombre_raw = normalizar_texto(persona.get("nombre", "")).upper()
    cargo = obtener_cargo_persona(persona).upper()
    centro_trabajo = normalizar_texto(persona.get("centro_trabajo", "")).upper()
    direccion = normalizar_texto(persona.get("direccion", ""))
    provincia = normalizar_texto(persona.get("provincia", ""))
    telefono = normalizar_texto(persona.get("telefono", ""))
    correo = normalizar_texto(persona.get("correo", ""))
    solicita = normalizar_texto(persona.get("solicita", ""))
    tratamiento = obtener_tratamiento(persona)
    fecha = obtener_fecha_actual()
    periodos = obtener_lineas_periodos(persona)

    return {
        "tratamiento": tratamiento,
        "nombre": nombre_raw,
        "cargo": cargo,
        "centro_trabajo": centro_trabajo,
        "direccion": direccion,
        "provincia": provincia,
        "telefono": telefono,
        "correo": correo,
        "solicita": solicita,
        "fecha": fecha,
        "periodos": periodos,
    }


def generar_documento_persona(persona):
    documento = Document()
    configurar_documento(documento)

    seccion = documento.sections[0]

    # Header y footer primero
    agregar_encabezado_oficio(seccion)
    agregar_pie_oficio(seccion)

    # Cuerpo principal (info + cuerpo)
    data = preparar_datos_persona(persona)
    agregar_seccion_info(documento, data)
    agregar_cuerpo_oficio(documento, data)

    salida = ruta_archivo_generado(persona)
    documento.save(str(salida))
    return salida


def generar_y_marcar(persona):
    archivo = generar_documento_persona(persona)
    actualizar_estado_generado(persona["id"])
    return archivo

