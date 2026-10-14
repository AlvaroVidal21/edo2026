# 01_modelo_negocio.md — Dominio y Vocabulario EDO 2026

## 1. Propósito

Definir los conceptos principales del trabajo del Crítico Verificador en la EDO 2026 y las relaciones que existen entre ellos en la realidad operativa.

Este documento describe el dominio del sistema antes de diseñar reglas de negocio, entidades de base de datos o código.

---

## 2. Diccionario de Términos

### Carga asignada

Conjunto de empresas que DISEL asigna a un Crítico Verificador para realizar seguimiento, asistencia, validación y crítica durante la ejecución de la EDO 2026.

La carga constituye el universo de trabajo operativo del crítico dentro del proyecto.

---

### Empresa

Organización formal privada incluida en la muestra de la EDO 2026 y asignada al crítico como parte de su carga de trabajo.

Es el elemento central del dominio.

Sobre una empresa pueden realizarse:

- contactos;
- seguimientos;
- asistencias;
- consultas;
- investigaciones;
- registro de incidencias;
- procesos de crítica y validación.

La empresa tiene una **Situación de Empresa** obtenida del aplicativo interno mediante la descarga diaria de la carga asignada y el cruce por RUC. Esta clasificación institucional es distinta del Estado de Encuesta, del Estado de Crítica y del Estado de Contacto.

---

### Informante

Persona de la empresa que proporciona, confirma o aclara información relacionada con la encuesta.

Generalmente corresponde a personal que conoce la política de recursos humanos o el funcionamiento de la empresa, como:

- Jefe de Recursos Humanos;
- Gerente;
- Administrador;
- otro funcionario autorizado.

Una empresa puede contar con un informante principal y otros contactos de apoyo.

Para el Directorio, el contacto principal aporta el nombre, teléfono y correo que se muestran en la tabla. Cada contacto puede tener un Estado de Contacto y una confirmación de correo propios.

---

### Situación de Empresa

Clasificación de la empresa obtenida del aplicativo interno. Se actualiza a partir de la descarga diaria de las empresas asignadas y su cruce por RUC. Su catálogo codificado es:

- 1 — Completado
- 2 — Fusionada/Absorbida
- 3 — Paralizada
- 4 — Liquidada
- 5 — De baja
- 6 — Suspensión temporal
- 7 — Empresas del Estado
- 8 — No ingresó al aplicativo a gestionar la encuesta
- 9 — Se negó a dar información (rechazo)
- 10 — No ubicada
- 11 — En proceso: quedó pendiente de terminar; pese a la insistencia, nunca terminó.

Esta clasificación describe la situación reportada por el aplicativo interno y no reemplaza los estados operativos que mantiene la bitácora.

---

### Estado de Contacto

Situación de la gestión de contacto con una persona informante. Sus valores son: Pendiente, Contactado, No contesta y Número incorrecto.

---

### Correo confirmado

Indicador asociado al correo de un contacto que señala si este fue confirmado. Sus valores son Sí y No.

---

### Acceso a WhatsApp

Enlace derivado del teléfono del informante que permite abrir un chat de WhatsApp. El enlace usa el formato `https://wa.me/<número>` con el número internacional compuesto únicamente por dígitos. Para un celular peruano registrado en formato local de nueve dígitos se antepone el código de país 51; si el número ya incluye ese código, no se duplica. Si no hay un teléfono utilizable, no se genera un enlace activo. El enlace facilita abrir el chat, pero no envía mensajes automáticamente.

---

### Actividad

Gestión realizada por el Crítico Verificador relacionada con una empresa.

Puede corresponder, entre otras, a:

- llamadas;
- mensajes por WhatsApp;
- correos;
- atención de consultas;
- asesorías;
- seguimientos;
- coordinaciones;
- investigaciones.

Las actividades conforman la bitácora histórica del trabajo realizado con cada empresa.

---

### Medio de contacto

Canal mediante el cual se desarrolla una actividad.

Ejemplos:

- WhatsApp;
- correo;
- llamada;
- presencial;
- otros medios.

---

### Categoría de actividad

Clasificación funcional de una actividad según el propósito de la gestión realizada.

Ejemplos:

- primer contacto;
- seguimiento;
- consulta;
- asesoría;
- investigación;
- coordinación;
- Gestión de incidencia (llamada, correo, investigación o consulta realizada para atenderla).

---

### Incidencia

Situación anómala, problema o inconsistencia que requiere atención especial durante el seguimiento o la crítica de una empresa.

Puede presentarse, por ejemplo, cuando:

