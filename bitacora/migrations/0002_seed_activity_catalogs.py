from django.db import migrations


def seed_catalogs(apps, schema_editor):
    Medio = apps.get_model("bitacora", "Medio")
    CategoriaActividad = apps.get_model("bitacora", "CategoriaActividad")
    Medio.objects.bulk_create(
        [Medio(nombre=name) for name in ["WhatsApp", "Correo", "Llamada", "Reunión virtual", "Presencial", "Otro"]],
        ignore_conflicts=True,
    )
    CategoriaActividad.objects.bulk_create(
        [
            CategoriaActividad(nombre=name)
            for name in [
                "Primer contacto", "Seguimiento", "Consulta", "Asesoría",
                "Investigación", "Coordinación", "Gestión de incidencia", "Otro",
            ]
        ],
        ignore_conflicts=True,
    )


def unseed_catalogs(apps, schema_editor):
    apps.get_model("bitacora", "Medio").objects.filter(
        nombre__in=["WhatsApp", "Correo", "Llamada", "Reunión virtual", "Presencial", "Otro"]
    ).delete()
    apps.get_model("bitacora", "CategoriaActividad").objects.filter(
        nombre__in=["Primer contacto", "Seguimiento", "Consulta", "Asesoría", "Investigación", "Coordinación", "Gestión de incidencia", "Otro"]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("bitacora", "0001_initial")]
    operations = [migrations.RunPython(seed_catalogs, unseed_catalogs)]
