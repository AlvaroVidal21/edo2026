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

---

### Informante

Persona de la empresa que proporciona, confirma o aclara información relacionada con la encuesta.

Generalmente corresponde a personal que conoce la política de recursos humanos o el funcionamiento de la empresa, como:

- Jefe de Recursos Humanos;
- Gerente;
- Administrador;
- otro funcionario autorizado.

Una empresa puede contar con un informante principal y otros contactos de apoyo.

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
- recordatorio;
- investigación;
- coordinación;
- incidencia.

---

### Incidencia

Situación anómala, problema o inconsistencia que requiere atención especial durante el seguimiento o la crítica de una empresa.

Puede presentarse, por ejemplo, cuando:

- una empresa no puede ser localizada;
- existe información contradictoria;
- se requiere confirmación adicional;
- aparece un problema durante el llenado o validación de la encuesta.

---

### Crítica

Proceso de revisión y control de calidad de la información registrada en la encuesta.

Durante la crítica, el Crítico Verificador analiza la coherencia de los datos y verifica que las variables sujetas a codificación o consistencia estén correctamente registradas.

La crítica puede producir una validación o una recodificación.

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

---

### Estado de Encuesta

Situación operativa en la que se encuentra una empresa respecto al proceso de llenado y seguimiento de la EDO.

Representa el avance de la empresa dentro de la etapa de recolección de información.

---

### Estado de Crítica

Situación en la que se encuentra una empresa dentro del proceso posterior de revisión, consistencia y validación.

Es independiente del Estado de Encuesta.

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
              ├── tiene ──> [INFORMANTES]
              │
              ├── genera ──> [ACTIVIDADES]
              │                 │
              │                 ├── usa ──> [MEDIO]
              │                 └── tiene ──> [CATEGORÍA]
              │
              ├── puede presentar ──> [INCIDENCIAS]
              │
              └── entra a ──> [CRÍTICA]
                                 │
                                 ├── produce ──> [VALIDACIÓN]
                                 │
                                 └── produce ──> [RECODIFICACIÓN]
                                                    │
                                                    ├── usa ──> [CLASIFICADORES]
                                                    │
                                                    └── requiere ──> [SUSTENTO]