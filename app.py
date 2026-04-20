from datetime import datetime
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from flask import Flask, jsonify, redirect, render_template, request, send_file

from services.documentos import generar_y_marcar, ruta_archivo_generado
from services.personas import (
    eliminar_persona,
    guardar_persona,
    obtener_persona_por_id,
    obtener_personas,
    persona_desde_payload,
    contar_personas
)


app = Flask(__name__)


from math import ceil
from flask import request

@app.route("/")
def index():

    pagina = int(request.args.get("page", 1))
    limite = 10

    personas, tipos_persona, condiciones = obtener_personas(pagina, limite)

    total = contar_personas()
    paginas = ceil(total / limite)

    generados = sum(1 for p in personas if str(p.get("estado","")).lower() == "generado")
    pendientes = total - generados

    return render_template(
        "index.html",
        personas=personas,
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
    data = {
        "nombre": request.form["nombre"],
        "tipo_persona_id": request.form["tipo_persona_id"],
        "sexo": request.form.get("sexo", "masculino"),
        "condicion_id": request.form["condicion_id"],
        "centro_trabajo": request.form["centro_trabajo"],
        "telefono": request.form["telefono"],
        "correo": request.form.get("correo", ""),
    }

    guardar_persona(data)
    return redirect("/")


@app.route("/eliminar/<int:persona_id>", methods=["DELETE"])
def eliminar(persona_id):
    persona = obtener_persona_por_id(persona_id)
    if persona:
        archivo = ruta_archivo_generado(persona)
        if archivo.exists():
            archivo.unlink()

    eliminar_persona(persona_id)
    return ("", 204)


@app.route("/generar", methods=["POST"])
def generar():
    payload = request.get_json(silent=True) or {}
    ids = payload.get("ids") or []
    personas_payload = payload.get("personas") or []
    ids = [int(persona_id) for persona_id in ids if str(persona_id).isdigit()]

    if not ids:
        return jsonify({"ok": False, "message": "No hay registros seleccionados."}), 400

    generados = []
    for persona_id in ids:
        persona = obtener_persona_por_id(persona_id)
        if not persona:
            persona = persona_desde_payload(persona_id, personas_payload)
        if not persona:
            continue

        archivo = generar_y_marcar(persona)
        generados.append({"id": persona_id, "archivo": archivo.name})

    if not generados:
        return jsonify(
            {
                "ok": False,
                "message": "No se pudo obtener el registro o la conexión con Supabase falló.",
            }
        ), 503

    return jsonify({"ok": True, "generados": generados})


@app.route("/descargar/<int:persona_id>")
def descargar(persona_id):
    persona = obtener_persona_por_id(persona_id)
    if not persona:
        return redirect("/")

    archivo = ruta_archivo_generado(persona)
    if not archivo.exists():
        archivo = generar_y_marcar(persona)

    return send_file(archivo, as_attachment=True, download_name=archivo.name)


@app.route("/ver/<int:persona_id>")
def ver(persona_id):
    return redirect(f"/descargar/{persona_id}")


@app.route("/descargar_zip")
def descargar_zip():
    ids_raw = request.args.get("ids", "")
    ids = [int(persona_id) for persona_id in ids_raw.split(",") if persona_id.strip().isdigit()]

    if not ids:
        personas, _, _ = obtener_personas()
        ids = [int(persona["id"]) for persona in personas]

    buffer = BytesIO()
    with ZipFile(buffer, "w", ZIP_DEFLATED) as zip_file:
        for persona_id in ids:
            persona = obtener_persona_por_id(persona_id)
            if not persona:
                continue

            archivo = ruta_archivo_generado(persona)
            if not archivo.exists():
                archivo = generar_y_marcar(persona)

            zip_file.write(archivo, arcname=archivo.name)

    buffer.seek(0)
    nombre_zip = f"oficios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    return send_file(buffer, as_attachment=True, download_name=nombre_zip, mimetype="application/zip")


if __name__ == "__main__":
    app.run(debug=True)
