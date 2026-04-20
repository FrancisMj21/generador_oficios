# TODO: Implementar nuevo flujo de registro y listado con oficios/cud

## Pendientes (6/7 completados)

- [x] 1. Crear services/cud.py (CRUD Supabase para cud table)
- [x] 2. Crear services/oficios.py (CRUD para oficios con joins a personas/cud)
- [x] 3. Editar app.py: actualizar /guardar (add cud/oficio create), /index (listar oficios), /generar (oficio ids), /eliminar/descargar_zip etc.
- [x] 4. Editar templates/index.html: agregar input numero_cud/solicita/direccion/provincia, cambiar tabla columns a ID/Nombre/CUD/Estado, loop documentos
- [x] 5. Editar static/app.js: handler submit form AJAX /guardar, adaptar a data-oficio, funciones obtenerOficioPorId etc., preview/generate from oficios
- [x] 6. Actualizar services/documentos.py: generar_y_marcar_oficio(data from oficio joins)
- [ ] 7. Test: ejecutar app, submit form (verifica Supabase crea persona/cud/oficio), check tabla, generar/listado

**Progreso: Marcar como completado cada paso. Al final: attempt_completion**

**Progreso: Marcar como completado cada paso. Al final: attempt_completion**

**Progreso: Marcar como completado cada paso. Al final: attempt_completion**
