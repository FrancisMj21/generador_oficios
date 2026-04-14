from flask import Flask, render_template, request, redirect
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# Mostrar lista
@app.route("/")
def index():

    response = supabase.table("personas").select("*").execute()
    personas = response.data

    return render_template("index.html", personas=personas)


# Registrar persona
@app.route("/guardar", methods=["POST"])
def guardar():

    data = {
        "dni": request.form["dni"],
        "nombre": request.form["nombre"],
        "tipo_persona": request.form["tipo_persona"],
        "condicion": request.form["condicion"],
        "centro_trabajo": request.form["centro_trabajo"],
        "telefono": request.form["telefono"],
        "correo": request.form["correo"]
    }

    supabase.table("personas").insert(data).execute()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)