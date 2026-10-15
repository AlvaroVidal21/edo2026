import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Guarda una copia local, portable y comprimida de PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument("--archivo", type=Path, help="Ruta de salida; por defecto backups/bitacora-<fecha>.dump")

    def handle(self, *args, **options):
        runtime_name = os.getenv("POSTGRES_RUNTIME", "podman")
        runtime = shutil.which(runtime_name) or shutil.which("podman") or shutil.which("docker")
        if not runtime:
            raise CommandError("No se encontró Podman ni Docker para ejecutar pg_dump en el contenedor local.")
        container = os.getenv("POSTGRES_CONTAINER", "fedora_postgres")
        database = settings.DATABASES["default"]["NAME"]

        output = options["archivo"] or (
            settings.BASE_DIR / "backups" / f"bitacora-{datetime.now().astimezone():%Y%m%d-%H%M%S}.dump"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        command = [
            runtime, "exec", "-u", "postgres", container,
            "pg_dump", "-d", database, "-Fc",
        ]
        try:
            with output.open("wb") as backup_file:
                result = subprocess.run(command, stdout=backup_file, stderr=subprocess.PIPE, check=False)
            if result.returncode:
                output.unlink(missing_ok=True)
                raise CommandError(result.stderr.decode(errors="replace").strip() or "pg_dump no pudo crear la copia.")
        except OSError as exc:
            output.unlink(missing_ok=True)
            raise CommandError(f"No se pudo escribir el respaldo: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(f"Respaldo creado: {output}"))
