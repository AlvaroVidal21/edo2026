# Entidades del sistema EDO 2026

## 1. Propósito

Definir las entidades principales del sistema, sus atributos y relaciones antes de diseñar las tablas físicas en PostgreSQL.

`Medio` y `Categoría de actividad` son entidades de catálogo: cada una tendrá su propia tabla secundaria en PostgreSQL y las actividades las referenciarán mediante claves foráneas. Sus opciones se podrán administrar desde la aplicación.

## 2. Empresa

Representa una empresa asignada al Crítico Verificador y constituye la entidad central del sistema.

### Atributos

| Atributo | Descripción | Requerido |
| --- | --- | :---: |
| `id` | Identificador único. | Sí |
| `ruc` | Registro Único de Contribuyentes. | Sí |
| `razon_social` | Razón social de la empresa. | Sí |
| `region` | Región a la que pertenece. | Sí |
| `ciiu` | Código de actividad económica. | Sí |

### Contacto principal

El contacto principal es obligatorio.

| Atributo | Descripción |
| --- | --- |
| `contacto_principal_nombre` | Nombre del contacto. |
| `contacto_principal_cargo` | Cargo del contacto. |
| `contacto_principal_telefono` | Teléfono del contacto. |
| `contacto_principal_correo` | Correo electrónico del contacto. |

### Contacto alternativo

El contacto alternativo es opcional.

| Atributo | Descripción |
| --- | --- |
| `contacto_alternativo_nombre` | Nombre del contacto. |
| `contacto_alternativo_cargo` | Cargo del contacto. |
| `contacto_alternativo_telefono` | Teléfono del contacto. |
| `contacto_alternativo_correo` | Correo electrónico del contacto. |

### Seguimiento

- `situacion_empresa`
- `estado_contacto`
- `correo_confirmado`
- `estado_encuesta`
- `estado_critica`

### Relaciones

Una empresa puede tener:

- muchas actividades;
- muchos registros de crítica.

## 3. Actividad

Representa una gestión realizada por el crítico respecto de una empresa.

### Ejemplos

- Llamada realizada.
- Mensaje enviado.
- Asistencia brindada.
- Consulta atendida.
- Investigación realizada.

### Atributos

| Atributo | Descripción |
| --- | --- |
| `id` | Identificador único. |
| `empresa_id` | Empresa relacionada. |
| `medio_id` | Medio utilizado. |
| `categoria_id` | Categoría de la actividad. |
| `fecha` | Fecha de la actividad. |
| `hora` | Hora de la actividad. |
| `descripcion` | Detalle de la gestión realizada. |

### Relaciones

```text
EMPRESA 1 ----- N ACTIVIDADES
MEDIO 1 ------- N ACTIVIDADES
CATEGORIA 1 -- N ACTIVIDADES
```

Toda actividad:

- pertenece a una empresa;
- utiliza un medio;
- pertenece a una categoría.

## 4. Medio

Representa el canal mediante el cual se realizó una actividad.

### Ejemplos iniciales

- WhatsApp
- Correo
- Llamada
- Reunión virtual
- Presencial
- Otro

### Atributos

| Atributo | Descripción |
| --- | --- |
| `id` | Identificador único. |
| `nombre` | Nombre del medio. |
| `activo` | Indica si el medio está disponible para nuevas actividades. |

El catálogo de medios debe poder administrarse desde la aplicación. Se podrá:

- agregar medios;
- modificar medios;
- desactivar medios.

Preferentemente, no se eliminarán físicamente los medios que ya hayan sido utilizados en actividades, para conservar la trazabilidad histórica.

## 5. Categoría de actividad

Representa el propósito o la naturaleza de una actividad.

### Ejemplos iniciales

- Primer contacto
- Seguimiento
- Consulta
- Asesoría
- Recordatorio
- Investigación
- Coordinación
- Otro

### Atributos

| Atributo | Descripción |
| --- | --- |
| `id` | Identificador único. |
| `nombre` | Nombre de la categoría. |
| `descripcion` | Explicación de la categoría. |
| `activo` | Indica si la categoría está disponible para nuevas actividades. |

El catálogo debe poder administrarse desde la aplicación. Se podrá:

- agregar categorías;
- modificar categorías;
- desactivar categorías.

Al igual que los medios, una categoría utilizada históricamente no debería eliminarse físicamente.

## 6. Diferencia entre medio y categoría

Son conceptos independientes:

- **Medio:** responde a «¿cómo se realizó la actividad?».
- **Categoría:** responde a «¿qué tipo de gestión se realizó?».

Ambas son tablas secundarias de catálogo, no columnas de texto repetidas en `Actividad`. Cada actividad tiene un solo medio y una sola categoría, seleccionados desde listas desplegables de selección única. No se usarán casillas de verificación, porque no se eligen varios valores para una misma actividad.

La aplicación permitirá agregar, editar y desactivar opciones. Si una opción ya está referenciada por actividades, no se eliminará físicamente. Si cambia el significado de una opción, se desactivará y se agregará otra para no alterar el sentido de los registros históricos; la edición se reservará para corregir o aclarar su nombre o descripción.

