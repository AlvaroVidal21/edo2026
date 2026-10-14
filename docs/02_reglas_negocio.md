# Reglas de negocio

## 1. Reglas sobre Empresas

### RN-001 — Una empresa se identifica mediante su RUC

Cada empresa debe identificarse mediante un RUC válido y único dentro de la carga.

### RN-002 — No se permiten empresas duplicadas en una carga

No deben existir dos empresas diferentes dentro de la misma carga con el mismo RUC.

## 2. Estados de la empresa

### RN-003 — Una empresa mantiene dos estados independientes

Cada empresa debe poder tener simultáneamente:

- un Estado de Encuesta;
- un Estado de Crítica.

Ambos representan procesos diferentes.

Ejemplo válido:

```text
Estado de Encuesta: Encuesta finalizada
Estado de Crítica: En análisis
```

Modificar un estado no implica modificar automáticamente el otro, salvo reglas explícitas definidas posteriormente.

La Situación de Empresa que proviene del aplicativo interno y el Estado de Contacto de cada informante son datos independientes. No deben sustituir ni actualizar automáticamente el Estado de Encuesta o el Estado de Crítica.

## 3. Reglas sobre Informantes

### RN-004 — Un informante pertenece a una empresa

Todo informante registrado debe estar relacionado con una empresa de la carga.

### RN-005 — Una empresa puede tener más de un informante

Una empresa puede registrar:

- un informante principal;
- uno o más contactos adicionales cuando resulte necesario.

El sistema debe permitir distinguir cuál es el contacto principal.

Cada informante debe poder registrar su Estado de Contacto (Pendiente, Contactado, No contesta o Número incorrecto) y si su correo está confirmado (Sí o No). Estos datos pertenecen al contacto, no a la empresa en general.

## 4. Reglas sobre Actividades

### RN-006 — Toda actividad debe pertenecer a una empresa

No puede existir una actividad de bitácora sin una empresa asociada.

### RN-007 — Toda actividad representa un hecho ocurrido

Una actividad debe registrar una gestión que ya ocurrió.

Ejemplos:

- llamada realizada;
- WhatsApp enviado;
- correo enviado;
- consulta atendida;
- investigación realizada.

Una actividad no debe utilizarse para representar una acción futura. La versión actual no incluye una entidad de recordatorios o próximos pasos; por tanto, el sistema no programa acciones futuras ni determina qué empresa debe contactarse posteriormente.

### RN-008 — Toda actividad debe registrar fecha

Toda actividad debe tener como mínimo:

- fecha;
- empresa;
- categoría;
- medio;
- descripción.

La hora podrá registrarse cuando sea conocida o necesaria para la trazabilidad.

### RN-009 — Medio y Categoría son conceptos independientes

El **Medio** indica cómo ocurrió la actividad. La **Categoría** indica qué tipo de gestión se realizó.

Ejemplo:

```text
Medio: WhatsApp
Categoría: Seguimiento
```

Una categoría no debe implicar automáticamente un medio determinado.

### RN-010 — El historial de actividades debe conservarse

Una actividad forma parte de la trazabilidad histórica del trabajo.

Las actividades no deben sobrescribirse para representar nuevas gestiones. Si ocurre una nueva interacción, debe registrarse una nueva actividad.

## 5. Reglas sobre Incidencias

### RN-011 — Una incidencia debe estar asociada a una empresa

Toda incidencia debe poder identificarse con la empresa afectada.

Además, cada incidencia debe identificar su ámbito: Seguimiento de encuesta o Crítica. Las incidencias de crítica deben vincularse también con el caso de crítica concreto al que afectan. Las incidencias de seguimiento pertenecen a la gestión operativa de la empresa y pueden relacionarse con las actividades que las atienden.

### RN-012 — Una incidencia representa una situación que requiere atención

Una incidencia no es simplemente una actividad. Representa un problema, bloqueo, inconsistencia o situación excepcional que puede requerir:

- seguimiento;
- investigación;
- consulta;
- confirmación;
- intervención del supervisor.

El ámbito determina dónde se consulta y qué caso atiende: Seguimiento de encuesta corresponde a la gestión operativa y Crítica corresponde a la revisión de datos. No deben mezclarse en un único indicador sin distinguir su ámbito.

### RN-013 — Una incidencia puede generar actividades

Una incidencia puede originar actividades como:

- llamadas;
- mensajes;
- investigaciones;
- consultas;

La resolución de la incidencia no elimina el historial de actividades realizadas.

Toda incidencia debe tener un estado propio:

- Abierta: requiere atención y todavía no está siendo gestionada activamente.
- En gestión: se están realizando acciones para atenderla.
- Resuelta: la situación que la originó fue atendida.

Al pasar a Resuelta, debe registrarse la fecha de cierre y un resumen de cómo se atendió. Una incidencia resuelta conserva su descripción, actividades y demás historial. La existencia de incidencias abiertas se calcula a partir de sus registros y se muestra separada por ámbito; no se almacena como Estado de Encuesta ni como Estado de Crítica de la empresa.

## 6. Reglas sobre el Proceso de Crítica

