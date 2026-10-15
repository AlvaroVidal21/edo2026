import shutil
import subprocess
from pathlib import Path
import os

from django.conf import settings

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restaura un respaldo local de PostgreSQL y reemplaza los objetos que coincidan."

    def add_arguments(self, parser):
        parser.add_argument("--archivo", required=True, type=Path, help="Archivo .dump creado con respaldar_db")
        parser.add_argument("--confirmar", action="store_true", help="Confirma que se reemplazarán los datos actuales.")

    def handle(self, *args, **options):
        source = options["archivo"]
        if not source.is_file():
            raise CommandError(f"No existe el archivo: {source}")
        if not options["confirmar"]:
            raise CommandError("La restauración reemplaza datos actuales. Repite el comando con --confirmar.")
        runtime_name = os.getenv("POSTGRES_RUNTIME", "podman")
        runtime = shutil.which(runtime_name) or shutil.which("podman") or shutil.which("docker")
        if not runtime:
            raise CommandError("No se encontró Podman ni Docker para ejecutar pg_restore en el contenedor local.")
        container = os.getenv("POSTGRES_CONTAINER", "fedora_postgres")
        database = settings.DATABASES["default"]["NAME"]

        command = [
            runtime, "exec", "-i", "-u", "postgres", container,
            "pg_restore", "--clean", "--if-exists", "--no-owner", "--single-transaction",
            "-d", database,
        ]
        try:
            with source.open("rb") as backup_file:
                result = subprocess.run(command, stdin=backup_file, stderr=subprocess.PIPE, check=False)
        except OSError as exc:
            raise CommandError(f"No se pudo leer el respaldo: {exc}") from exc
        if result.returncode:
            raise CommandError(result.stderr.decode(errors="replace").strip() or "pg_restore no pudo restaurar la copia.")

        self.stdout.write(self.style.SUCCESS(f"Base restaurada desde: {source}"))
