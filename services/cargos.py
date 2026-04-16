from utils.texto import normalizar_texto


TIPOS_BASE = {
    "DOCENTE": "PROFESOR",
    "AUXILIAR": "AUXILIAR DE EDUCACION",
    "AUXILIAR DE EDUCACION": "AUXILIAR DE EDUCACION",
    "ADMINISTRATIVO": "ADMINISTRATIVO",
}

TIPOS_FEMENINOS = {
    "PROFESOR": "PROFESORA",
    "ADMINISTRATIVO": "ADMINISTRATIVA",
}

CONDICIONES_FEMENINAS = {
    "NOMBRADO": "NOMBRADA",
    "CONTRATADO": "CONTRATADA",
}


def obtener_tratamiento(persona):
    sexo = normalizar_texto(persona.get("sexo")).lower()
    return "SEÑORA" if sexo == "femenino" else "SEÑOR"


def obtener_tipo_base(persona):
    tipo = normalizar_texto(persona.get("tipo_persona")).upper()
    return TIPOS_BASE.get(tipo, tipo)


def ajustar_tipo_por_sexo(tipo_base, sexo):
    if sexo != "femenino":
        return tipo_base
    return TIPOS_FEMENINOS.get(tipo_base, tipo_base)


def ajustar_condicion_por_sexo(condicion, sexo):
    condicion = condicion.upper()
    if sexo != "femenino":
        return condicion
    return CONDICIONES_FEMENINAS.get(condicion, condicion)


def obtener_cargo_persona(persona):
    sexo = normalizar_texto(persona.get("sexo")).lower()
    tipo_base = obtener_tipo_base(persona)
    tipo_ajustado = ajustar_tipo_por_sexo(tipo_base, sexo)
    condicion = normalizar_texto(persona.get("condicion")).upper()
    condicion_ajustada = ajustar_condicion_por_sexo(condicion, sexo)

    return " ".join(parte for parte in [tipo_ajustado, condicion_ajustada] if parte).strip()