### Ejemplo

| Campo | Valor |
| --- | --- |
| Empresa | Empresa ABC |
| Medio | Llamada |
| Categoría | Seguimiento |
| Descripción | Se llamó para consultar el avance del formulario. |

Otro ejemplo:

| Medio | Categoría |
| --- | --- |
| WhatsApp | Consulta |

Una misma categoría puede utilizar diferentes medios y un mismo medio puede utilizarse para diferentes categorías.

## 7. Crítica

Representa la revisión de un dato registrado en la encuesta para determinar si debe mantenerse o recodificarse.

Esta entidad pertenece a una empresa y será desarrollada con mayor detalle durante la implementación de la segunda etapa del sistema.

### Atributos iniciales

- `id`
- `empresa_id`
- `variable_analizada`
- `valor_original`
- `valor_resultante`
- `tipo_resultado`
- `evidencia`
- `metodo_analisis`
- `justificacion`
- `nivel_confianza`
- `estado_revision`

### Tipos de resultado

- Validación
- Recodificación

### Relación

```text
EMPRESA 1 ----- N CRITICAS
```

Actividad y Crítica no necesitan relacionarse directamente.

## 8. Entidades no creadas

### Informante

No será una entidad independiente en esta versión. La aplicación manejará como máximo:

- un contacto principal obligatorio;
- un contacto alternativo opcional.

Sus datos permanecerán dentro de `Empresa`. Las actividades se realizan respecto de la empresa y no respecto de un informante individual.

### Incidencia

No se define todavía como entidad independiente. Su diseño se evaluará posteriormente junto con la etapa completa de crítica y consistencia.

## 9. Modelo conceptual

```text
                         EMPRESA
                            |
                 +----------+----------+
                 |                     |
                 v                     v
             ACTIVIDAD              CRITICA
              |     |
              |     |
              v     v
            MEDIO  CATEGORIA
```

### Relaciones

- Empresa `1:N` Actividad.
- Empresa `1:N` Crítica.
- Medio `1:N` Actividad.
- Categoría `1:N` Actividad.

## 10. Entidades actuales

### Entidades principales

- Empresa
- Actividad
- Crítica

### Entidades de catálogo administrables

- Medio
- Categoría de actividad

La mejora principal consiste en reemplazar los valores de texto almacenados directamente en `Actividad` por referencias a catálogos:

```text
Antes:
Actividad
- medio = "WhatsApp"
- categoria = "Seguimiento"

Ahora:
Actividad
- medio_id -> Medio
- categoria_id -> CategoriaActividad
```

## 11. Relaciones SQL en PostgreSQL

Se usarán los nombres `empresa`, `actividad`, `critica`, `medio` y `categoria_actividad` para las tablas. Cada tabla tendrá `id` como clave primaria; las columnas que la referencien deberán tener un tipo compatible.

| Tabla | Clave foránea | Referencia | Relación |
| --- | --- | --- | --- |
| `actividad` | `empresa_id` | `empresa.id` | Una empresa puede tener muchas actividades. |
| `actividad` | `medio_id` | `medio.id` | Un medio puede utilizarse en muchas actividades. |
| `actividad` | `categoria_id` | `categoria_actividad.id` | Una categoría puede utilizarse en muchas actividades. |
| `critica` | `empresa_id` | `empresa.id` | Una empresa puede tener muchos casos de crítica. |

El siguiente SQL define las relaciones para cuando se creen las tablas y sus columnas:

```sql
ALTER TABLE actividad
    ALTER COLUMN empresa_id SET NOT NULL,
    ALTER COLUMN medio_id SET NOT NULL,
    ALTER COLUMN categoria_id SET NOT NULL,
    ADD CONSTRAINT actividad_empresa_fk
        FOREIGN KEY (empresa_id) REFERENCES empresa (id)
        ON DELETE RESTRICT,
    ADD CONSTRAINT actividad_medio_fk
        FOREIGN KEY (medio_id) REFERENCES medio (id)
        ON DELETE RESTRICT,
    ADD CONSTRAINT actividad_categoria_fk
        FOREIGN KEY (categoria_id) REFERENCES categoria_actividad (id)
        ON DELETE RESTRICT;

ALTER TABLE critica
    ALTER COLUMN empresa_id SET NOT NULL,
    ADD CONSTRAINT critica_empresa_fk
        FOREIGN KEY (empresa_id) REFERENCES empresa (id)
        ON DELETE RESTRICT;
```

Las relaciones son obligatorias para cada actividad y caso de crítica. `ON DELETE RESTRICT` impide eliminar una empresa, medio o categoría mientras tenga registros relacionados, conservando su historial.

Los contactos permanecen como atributos de `empresa`. Para recodificar su cargo, el caso de crítica utiliza `empresa_id` y una `variable_analizada` específica, como `contacto_principal_cargo` o `contacto_alternativo_cargo`, conservando el texto informado en `valor_original` y el código asignado en `valor_resultante`. No se requiere una clave foránea de contacto ni una relación directa entre `actividad` y `critica`.
