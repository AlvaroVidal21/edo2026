# Guía para trabajar en este repositorio

## Antes de implementar

- Lee `docs/00_contexto.md`, `docs/01_modelo_negocio.md`, `docs/02_reglas_negocio.md`, `docs/04_entidades.md` y `docs/05_stack.md`. Consulta `docs/03_casos_uso.md` cuando el cambio afecte un flujo.
- Si dos documentos discrepan, no inventes una regla: señala la contradicción y conserva la decisión más reciente expresada por el usuario.
- La aplicación es local. No envíes datos de empresas a servicios externos.

## Decisiones del dominio

- `Empresa` es la raíz de los registros operativos y de crítica.
- Los contactos principal y alternativo permanecen como atributos de `Empresa`; no crear una entidad `Contacto` sin una nueva decisión del usuario.
- Cada crítica pertenece a una empresa y debe identificar la variable y el registro analizados. Para recodificar un cargo de contacto, conserva el texto original y el código resultante en la crítica, junto con su sustento.
- `Actividad` referencia a `Empresa`, `Medio` y `Categoría de actividad`. Medio y categoría son catálogos editables, de selección única por actividad; desactiva opciones usadas en vez de borrarlas físicamente.
- El tratamiento de `Incidencia` como entidad o atributo sigue pendiente. `docs/02_reglas_negocio.md` describe ámbito y ciclo de vida, mientras `docs/04_entidades.md` aplaza su entidad propia. No fijes el esquema de incidencias hasta resolver esa discrepancia con el usuario.
- La versión actual no administra recordatorios ni acciones futuras.

## Stack y convenciones

- Sigue el stack documentado en `docs/05_stack.md`: Python, Django y PostgreSQL. Usa modelos y migraciones de Django para cambios de esquema; el SQL de `docs/04_entidades.md` sirve como referencia relacional.
- La interfaz y la documentación del proyecto están en español. Mantén las convenciones existentes para nombres de tablas, campos y código.
- Mantén los cambios acotados al requerimiento y actualiza los documentos afectados cuando cambie una decisión del dominio.
