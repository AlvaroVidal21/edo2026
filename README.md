# Bitácora EDO 2026

Aplicación local para el seguimiento de empresas y el sustento de crítica de la EDO 2026.

## Inicio local

Requisitos: Python 3.12 o superior, `uv`, Node.js/npm y el contenedor PostgreSQL local.

1. Inicia tu contenedor PostgreSQL: `podman start fedora_postgres`.
2. Copia `.env.example` como `.env` y define una clave `SECRET_KEY` y las credenciales PostgreSQL locales.
3. Instala dependencias: `uv sync` y `npm ci`.
4. Prepara la base: `uv run python manage.py migrate`.
5. Ejecuta: `uv run python manage.py runserver` y abre `http://127.0.0.1:8000/`.

El cruce diario de la situación institucional se realiza con `uv run python manage.py cruzar_situacion archivo.xlsx --col-ruc RUC --col-situacion "Situación de empresas"`. Usa `--dry-run` para revisar el cruce sin guardar.
Para respaldar la base: `uv run python manage.py respaldar_db`. Para restaurar, usa `uv run python manage.py restaurar_db --archivo backups/nombre.dump --confirmar`.

Los catálogos de medios y categorías de actividad vienen precargados y se administran desde `/admin/`.

Para cargar el directorio desde el Excel de asignación: `uv run python manage.py importar_carga /ruta/carga.xlsx --dry-run`. Revisa el resumen y ejecuta sin `--dry-run` para guardar. El importador valida la estructura por columna y bloque, cruza contactos actualizados, base/envío 2026, Planilla 2025, EDO 2025, EDO 2024 y SUNAFIL, separa listas de canales y conserva los originales y su procedencia en cada empresa. Las recargas preservan ediciones locales y estados de gestión. La situación institucional se presenta separada de la disponibilidad de contactos; un código `0` no significa que una empresa carezca de correo o teléfono.
Para administrar los catálogos, crea una cuenta local con `uv run python manage.py createsuperuser`.
El diseño de Incidencia sigue pendiente según la decisión documentada en [04_entidades.md](docs/04_entidades.md); la primera versión cubre Dashboard, Directorio, Actividades y Sustento de crítica.

## Demostración del primer entregable

La base `bitacora_demo` contiene una copia del directorio y un escenario ilustrativo de tres días: 36 empresas contactadas (19,9% de 181), 9 intentos sin respuesta, 12 asistencias dentro de las contactadas y 3 casos de crítica pendientes. Son 45 empresas gestionadas y 57 actividades. El límite del 20% se aplica al contacto efectivo; las reiteraciones no duplican empresas.

Para preparar una base de demostración vacía ya creada en PostgreSQL:

```bash
DEMO_MODE=true DB_NAME=bitacora_demo uv run python manage.py migrate
DEMO_MODE=true DB_NAME=bitacora_demo uv run python manage.py importar_carga /ruta/carga.xlsx
DEMO_MODE=true DB_NAME=bitacora_demo uv run python manage.py preparar_demo --contactadas 36
DEMO_MODE=true DB_NAME=bitacora_demo uv run python manage.py runserver 127.0.0.1:8011
```

El dashboard de demostración se muestra en `http://127.0.0.1:8011/`; la bitácora real se mantiene en `http://127.0.0.1:8010/`. El modo demo requiere una base cuyo nombre contenga `demo`, muestra un aviso en todas las vistas y etiqueta las exportaciones. Sus gestiones simuladas sirven para probar la presentación y no acreditan ejecución real. No se programan acciones futuras del modelo de informe.
