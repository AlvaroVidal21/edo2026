from collections import defaultdict, deque
from datetime import date, time, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from bitacora.models import (
    Actividad,
    CategoriaActividad,
    Critica,
    Empresa,
    EstadoContacto,
    EstadoCritica,
    EstadoEncuesta,
    Medio,
)

MARKER = "[DEMO-ENTREGABLE]"


def representative_order(companies):
    regions = defaultdict(deque)
    for company in companies:
        regions[company.region].append(company)
    result = []
    while any(regions.values()):
        for region in sorted(regions):
            if regions[region]:
                result.append(regions[region].popleft())
    return result


class Command(BaseCommand):
    help = "Prepara tres días de gestiones simuladas en una base de demostración separada."

    def add_arguments(self, parser):
        parser.add_argument("--contactadas", type=int, default=36)
        parser.add_argument("--fecha-corte", type=date.fromisoformat, default=timezone.localdate())

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEMO_MODE:
            raise CommandError("Este comando requiere DEMO_MODE=true y una base de demostración separada.")
        total = Empresa.objects.count()
        contacted_condition = Q(contacto_principal_estado=EstadoContacto.CONTACTADO) | Q(contacto_alternativo_estado=EstadoContacto.CONTACTADO)
        requested = options["contactadas"]
        if not total or requested < 0 or requested * 5 > total:
            raise CommandError(f"Máximo permitido: {total // 5} contactadas sobre {total} empresas (20%).")
        if options["fecha_corte"] > timezone.localdate():
            raise CommandError("La fecha de corte no puede ser posterior a hoy.")
        if Actividad.objects.exclude(descripcion__startswith=MARKER).exists() or Critica.objects.exclude(evidencia__startswith=MARKER).exists():
            raise CommandError("La base contiene registros ajenos al escenario de demostración.")
        if Actividad.objects.filter(descripcion__startswith=MARKER).exists():
            effective = Empresa.objects.filter(contacted_condition).count()
            if effective != requested:
                raise CommandError("Ya existe otro escenario. Usa una copia de demostración nueva para cambiarlo.")
            self.stdout.write("El escenario ya está preparado; no se duplicaron gestiones.")
            return

        available = list(Empresa.objects.exclude(contacto_principal_telefono="").order_by("ruc"))
        named = representative_order([company for company in available if company.contacto_principal_nombre])
        if len(named) < requested:
            raise CommandError("No hay suficientes empresas con informante y teléfono para este escenario.")
        contacted = named[:requested]
        contacted_ids = {company.pk for company in contacted}
        unanswered = representative_order([company for company in available if company.pk not in contacted_ids])[:9]
        calls = Medio.objects.get(nombre="Llamada")
        whatsapp = Medio.objects.get(nombre="WhatsApp")
        mail = Medio.objects.get(nombre="Correo")
        first = CategoriaActividad.objects.get(nombre="Primer contacto")
        assistance = CategoriaActividad.objects.get(nombre="Asesoría")
        start = options["fecha_corte"] - timedelta(days=2)

        for index, company in enumerate(contacted):
            day = start + timedelta(days=index % 3)
            channel = whatsapp if index % 3 == 0 and company.whatsapp_url else calls
            Actividad.objects.create(
                empresa=company, medio=channel, categoria=first, fecha=day,
                hora=time(9 + (index // 3) // 3, ((index // 3) % 3) * 15),
                descripcion=f"{MARKER} Contacto efectivo simulado: presentación de la EDO 2026, identificación del informante y consulta sobre recepción de accesos. Registro de prueba.",
            )
            company.contacto_principal_estado = EstadoContacto.CONTACTADO
            company.contacto_principal_correo_confirmado = bool(company.contacto_principal_correo) and channel == calls
            company.estado_encuesta = EstadoEncuesta.EN_SEGUIMIENTO
            company._change_reason = "Demostración: contacto simulado, sin gestión real acreditada."
            company.save()
            if index < 12 and company.contacto_principal_correo:
                Actividad.objects.create(
                    empresa=company, medio=mail, categoria=assistance, fecha=day,
                    hora=time(14, (index // 3) * 10),
                    descripcion=f"{MARKER} Asistencia simulada: orientación sobre acceso al aplicativo e interpretación de preguntas del formulario. Llenado pendiente; registro de prueba.",
                )
            if index < 3:
                Critica.objects.create(
                    empresa=company, variable_analizada="Cargo del contacto",
                    registro_referencia="Contacto principal · caso de demostración",
                    valor_original=company.contacto_principal_cargo or "Cargo no informado en la fuente",
                    evidencia=f"{MARKER} Texto original del directorio; análisis ilustrativo sin confirmación del informante.",
                    metodo_analisis="Revisión ilustrativa del cargo y sus funciones",
                    justificacion="Caso de prueba: se requiere confirmar las funciones del cargo antes de decidir su validación o recodificación.",
                    nivel_confianza=Critica.NivelConfianza.BAJA,
                )
                company.estado_critica = EstadoCritica.EN_ANALISIS
                company.save()

        for index, company in enumerate(unanswered):
            Actividad.objects.create(
                empresa=company, medio=calls, categoria=first,
                fecha=start + timedelta(days=index % 3), hora=time(12, (index // 3) * 15),
                descripcion=f"{MARKER} Intento de contacto simulado sin respuesta. No se acredita contacto efectivo. Registro de prueba.",
            )
            company.contacto_principal_estado = EstadoContacto.NO_CONTESTA
            company._change_reason = "Demostración: intento sin respuesta simulado."
            company.save()

        effective = Empresa.objects.filter(contacted_condition).count()
        if effective * 5 > total:
            raise CommandError("El escenario superaría el 20% de contacto efectivo; se revirtió la operación.")
        managed = Actividad.objects.values("empresa_id").distinct().count()
        self.stdout.write(self.style.SUCCESS(
            f"Demostración preparada: {total} empresas, {managed} con gestión, {effective} contactadas "
            f"({effective / total:.1%}), {Actividad.objects.count()} actividades y {Critica.objects.count()} casos ilustrativos."
        ))
