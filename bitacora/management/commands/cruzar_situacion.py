import re
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from bitacora.models import Empresa, SituacionEmpresa


def normalize_ruc(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    digits = re.sub(r"\D", "", text)
    return digits if len(digits) == 11 else ""


def normalize_situation(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    match = re.match(r"^(\d{1,2})(?:\s|[-.:])", text)
    code = match.group(1) if match else text
    valid_codes = {choice for choice, _label in SituacionEmpresa.choices}
    return code if code in valid_codes else ""


class Command(BaseCommand):
    help = "Cruza un archivo institucional con las empresas por RUC y actualiza su situación."

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=Path)
        parser.add_argument("--col-ruc", default="RUC", help="Nombre exacto de la columna con RUC.")
        parser.add_argument(
            "--col-situacion", default="Situación de empresas",
            help="Nombre exacto de la columna con el código o etiqueta de situación.",
        )
        parser.add_argument("--hoja", help="Nombre o índice de hoja Excel; por defecto, la primera.")
        parser.add_argument("--dry-run", action="store_true", help="Valida y muestra el cruce sin guardar cambios.")

    def handle(self, *args, **options):
        source = options["archivo"]
        if not source.is_file():
            raise CommandError(f"No existe el archivo: {source}")

        try:
            if source.suffix.lower() in {".xlsx", ".xlsm", ".xls"}:
                sheet = options["hoja"]
                if sheet and sheet.isdigit():
                    sheet = int(sheet)
                dataframe = pd.read_excel(source, sheet_name=sheet or 0, dtype=str)
            elif source.suffix.lower() == ".csv":
                dataframe = pd.read_csv(source, dtype=str)
            else:
                raise CommandError("Formato no admitido. Usa un archivo Excel o CSV.")
        except (OSError, ValueError, ImportError) as exc:
            raise CommandError(f"No se pudo leer el archivo: {exc}") from exc

        for column in (options["col_ruc"], options["col_situacion"]):
            if column not in dataframe.columns:
                available = ", ".join(map(str, dataframe.columns))
                raise CommandError(f"No se encontró la columna «{column}». Columnas disponibles: {available}")

        dataframe = dataframe[[options["col_ruc"], options["col_situacion"]]].copy()
        dataframe["ruc_normalizado"] = dataframe[options["col_ruc"]].map(normalize_ruc)
        dataframe["situacion_normalizada"] = dataframe[options["col_situacion"]].map(normalize_situation)
        invalid = dataframe[
            (dataframe["ruc_normalizado"] == "") | (dataframe["situacion_normalizada"] == "")
        ]
        duplicate_mask = dataframe["ruc_normalizado"].duplicated(keep=False) & (dataframe["ruc_normalizado"] != "")
        duplicates = dataframe[duplicate_mask]
        if not invalid.empty or not duplicates.empty:
            details = []
            if not invalid.empty:
                details.append(f"{len(invalid)} fila(s) sin RUC de 11 dígitos o situación válida")
            if not duplicates.empty:
                details.append(f"{duplicates['ruc_normalizado'].nunique()} RUC duplicado(s) en el archivo")
            examples = invalid.head(5).to_dict(orient="records")
            raise CommandError("; ".join(details) + (f". Ejemplos inválidos: {examples}" if examples else "."))

        companies = Empresa.objects.in_bulk(dataframe["ruc_normalizado"].tolist(), field_name="ruc")
        matched = []
        unmatched = []
        update_date = timezone.localdate()
        for row in dataframe.to_dict(orient="records"):
            company = companies.get(row["ruc_normalizado"])
            if company is None:
                unmatched.append(row["ruc_normalizado"])
                continue
            company.situacion_empresa = row["situacion_normalizada"]
            company.situacion_actualizada_en = update_date
            matched.append(company)

        if not options["dry_run"]:
            with transaction.atomic():
                for company in matched:
                    company.save(update_fields=["situacion_empresa", "situacion_actualizada_en"])

        mode = "Cruce validado" if options["dry_run"] else "Situaciones actualizadas"
        self.stdout.write(self.style.SUCCESS(f"{mode}: {len(matched)} empresa(s)."))
        self.stdout.write(f"RUC del archivo sin coincidencia en el directorio: {len(unmatched)}.")
        if unmatched:
            self.stdout.write("Sin coincidencia: " + ", ".join(unmatched[:20]))
