import re


def normalizar_texto(valor):
    return str(valor or "").strip()


def slugify(valor):
    texto = normalizar_texto(valor).lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    return texto.strip("_") or "archivo"
