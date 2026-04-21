from datetime import date
from config import supabase
from utils.texto import normalizar_texto


def guardar_cud(data):
    
    numero_cud = normalizar_texto(data.get('numero_cud', ''))
    if not numero_cud:
        raise ValueError('numero_cud requerido')
    
    # Search existing
    existente = supabase.table('cud').select('id').eq('numero_cud', numero_cud).limit(1).execute()
    
    if existente.data:
        return existente.data[0]['id']
    
    # Create new
    nueva_data = {
        'numero_cud': numero_cud,
        'fecha': data.get('fecha'),
        'solicita': normalizar_texto(data.get('solicita', '')),
        'periodos': normalizar_texto(data.get('periodos', '')),
    }
    nueva = supabase.table('cud').insert(nueva_data).execute()
    return nueva.data[0]['id']


def obtener_cud_por_id(cud_id):
    try:
        response = supabase.table('cud').select('*').eq('id', cud_id).limit(1).execute()
        return response.data[0] if response.data else None
    except Exception:
        return None