- una empresa no puede ser localizada;
- existe información contradictoria;
- se requiere confirmación adicional;
- aparece un problema durante el llenado o validación de la encuesta.

Cada incidencia pertenece a uno de dos ámbitos: Seguimiento de encuesta o Crítica. Las de seguimiento se asocian a la gestión operativa de la empresa; las de crítica se asocian al caso específico que afectan. Ambas tienen un ciclo de vida independiente de los estados de la empresa: Abierta, En gestión o Resuelta. Al resolverla, se registra la fecha de cierre y cómo se atendió, conservando el historial.

---

### Crítica

Proceso de revisión y control de calidad de la información registrada en la encuesta.

Durante la crítica, el Crítico Verificador analiza la coherencia de los datos y verifica que las variables sujetas a codificación o consistencia estén correctamente registradas.

La crítica puede producir una validación o una recodificación.

Cada caso de crítica se vincula con el registro específico de la encuesta que se analiza. En el caso de una ocupación, se refiere a una ocupación concreta del formulario 3.2. Cuando sea pertinente, el caso conserva el contexto utilizado como evidencia: tareas, nivel educativo, CIIU y remuneración.

---

### Validación

Resultado de la crítica en el que se determina que la información registrada es correcta y puede mantenerse.

La validación no implica necesariamente modificar el dato original.

---

### Recodificación

Resultado de la crítica en el que se determina que una variable debe ser modificada o asignada nuevamente de acuerdo con los criterios y clasificadores utilizados por la EDO.

Puede aplicarse, entre otros, a:

- actividad económica;
- ocupaciones;
- carreras;
- capacitaciones.

---

### Clasificadores oficiales

Instrumentos utilizados para ordenar y codificar información de la EDO.

Los principales son:

- CIIU Rev. 4 — Actividades económicas;
- CNO 2015 — Ocupaciones;
- Clasificador Nacional de Programas de Educación Superior 2018;
- Clasificador de Cursos de Capacitación.

Estos clasificadores constituyen referencias técnicas para el proceso de crítica y recodificación.

---

### Sustento metodológico

Información que permite explicar y respaldar una decisión tomada durante el proceso de crítica.

El sustento puede incluir:

- información proporcionada por el informante;
- información registrada en la encuesta;
- descripción de tareas o funciones;
- clasificadores oficiales;
- análisis realizado por el crítico;
- otras fuentes o criterios válidos.

Su finalidad es conservar trazabilidad sobre el motivo de una validación o recodificación.

Toda decisión debe tener una justificación. Para una validación, basta una explicación concisa de por qué se mantiene el valor original; para una recodificación, debe explicar el cambio realizado.

---

### Estado de Encuesta

Situación operativa en la que se encuentra una empresa respecto al proceso de llenado y seguimiento de la EDO.

Representa el avance de la empresa dentro de la etapa de recolección de información.

---

### Estado de Crítica

Situación en la que se encuentra una empresa dentro del proceso posterior de revisión, consistencia y validación.

Es independiente del Estado de Encuesta.

No incluye un estado “Con incidencia”. Tampoco se agrega “Con incidencia” al Estado de Encuesta. La presencia de incidencias abiertas se deriva de sus registros y se calcula por ámbito.

---

### Respaldo local

Copia recuperable de la base de datos guardada localmente, con fecha identificable y con los registros necesarios para restaurar la información y su trazabilidad.

---

---

## 3. Relaciones del Dominio

```text
DISEL
  │
  └── asigna
        │
        ▼
   [CARGA ASIGNADA]
        │
        └── contiene
              │
              ▼
          [EMPRESA]
              │
              ├── tiene situación institucional actualizada por RUC
              │
              ├── tiene ──> [INFORMANTES]
              │                 ├── Estado de Contacto
              │                 └── Correo confirmado
              │
              ├── genera ──> [ACTIVIDADES]
              │                 │
              │                 ├── usa ──> [MEDIO]
              │                 └── tiene ──> [CATEGORÍA]
              │
              ├── puede presentar ──> [INCIDENCIAS]
              │                         ├── ámbito: seguimiento o crítica
              │                         └── tienen estado, fecha de cierre y resolución
              │
              └── entra a ──> [CRÍTICA]
                                 │
                                 ├── contiene casos vinculados a registros concretos de la encuesta
                                 │     └── pueden tener incidencias asociadas
                                 │
                                 ├── produce ──> [VALIDACIÓN]
                                 │
                                 └── produce ──> [RECODIFICACIÓN]
                                                    │
                                                    ├── usa ──> [CLASIFICADORES]
                                                    │
                                                    └── requiere ──> [SUSTENTO]