### RN-014 — La crítica corresponde a información registrada en la encuesta

El proceso de crítica tiene como objeto revisar, consistenciar, validar o recodificar información previamente registrada para una empresa.

### RN-015 — Una empresa puede tener múltiples casos de crítica

Una misma empresa puede requerir revisión de varias variables.

Ejemplo:

```text
Empresa X
    - Ocupación
    - Carrera
    - Capacitación
    - CIIU
    - Remuneración
```

Cada caso debe poder analizarse independientemente.

Cada caso debe apuntar al registro concreto de la encuesta que se está revisando. Para una ocupación, debe identificar una ocupación específica del formulario 3.2, no solamente la empresa y la variable “Ocupación”. Si la fuente no proporciona un identificador estable, el caso debe conservar datos suficientes para distinguir ese registro.

Cuando el caso analice una ocupación, debe poder guardar como evidencia el contexto pertinente del registro, incluyendo descripción de tareas, nivel educativo, actividad económica (CIIU) y remuneración, además de cualquier otra información utilizada según los criterios de codificación.

### RN-016 — Cada caso de crítica debe identificar la variable analizada

Toda revisión debe indicar qué elemento está siendo evaluado.

Ejemplos:

- CIIU;
- CNO;
- carrera;
- capacitación;
- nivel educativo;
- remuneración.

### RN-017 — Debe conservarse el valor original

Cuando un dato sea analizado, el sistema debe preservar el valor recibido originalmente.

El valor original no debe reemplazarse ni perderse al realizar una validación o recodificación.

### RN-018 — Toda decisión debe registrar el valor resultante

El proceso de crítica debe permitir identificar claramente:

```text
Valor original
      |
      v
Análisis
      |
      v
Valor validado o asignado
```

## 7. Reglas sobre Validación y Recodificación

### RN-019 — Una crítica puede concluir en Validación o Recodificación

**Validación**

El dato analizado se considera correcto.

```text
Original = Validado
```

**Recodificación**

El dato o código debe modificarse.

```text
Original != Asignado
```

### RN-020 — Una recodificación nunca debe borrar el valor original

El sistema debe permitir reconstruir:

- qué informó inicialmente la empresa;
- qué valor fue finalmente asignado.

### RN-021 — Toda recodificación debe tener sustento

No debe considerarse completa una recodificación si no existe información suficiente que permita explicar por qué se realizó el cambio.

La exigencia de sustento aplica también a las validaciones. En una validación, la justificación puede ser breve, pero debe indicar por qué se considera correcto mantener el valor original.

## 8. Reglas sobre Sustento Metodológico

### RN-022 — Fuente de evidencia y método de análisis son conceptos distintos

Una decisión puede utilizar una determinada fuente de evidencia y, de manera independiente, aplicar un método de análisis.

Ejemplo:

```text
Fuente: Descripción de tareas registrada por la empresa
Método: Análisis cualitativo
```

### RN-023 — Toda decisión debe poder identificar su evidencia

La decisión debe poder relacionarse con la información utilizada para justificarla.

Ejemplos:

- confirmación del informante;
- información registrada en la encuesta;
- descripción de tareas;
- clasificador oficial;
- documentación autorizada.

### RN-024 — Toda decisión debe registrar una justificación comprensible

La justificación debe permitir que posteriormente otra persona pueda entender:

- qué se observó;
- qué criterio se aplicó;
- por qué se mantuvo o cambió el valor.

No debe limitarse únicamente a registrar el código final.

La justificación es obligatoria tanto para validar como para recodificar. Para una validación puede ser concisa; para una recodificación debe explicar el cambio con el detalle necesario para reconstruir el criterio aplicado.

## 9. Reglas sobre Clasificadores

### RN-025 — Los clasificadores oficiales son referencias técnicas del proceso de crítica

Las variables sujetas a codificación deben contrastarse, cuando corresponda, con los instrumentos oficiales utilizados por la EDO:

- CIIU Rev. 4;
- CNO 2015;
- Clasificador Nacional de Programas de Educación Superior 2018;
- Clasificador de Cursos de Capacitación.

### RN-026 — Un algoritmo no constituye por sí solo una decisión definitiva

En futuras versiones, un clasificador asistido por IA o algoritmo podrá:

- sugerir candidatos;
- calcular similitudes;
- recomendar códigos;
- estimar niveles de confianza.

La decisión definitiva seguirá siendo responsabilidad del Crítico Verificador.

## 10. Reglas sobre Nivel de Confianza y Revisión

### RN-027 — Confianza y Estado de Revisión son conceptos distintos

El nivel de confianza expresa la certeza sobre una conclusión.

Valores iniciales:

- Alta;
- Media;
- Baja.

El Estado de Revisión indica el avance del proceso de validación.

Valores iniciales:

- Revisión requerida;
- Revisado;
- Validado.

Ejemplo válido:

```text
Confianza: Alta
Estado de revisión: Revisión requerida
```

### RN-028 — Una confianza baja debe ser visible

Los casos con confianza baja deben poder identificarse fácilmente para facilitar su revisión o consulta posterior.

