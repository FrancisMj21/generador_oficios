# TODO: Refactor Documento Generación

## Plan Aprobado: Separar Encabezado/Info/Cuerpo/Pie

### [x] 1. Actualizar services/documento_layout.py
   - Agregar función `configurar_documento(doc)` para márgenes y fuentes.

### [x] 2. Extender services/documento_partes.py
   - Importar layout constants.
   - Agregar `agregar_seccion_info(seccion, info_data)`.
   - Agregar `agregar_cuerpo_oficio(seccion, data)`.
   - Mover utils borde/texto aquí si aplica.

### [x] 3. Refactor services/documentos.py
   - Remover template loading y constructores inline.
   - Nueva `generar_documento_persona()` usando partes/layout.
   - Eliminar duplicados.

### [x] 4. Probar
   - `python app.py` (servidor activo)
   - Generar 1 oficio via UI completado ✅
   - Nuevos archivos en generados/ con estructura refactorizada.

### [x] 5. Limpiar ✅
   - Archivos generados listos para nueva prueba.


