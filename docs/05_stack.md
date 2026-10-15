# 05_stack.md — Stack Tecnológico y Arquitectura de Implementación

## 1. Propósito

Definir el stack tecnológico seleccionado para la **Bitácora Laboral y Sustento de Crítica EDO 2026**, detallando cada componente y justificando su elección en función de los requisitos del negocio, las restricciones operativas y el entorno de ejecución local.

---

## 2. Resumen del Stack

| Capa / Componente | Tecnología | Justificación Clave |
| :--- | :--- | :--- |
| **Base de Datos** | **PostgreSQL** (con driver `psycopg` v3) | Integridad referencial estricta (`ON DELETE RESTRICT`), soporte nativo para restricciones complejas (`CHECK`), búsqueda por trigramas (`pg_trgm`) y base para clasificadores futuros (`pgvector`). Requisito no negociable. |
| **Lenguaje** | **Python 3.12+** | Ecosistema óptimo para manipulación de datos tabulares (Excel/CSV), procesamiento analítico y clasificadores asistidos (fase 2). |
| **Framework Backend** | **Django 5.x** | Integración nativa con PostgreSQL (ORM maduro con `CheckConstraint` y `on_delete=PROTECT`), sistema de migraciones robusto, formularios/validaciones del lado del servidor y panel administrativo integrado para catálogos. |
| **Interfaz / Frontend** | **Plantillas Django + HTMX** | Interactividad suficiente (filtros, formularios parciales) sin mantener una SPA separada. Alpine.js queda como opción si una interacción concreta lo requiere. |
| **Diseño / UI** | **Bootstrap 5** | Interfaz responsiva y orientada a formularios y tablas de alta densidad, con estilos servidos localmente desde npm. |
| **Visualización** | **Chart.js** | Ligero y directo para los indicadores y métricas del Dashboard de Supervisión. |
| **Manejo de Datos** | **openpyxl** + **pandas** | Cruce diario por RUC con la carga institucional y exportación estructurada a Excel/CSV. |
| **Gestor de Paquetes / Entorno** | **uv** | Resolución y sincronización ultra-rápida de dependencias con `pyproject.toml` y lockfiles reproducibles. |
| **Trazabilidad / Auditoría** | **django-simple-history** | Registro automático de versiones previas en validaciones y recodificaciones (RN-017, RN-020, RN-032). |
| **Clasificación Asistida (Fase 2)** | **rapidfuzz** + búsqueda vectorial local | Sugerencia de códigos (CIIU, CNO) ejecutada 100% en local sin exponer datos sensibles a APIs externas (RN-034, RN-035). |

---

## 3. Justificación Detallada por Componente

### 3.1 Base de Datos: PostgreSQL

PostgreSQL es el motor relacional central y no negociable del sistema.

- **Integridad referencial y reglas de negocio en la BD:**
  - `ON DELETE RESTRICT`: Protege los catálogos (`Medio`, `CategoriaActividad`) y el historial de actividades frente a borrados accidentales.
  - `CHECK constraints`: Permite validar a nivel de base de datos el formato del RUC (`CHECK (ruc ~ '^\d{11}$')`), la obligatoriedad de justificación en recodificaciones y el cierre formal de incidencias (`fecha_cierre` y `resolucion` no nulos al resolverse).
- **Extensiones especializadas:**
  - `pg_trgm`: Búsquedas difusas sobre razones sociales o descripciones con errores tipográficos.
  - `pgvector` (proyección): Almacenamiento y búsqueda por similitud de descripciones de puestos vs. clasificadores oficiales (CNO 2015, CIIU Rev. 4) en la etapa de crítica asistida.
- **Respaldo y Recuperación Local (RN-038):**
  - Se implementan comandos (`manage.py respaldar_db` / `manage.py restaurar_db`) basados en `pg_dump -Fc` y `pg_restore --clean`, permitiendo generar respaldos portables con marca temporal elegidos por el usuario.
- **Seguridad local (RN-034):**
  - Configurado en `listen_addresses = 'localhost'`, sin exposición en red externa.

### 3.2 Backend: Python 3 + Django

