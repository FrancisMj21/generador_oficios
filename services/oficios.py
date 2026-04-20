from datetime import datetime
from config import supabase


def obtener_oficios(pagina=1, limite=10):
    offset = (pagina - 1) * limite
    try:
        response = (supabase
            .table('oficios')
            .select('*, personas:nombre, cud:numero_cud')
            .range(offset, offset + limite - 1)
            .order('fecha_generado', desc=True)
            .execute())
        return response.data or [], obtener_tipos_persona(), obtener_condiciones()  # Reuse from personas if imported
    except Exception as e:
        print("ERROR OBTENER OFICIOS:", e)
        return [], obtener_tipos_persona(), obtener_condiciones()


def obtener_tipos_persona():
    response = supabase.table("tipos_persona").select("*").execute()
    return response.data or []


def obtener_condiciones():
    response = supabase.table("condiciones").select("*").execute()
    return response.data or []


def enriquecer_oficio(oficio):
    # Enrich tipo/cond from persona joins if needed
    from services.personas import enriquecer_personas  # Adapt if needed
    # For now assume joins bring nombre, add tipo/cond if selected *,personas(*)
    return oficio


def obtener_oficios_enriquecidos(pagina=1, limite=10):
    oficios_raw, tipos, conds = obtener_oficios(pagina, limite)
    # Enrich if needed
    for o in oficios_raw:
        o['nombre_completo'] = o['personas']['nombre']
        o['cud'] = o['cud']['numero_cud']
    return oficios_raw, tipos, conds


def obtener_oficio_por_id(oficio_id):
    try:
        response = supabase.table('oficios').select('*, personas(*), cud(*)').eq('id', oficio_id).single().execute()
        if response.data:
            data = response.data
            data['nombre_completo'] = data['personas']['nombre']
            data['cud'] = data['cud']['numero_cud'] if data['cud'] else ''
            # Add tipo/cond from personas
            data['tipo_persona'] = data['personas'].get('tipo_persona', '')
            data['condicion'] = data['personas'].get('condicion', '')
            data['centro_trabajo'] = data['personas'].get('centro_trabajo', '')
            # Copy other needed for docx
            for k, v in data['personas'].items():
                if k not in data:
                    data[k] = v
            return data
        return None
    except Exception:
        return None


def guardar_oficio(persona_id, cud_id):
    data = {
        'persona_id': persona_id,
        'cud_id': cud_id,
        'fecha_generado': datetime.now().isoformat(),
        'estado': 'Pendiente',
        'archivo_docx': None
    }
    nueva = supabase.table('oficios').insert(data).execute()
    return nueva.data[0]['id']


def eliminar_oficio(oficio_id):
    supabase.table('oficios').delete().eq('id', oficio_id).execute()


def actualizar_estado_generado(oficio_id):
    try:
        supabase.table('oficios').update({'estado': 'Generado', 'fecha_generado': datetime.now().isoformat()}).eq('id', oficio_id).execute()
    except Exception:
        pass


def contar_oficios():
    try:
        r = supabase.table('oficios').select('id', count='exact').execute()
        return r.count or 0
    except Exception:
        return 0
