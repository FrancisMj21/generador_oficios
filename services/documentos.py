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


def nombre_archivo_oficio(data):
    return f"oficio_{data['id']}_{slugify(data.get('nombre_completo', data.get('nombre', '')))}.docx"


def ruta_archivo_generado(data):
    return GENERATED_DIR / nombre_archivo_oficio(data)


def obtener_lineas_periodos(data):
    periodos = normalizar_texto(data.get("periodos"))
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


def preparar_datos(data):
    nombre_raw = normalizar_texto(data.get("nombre", "")).upper()
    cargo = obtener_cargo_persona(data).upper()
    centro_trabajo = normalizar_texto(data.get("centro_trabajo", "")).upper()
    direccion = normalizar_texto(data.get("direccion", ""))
    provincia = normalizar_texto(data.get("provincia", ""))
    telefono = normalizar_texto(data.get("telefono", ""))
    correo = normalizar_texto(data.get("correo", ""))
    solicita = normalizar_texto(data.get("solicita", ""))
    tratamiento = obtener_tratamiento(data)
    fecha_cud_raw = data.get("fecha", "")
    fecha_cud = ""

    if fecha_cud_raw:
        fecha_cud = datetime.strptime(fecha_cud_raw, "%Y-%m-%d").strftime("%d/%m/%Y")
    periodos = obtener_lineas_periodos(data)
    numero_cud = normalizar_texto(data.get("numero_cud", ""))


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
        "fecha_cud": fecha_cud,
        "periodos": periodos,
        "numero_cud": numero_cud,
    }


def generar_documento(data):
    documento = Document()
    configurar_documento(documento)

    seccion = documento.sections[0]

    # Header y footer primero
    agregar_encabezado_oficio(seccion)
    agregar_pie_oficio(seccion)

    # Cuerpo principal (info + cuerpo)
    data_prepared = preparar_datos(data)
    agregar_seccion_info(documento, data_prepared)
    agregar_cuerpo_oficio(documento, data_prepared)

    salida = ruta_archivo_generado(data)
    documento.save(str(salida))
    return salida


def generar_y_marcar(data):
    archivo = generar_documento(data)
    return archivo