- **ORM alineado a las reglas del dominio:**
  - El ORM de Django traduce directamente las restricciones declaradas en `02_reglas_negocio.md` a través de `CheckConstraint`, `UniqueConstraint` y `on_delete=models.PROTECT`.
- **Panel Administrativo inmediato para Catálogos:**
  - Permite gestionar `Medio` y `CategoriaActividad` (crear, editar nombre/descripción, activar/desactivar) de inmediato sin necesidad de programar vistas CRUD dedicadas para tablas secundarias.
- **Manejo de archivos institucionales:**
  - La descarga diaria de la carga en Excel y el cruce por RUC se realizan de forma natural en Python mediante scripts o comandos de gestión de Django, asegurando que la carga y exportación compartan la misma fuente de verdad (RN-036).

### 3.3 Frontend: Django Templates + HTMX (¿Por qué no una SPA con React?)

Se evaluó la alternativa de una arquitectura desacoplada (FastAPI/Django REST + React) y se descartó por las siguientes razones:

1. **Evita la duplicación de modelos y lógica de validación:**
   - En una SPA, las reglas de formulario y esquemas de datos deben escribirse y mantenerse dos veces (Python y TypeScript/Zod). Con Django + HTMX la validación reside en el servidor como única fuente de verdad.
2. **Sin sobrecarga de "plomería" de API:**
   - La aplicación es una herramienta de uso local y personal para un Crítico Verificador (monousuario). No requiere endpoints de consumo público ni serializadores para cada entidad secundaria.
3. **Mantenimiento y arranque simplificados:**
   - No requiere compilar bundles (`npm run build`, Vite), ni gestionar dos servidores de desarrollo en simultáneo. Un único comando levanta todo el entorno.
4. **Interactividad suficiente:**
   - Las necesidades interactivas (filtrado reactivo de tablas en el Directorio, actualización de estados sin recargar página completa, apertura de modales para registro de actividad y enlaces directos de WhatsApp) se resuelven de forma limpia mediante atributos HTMX (`hx-get`, `hx-post`, `hx-target`, `hx-swap`). Los recursos de Bootstrap, HTMX y Chart.js se sirven localmente.

### 3.4 Resguardo y Trazabilidad: django-simple-history

- Las reglas RN-017, RN-020 y RN-032 exigen que **ninguna recodificación o cambio metodológico destruya el valor original**.
- `django-simple-history` crea tablas shadow (`HistoricalCritica`, `HistoricalEmpresa`) que auditan automáticamente cada cambio, quién lo hizo, cuándo y qué valor cambió, garantizando reconstrucción histórica completa para el informe final sin sobrecargar la estructura de las tablas principales.

---

## 4. Arquitectura de Despliegue Local

```text
[ Navegador Web ]
       │
       ▼  (HTTP / localhost)
[ Django App (Gunicorn / Runserver local) ]
   ├── Django Templates + HTMX
   ├── Lógica de Dominio y Validaciones
   ├── Servicios de Cruce / Exportación (openpyxl/pandas)
   └── Auditoría (django-simple-history)
       │
       ▼  (Conexión local / TCP 5432 o socket unix)
[ PostgreSQL (localhost) ]
   ├── Esquema relacional con restricciones CHECK
   ├── Catálogos protegidos (PROTECT / RESTRICT)
   └── Respaldos periódicos (pg_dump / pg_restore)
```

---

## 5. Estrategia de Implementación Inicial

1. **Configuración de base de datos:** Creación de base de datos local y usuario específico en PostgreSQL.
2. **Inicialización del proyecto Django:** Configuración del entorno virtual, dependencias (`psycopg`, `django`, `django-htmx`, `openpyxl`, `django-simple-history`) y variables de entorno (`.env`).
3. **Modelado de datos:**
   - Mapear las tablas de `04_entidades.md` aplicando restricciones `CHECK` y claves foráneas `PROTECT`.
   - Resolver inconsistencias identificadas (detalles de múltiples contactos vs. columnas planas, e incorporación explícita de la entidad `Incidencia`).
4. **Comandos de respaldo y carga:**
   - Implementar `manage.py cruzar_carga` y `manage.py respaldar_db`.
