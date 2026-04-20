from datetime import datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from config import supabase

from flask import Flask, jsonify, redirect, render_template, request, send_file

from pathlib import Path
from services.cud import guardar_cud
from services.documentos import generar_y_marcar, ruta_archivo_generado
from utils.texto import slugify
from config import GENERATED_DIR
from services.oficios import (
    contar_oficios,
    eliminar_oficio,
    guardar_oficio,
    obtener_oficio_por_id,
    obtener_oficios_enriquecidos,
    actualizar_estado_generado,
)
from services.personas import (
    guardar_persona,
)


app = Flask(__name__)


from math import ceil
from flask import request

@app.route("/")
def index():

    pagina = int(request.args.get("page", 1))
    limite = 10

    documentos, tipos_persona, condiciones = obtener_oficios_enriquecidos(pagina, limite)

    total = contar_oficios()
    paginas = ceil(total / limite)

    generados = sum(1 for d in documentos if str(d.get("estado","")).lower() == "generado")
    pendientes = total - generados

    print("TIPOS_PERSONA:", tipos_persona)
    print("CONDICIONES:", condiciones)

    return render_template(
        "index.html",
        documentos=documentos,
        tipos_persona=tipos_persona,
        condiciones=condiciones,
        total=total,
        generados=generados,
        pendientes=pendientes,
        pagina=pagina,
        paginas=paginas
    )


@app.route("/guardar", methods=["POST"])
def guardar():
    data_persona = {
        "nombre": request.form["nombre"],
        "tipo_persona_id": request.form["tipo_persona_id"],
        "sexo": request.form.get("sexo", "masculino"),
        "condicion_id": request.form["condicion_id"],
        "centro_trabajo": request.form["centro_trabajo"],
        "telefono": request.form["telefono"],
        "correo": request.form.get("correo", ""),
        "direccion": request.form.get("direccion", ""),
        "provincia": request.form.get("provincia", "Tacna"),
    }

    persona_id = guardar_persona(data_persona)
    cud_data = {
        "numero_cud": request.form.get("numero_cud", ""),
        "solicita": request.form.get("solicita", ""),
        "periodos": request.form.get("periodos", ""),
    }
    cud_id = guardar_cud(cud_data)
    guardar_oficio(persona_id, cud_id)
    return redirect("/")


@app.route("/eliminar/<int:oficio_id>", methods=["DELETE"])
def eliminar(oficio_id):
    oficio = obtener_oficio_por_id(oficio_id)
    if oficio:
        archivo_name = f"oficio_{oficio_id}_{slugify(oficio.get('nombre_completo', ''))}.docx"
        archivo = GENERATED_DIR / archivo_name
        if archivo.exists():
            archivo.unlink()
    eliminar_oficio(oficio_id)
    return ("", 204)


@app.route("/generar", methods=["POST"])
def generar():
    payload = request.get_json(silent=True) or {}
    ids = payload.get("ids") or []
    oficios_payload = payload.get("oficios") or []  # Change from personas_payload
    ids = [int(id_) for id_ in ids if str(id_).isdigit()]

    if not ids:
        return jsonify({"ok": False, "message": "No hay registros seleccionados."}), 400

    generados = []
    for id_ in ids:
        oficio = obtener_oficio_por_id(id_)
        if not oficio:
            # Fallback to payload
            for o in oficios_payload:
                if str(o.get("id")) == str(id_):
                    oficio = o
                    break
        if not oficio:
            continue

        archivo = generar_y_marcar(oficio)
        supabase.table('oficios').update({'archivo_docx': archivo.name}).eq('id', id_).execute()
        actualizar_estado_generado(id_)
        generados.append({"id": id_, "archivo": archivo.name})

    if not generados:
        return jsonify({
            "ok": False,
            "message": "No se pudo obtener el registro o la conexión con Supabase falló.",
        }), 503

    return jsonify({"ok": True, "generados": generados})


@app.route("/descargar/<int:oficio_id>")
def descargar(oficio_id):
    oficio = obtener_oficio_por_id(oficio_id)
    if not oficio:
        return redirect("/")

    archivo_name = f"oficio_{oficio_id}_{slugify(oficio.get('nombre_completo', ''))}.docx"
    archivo = GENERATED_DIR / archivo_name
    if not archivo.exists():
        archivo = generar_y_marcar(oficio)

    return send_file(archivo, as_attachment=True, download_name=archivo.name)


@app.route("/ver/<int:oficio_id>")
def ver(oficio_id):
    return redirect(f"/descargar/{oficio_id}")





@app.route("/descargar_zip")
def descargar_zip():
    ids_raw = request.args.get("ids", "")
    ids = [int(id_) for id_ in ids_raw.split(",") if id_.strip().isdigit()]

    if not ids:
        documentos, _, _ = obtener_oficios_enriquecidos()
        ids = [int(d["id"]) for d in documentos]

    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as zip_file:
        for id_ in ids:
            oficio = obtener_oficio_por_id(id_)
            if not oficio:
                continue
            archivo_name = f"oficio_{id_}_{slugify(oficio.get('nombre_completo', ''))}.docx"
            archivo = GENERATED_DIR / archivo_name
            if not archivo.exists():
                archivo = generar_y_marcar(oficio)
            zip_file.write(archivo, arcname=archivo.name)

    buffer.seek(0)
    nombre_zip = f"oficios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    return send_file(buffer, as_attachment=True, download_name=nombre_zip, mimetype="application/zip")


if __name__ == "__main__":
    app.run(debug=True)
