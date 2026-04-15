from config import supabase
from utils.texto import normalizar_texto


LOOKUP_CACHE = {
    "tipos_persona": [],
    "condiciones": [],
}


def obtener_lista(nombre_tabla):
    try:
        response = supabase.table(nombre_tabla).select("*").execute()
        data = response.data or []
        if nombre_tabla in LOOKUP_CACHE and data:
            LOOKUP_CACHE[nombre_tabla] = data
        return data
    except Exception:
        return LOOKUP_CACHE.get(nombre_tabla, [])


def enriquecer_personas(personas, tipos_persona, condiciones):
    tipo_map = {tipo["id"]: tipo["nombre"] for tipo in tipos_persona}
    condicion_map = {cond["id"]: cond["nombre"] for cond in condiciones}

    for persona in personas:
        persona["tipo_persona"] = tipo_map.get(
            persona.get("tipo_persona_id"),
            persona.get("tipo_persona", ""),
        )
        persona["condicion"] = condicion_map.get(
            persona.get("condicion_id"),
            persona.get("condicion", ""),
        )
        persona["estado"] = normalizar_texto(persona.get("estado")) or "Pendiente"

    return personas


def obtener_personas():
    personas = obtener_lista("personas")
    tipos_persona = obtener_lista("tipos_persona")
    condiciones = obtener_lista("condiciones")
    return enriquecer_personas(personas, tipos_persona, condiciones), tipos_persona, condiciones


def obtener_persona_por_id(persona_id):
    try:
        response = supabase.table("personas").select("*").eq("id", persona_id).limit(1).execute()
        data = response.data or []
    except Exception:
        data = []

    if not data:
        return None

    persona = data[0]
    tipos_persona = obtener_lista("tipos_persona")
    condiciones = obtener_lista("condiciones")
    return enriquecer_personas([persona], tipos_persona, condiciones)[0]


def persona_desde_payload(persona_id, personas_payload):
    for persona in personas_payload:
        if str(persona.get("id")) == str(persona_id):
            return persona
    return None


def guardar_persona(data):
    supabase.table("personas").insert(data).execute()


def eliminar_persona(persona_id):
    supabase.table("personas").delete().eq("id", persona_id).execute()


def actualizar_estado_generado(persona_id):
    try:
        supabase.table("personas").update({"estado": "Generado"}).eq("id", persona_id).execute()
    except Exception:
        pass
