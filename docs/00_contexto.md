# 00_contexto.md — Bitácora Laboral y Sustento de Crítica EDO 2026

## 1. Qué es el proyecto

Aplicación web local orientada al trabajo de un **Crítico Verificador de la Encuesta de Demanda Ocupacional (EDO 2026) del MTPE**.

El sistema busca centralizar dos necesidades principales:

1. El seguimiento operativo de las empresas asignadas durante la ejecución de la encuesta.
2. El registro del análisis y sustento técnico utilizado durante la etapa de crítica, validación y recodificación de información.

La aplicación funcionará de manera local y tendrá como prioridad la simplicidad, trazabilidad y resguardo de la información.

---

## 2. Problema que resuelve

### 2.1 Seguimiento operativo

El crítico debe gestionar una carga de empresas y mantener contacto con ellas mediante distintos canales, principalmente:

- WhatsApp
- Correo electrónico
- Llamadas
- Reunión virtual


El uso de múltiples canales dificulta mantener una visión clara de:

- qué empresas ya fueron contactadas;
- cuándo fue la última gestión;
- qué acciones se realizaron;
- qué consultas o incidencias existen;
- cuál es el estado actual de cada empresa;
- qué acción debe realizarse después.

La aplicación debe permitir conservar un historial cronológico y consultable de todas estas gestiones.

### 2.2 Etapa de crítica y validación

Durante la etapa posterior al llenado de la encuesta, el crítico debe revisar, validar, consistenciar y, cuando corresponda, recodificar información registrada por las empresas.

El sistema institucional puede conservar información sobre los códigos modificados, pero existe la necesidad adicional de registrar de manera estructurada:

- qué variable fue revisada;
- cuál era el valor original;
- cuál fue el valor finalmente validado o asignado;
- qué evidencia sustentó la decisión;
- qué método de análisis se utilizó;
- cuál fue el nivel de confianza del análisis;
- si la decisión requiere o recibió revisión humana;
- una explicación breve del criterio aplicado.

El objetivo es conservar una trazabilidad técnica de las decisiones realizadas durante la crítica.

---

## 3. Objetivo general

Construir una aplicación local que permita al Crítico Verificador:

- controlar su carga de empresas;
- registrar actividades de seguimiento;
- conocer rápidamente el estado de cada empresa;
- documentar incidencias;
- registrar y sustentar decisiones de crítica y recodificación;
- generar información exportable;
- visualizar indicadores de avance mediante un dashboard.

La aplicación debe facilitar la preparación de reportes, supervisiones e insumos para el Informe Final.

---

## 4. Usuarios del sistema

### 4.1 Crítico Verificador

Usuario principal del sistema.

Puede:

- administrar empresas;
- registrar y actualizar contactos;
- registrar actividades;
- modificar estados;
- documentar incidencias;
- registrar análisis y sustentos de crítica;
- consultar el dashboard;
- exportar información.

### 4.2 Supervisor o usuario externo

En la Versión 1 no tendrá una cuenta propia ni acceso remoto al sistema.

El crítico podrá:

- mostrar el dashboard desde su equipo;
- generar exportaciones;
- presentar tablas, indicadores o sustentos durante la supervisión.

El acceso multiusuario o remoto queda fuera del alcance inicial.

---

## 5. Estructura funcional de la aplicación

La aplicación se organizará inicialmente en cuatro secciones principales:

1. Directorio
2. Actividades
3. Sustento de Crítica
4. Dashboard de Supervisión

---

## 6. Alcance de la Versión 1 — MVP

### 6.1 Sección 1 — Directorio

Permitirá administrar las empresas asignadas.

Datos básicos considerados inicialmente:

- RUC
- Razón social
- Región
- Actividad económica / CIIU
- Informante principal
- Informante adicional
- Cargo
- Correo electrónico
- Teléfono o celular

Cada empresa tendrá dos estados independientes.

### Estado de Encuesta

Representa el avance operativo del proceso de levantamiento.

Estados iniciales:

- Sin datos / En búsqueda
- Por contactar
- En seguimiento / Llenando
- Encuesta finalizada

### Estado de Crítica

Representa el avance del proceso posterior de revisión y validación.

Estados iniciales:

- Sin iniciar
- En análisis
- Con incidencia
- Validada / Cerrada

Estos estados son independientes.

Ejemplo:

```text
Estado de Encuesta: Encuesta finalizada
Estado de Crítica: En análisis