## 11. Reglas sobre Estados

### RN-029 — El estado representa la situación actual, no el historial

El Estado de Encuesta y el Estado de Crítica representan el momento actual de una empresa.

El historial de lo ocurrido debe obtenerse mediante actividades y registros de crítica.

La existencia de una incidencia no es un Estado de Encuesta ni un Estado de Crítica. Una empresa puede estar “En análisis” y tener incidencias abiertas de seguimiento, de crítica o de ambos ámbitos. Los indicadores de incidencias abiertas deben derivarse de las incidencias cuyo estado sea Abierta o En gestión y presentarse por separado para cada ámbito.

### RN-030 — Finalizar la encuesta no implica finalizar la crítica

Una empresa puede haber terminado el proceso de llenado y todavía requerir:

- análisis;
- consistencia;
- validación;
- recodificación.

Por tanto:

```text
Encuesta finalizada
        !=
Crítica finalizada
```

## 12. Reglas sobre Trazabilidad

### RN-031 — El sistema debe permitir reconstruir lo ocurrido

Para una empresa debe ser posible conocer:

- qué actividades se realizaron;
- cuándo ocurrieron;
- qué incidencias existieron;
- qué datos fueron analizados;
- qué valores originales existían;
- qué valores fueron finalmente asignados;
- por qué se tomó cada decisión.

### RN-032 — Las correcciones no deben destruir la trazabilidad relevante

Cuando una modificación tenga importancia metodológica, debe conservarse suficiente información para comprender el estado anterior y el resultado final.

## 13. Reglas sobre Confidencialidad

### RN-033 — La información de las empresas es confidencial

La información obtenida durante el servicio no debe divulgarse a personas ajenas al estudio.

La capacitación de la EDO establece expresamente el deber de confidencialidad y el Secreto Estadístico.

### RN-034 — El sistema debe minimizar la exposición externa de datos

La Versión 1 funcionará localmente. Las funciones esenciales no dependerán del envío de información de empresas a servicios externos.

### RN-035 — Los servicios de IA no deben recibir información identificable innecesaria

Si en futuras versiones se utilizan servicios externos de inteligencia artificial, se debe evitar enviar información identificable de empresas cuando no sea necesaria para realizar el análisis.

## 14. Reglas sobre Exportación

### RN-036 — Los datos exportados deben provenir de la información registrada en el sistema

Las exportaciones CSV/XLSX y los indicadores del dashboard deben derivarse de la misma fuente de datos utilizada por la aplicación.

La exportación no constituye una segunda fuente de verdad.

### RN-037 — La estructura de exportación puede diferir del modelo interno

El sistema puede almacenar información de forma relacional y exportarla posteriormente como tablas planas apropiadas para Excel.

Ejemplo:

```text
Base de datos
Empresa - Actividades - Categorías - Medios
              |
              | exportación
              v
Fecha | RUC | Empresa | Medio | Categoría | Descripción
```

## 15. Reglas sobre Respaldo Local

### RN-038 — La base local debe contar con respaldo recuperable

La aplicación debe permitir crear copias de respaldo locales de la base de datos en una ubicación elegida por el usuario. El respaldo debe incluir los registros necesarios para recuperar la trazabilidad del trabajo y poder restaurarse en la aplicación. El usuario debe poder identificar cuándo se generó cada copia.

## 16. Reglas sobre Directorio y Situación de Empresa

### RN-039 — La Situación de Empresa se actualiza desde el aplicativo interno

Para actualizar la situación de las empresas asignadas, el Crítico Verificador debe descargar diariamente del aplicativo interno el listado de su carga y cruzarlo con el Directorio mediante el RUC. La situación obtenida se registra por empresa junto con la fecha de actualización. El RUC es la clave del cruce; la actualización de la Situación de Empresa no modifica los estados de encuesta, crítica o contacto.

La Situación de Empresa conserva los códigos y etiquetas del listado institucional:

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

### RN-040 — Los datos de contacto son propios de cada informante

El Estado de Contacto de cada informante debe admitir únicamente: Pendiente, Contactado, No contesta y Número incorrecto. La confirmación del correo debe admitir Sí o No y registrarse por contacto. La confirmación del correo no se deduce del Estado de Contacto.

### RN-041 — El Directorio muestra únicamente las columnas definidas

La tabla principal del Directorio debe mostrar estas columnas:

- RUC;
- Nombre de contacto;
- Teléfono de contacto;
- Correo de contacto;
- Situación de Empresa;
- Estado de Contacto;
- Correo confirmado.

Para cada empresa se muestran los datos del informante principal. Los demás datos pueden permanecer en el registro y mostrarse en la ficha de detalle, pero no como columnas adicionales de la tabla principal.

## 17. Principios de Negocio del Sistema

El sistema debe mantener separadas cuatro preguntas fundamentales:

| Pregunta | Respuesta del sistema |
| --- | --- |
| ¿Qué ocurrió? | Actividades |
| ¿Dónde se encuentra actualmente la empresa? | Estados |
| ¿Qué se decidió durante la crítica y por qué? | Validación / Recodificación + Sustento |
