# Entidades del sistema EDO 2026

## 1. Propósito

Definir las entidades principales del sistema, sus atributos y relaciones antes de diseñar las tablas físicas en PostgreSQL.

El modelo debe permitir que ciertos catálogos, como medios y categorías de actividad, puedan administrarse desde la aplicación.

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

### Catálogos administrables

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
