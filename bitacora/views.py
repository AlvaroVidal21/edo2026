from django.contrib import messages
from django.db.models import Count, Max, Min, Q
from django.shortcuts import get_object_or_404, redirect, render

from .exports import tabular_export
from .forms import ActividadForm, CriticaForm, EmpresaForm
from .models import (
    Actividad,
    CategoriaActividad,
    Critica,
    Empresa,
    EstadoContacto,
    Medio,
    SituacionEmpresa,
)


def dashboard(request):
    total = Empresa.objects.count()
    managed_ids = Actividad.objects.values("empresa_id")
    contacted_condition = Q(contacto_principal_estado=EstadoContacto.CONTACTADO) | Q(contacto_alternativo_estado=EstadoContacto.CONTACTADO)
    contacted = Empresa.objects.filter(contacted_condition)
    others = Empresa.objects.exclude(contacted_condition)
    waiting = others.exclude(pk__in=managed_ids)
    no_channels = Q(contacto_principal_correo="", contacto_principal_telefono="",
                    contacto_alternativo_correo="", contacto_alternativo_telefono="")
    report = [
        {"label": "Contacto efectivo", "total": contacted.count()},
        {"label": "Con gestión, sin contacto efectivo", "total": others.filter(pk__in=managed_ids).count()},
        {"label": "Por gestionar · con datos", "total": waiting.exclude(no_channels).count()},
        {"label": "Sin canales de contacto", "total": waiting.filter(no_channels).count()},
    ]
    for item in report:
        item["porcentaje"] = item["total"] * 100 / total if total else 0
    period = Actividad.objects.aggregate(desde=Min("fecha"), hasta=Max("fecha"))
    empresas_sin_correo = Empresa.objects.filter(
        Q(contacto_principal_correo="") | Q(contacto_principal_correo__isnull=True)
    ).filter(
        Q(contacto_alternativo_correo="") | Q(contacto_alternativo_correo__isnull=True)
    ).order_by("razon_social")
    situaciones = Empresa.objects.values("situacion_empresa").annotate(
        total=Count("id")
    ).order_by("situacion_empresa")
    situation_labels = dict(SituacionEmpresa.choices)
    situaciones = [
        {"label": situation_labels.get(item["situacion_empresa"], "Situación sin clasificar"), "total": item["total"]}
        for item in situaciones
    ]
    context = {
        "empresa_count": total,
        "gestionadas_count": Actividad.objects.values("empresa_id").distinct().count(),
        "asistencia_count": Actividad.objects.filter(categoria__nombre="Asesoría").values("empresa_id").distinct().count(),
        "contactadas_porcentaje": contacted.count() * 100 / total if total else 0,
        "reporte": report,
        "periodo": period,
        "reporte_chart": {"labels": [item["label"] for item in report], "values": [item["total"] for item in report]},
        "actividades_por_medio": Actividad.objects.values("medio__nombre").annotate(total=Count("id")).order_by("-total"),
        "con_contacto_count": Empresa.objects.exclude(
            contacto_principal_correo="", contacto_principal_telefono="",
            contacto_alternativo_correo="", contacto_alternativo_telefono="",
        ).count(),
        "con_correo_count": Empresa.objects.exclude(contacto_principal_correo="", contacto_alternativo_correo="").count(),
        "con_telefono_count": Empresa.objects.exclude(contacto_principal_telefono="", contacto_alternativo_telefono="").count(),
        "con_nombre_count": Empresa.objects.exclude(contacto_principal_nombre="", contacto_alternativo_nombre="").count(),
        "codigo_cero_count": Empresa.objects.filter(datos_carga__columnas__W="0").count(),
        "empresas_sin_correo_count": empresas_sin_correo.count(),
        "empresas_sin_correo": empresas_sin_correo,
        "contactadas_count": contacted.count(),
        "encuestas_finalizadas_count": Empresa.objects.filter(
            estado_encuesta="finalizada"
        ).count(),
        "criticas_abiertas_count": Critica.objects.exclude(estado_revision="validado").count(),
        "actividad_count": Actividad.objects.count(),
        "situaciones": situaciones,
        "situaciones_chart": {
            "labels": [item["label"] for item in situaciones],
            "values": [item["total"] for item in situaciones],
        },
        "ultimas_actividades": Actividad.objects.select_related(
            "empresa", "medio", "categoria"
        )[:8],
        "ultimas_criticas": Critica.objects.select_related("empresa")[:6],
    }
    return render(request, "bitacora/dashboard.html", context)


def directorio(request):
    empresas = Empresa.objects.all()
    query = request.GET.get("q", "").strip()
    situacion = request.GET.get("situacion", "")
    estado_contacto = request.GET.get("estado_contacto", "")

    if query:
        empresas = empresas.filter(
            Q(ruc__icontains=query)
            | Q(razon_social__icontains=query)
            | Q(contacto_principal_nombre__icontains=query)
        )
    if situacion:
        empresas = empresas.filter(situacion_empresa=situacion)
    if estado_contacto:
        empresas = empresas.filter(contacto_principal_estado=estado_contacto)

    context = {
            "empresas": empresas,
            "query": query,
            "situacion_seleccionada": situacion,
            "estado_contacto_seleccionado": estado_contacto,
            "situaciones": SituacionEmpresa.choices,
            "estados_contacto": EstadoContacto.choices,
        }
    export = tabular_export(
        request,
        "directorio-edo",
        ["RUC", "Razón social", "Contacto", "Cargo", "Teléfono", "WhatsApp", "Correo", "Situación", "Actualizada", "Estado contacto", "Correo confirmado", "Estado encuesta", "Estado crítica"],
        [
            [
                company.ruc, company.razon_social, company.contacto_principal_nombre,
                company.contacto_principal_cargo, company.contacto_principal_telefono,
                company.whatsapp_url, company.contacto_principal_correo,
                company.get_situacion_empresa_display(), company.situacion_actualizada_en,
                company.get_contacto_principal_estado_display(),
                "Sí" if company.contacto_principal_correo_confirmado else "No",
                company.get_estado_encuesta_display(), company.get_estado_critica_display(),
            ]
            for company in empresas
        ],
    )
    if export:
        return export
    context["resultados_exportados"] = empresas.count()
    empresas = empresas[:200]
    context["empresas"] = empresas
    template = "bitacora/partials/directorio_resultados.html" if getattr(request, "htmx", False) else "bitacora/directorio.html"
    return render(request, template, context)


def empresa_nueva(request):
    return _empresa_form(request)


def empresa_editar(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    return _empresa_form(request, empresa)


def _empresa_form(request, empresa=None):
    form = EmpresaForm(request.POST or None, instance=empresa)
    if request.method == "POST" and form.is_valid():
        saved = form.save()
        messages.success(request, "Empresa guardada.")
        return redirect("bitacora:empresa_detalle", pk=saved.pk)
    return render(
        request,
        "bitacora/empresa_form.html",
        {"form": form, "empresa": empresa, "page_title": "Editar empresa" if empresa else "Nueva empresa"},
    )


def empresa_detalle(request, pk):
    empresa = get_object_or_404(Empresa, pk=pk)
    source = empresa.datos_carga
    channels = {}
    for key in ["correos", "telefonos"]:
        by_value = {}
        for item in source.get(key, []):
            entry = by_value.setdefault(item["valor"], {"valor": item["valor"], "fuentes": []})
            label = f"{item['fuente']} · {item['columna']}"
            if label not in entry["fuentes"]:
                entry["fuentes"].append(label)
        channels[key] = list(by_value.values())
    originals = [
        {"columna": column, "titulo": source.get("encabezados", {}).get(column, column), "valor": value}
        for column, value in source.get("columnas", {}).items()
    ]
    return render(
        request,
        "bitacora/empresa_detalle.html",
        {
            "empresa": empresa,
            "origenes": source.get("origenes", {}),
            "contactos_origen": source.get("contactos", []),
            "canales_origen": channels,
            "valores_origen": originals,
            "actividades": empresa.actividades.select_related("medio", "categoria")[:10],
            "criticas": empresa.criticas.all()[:10],
        },
    )


def actividades(request):
    queryset = Actividad.objects.select_related("empresa", "medio", "categoria")
    query = request.GET.get("q", "").strip()
    categoria = request.GET.get("categoria", "")
    medio = request.GET.get("medio", "")
    if query:
        queryset = queryset.filter(
            Q(empresa__ruc__icontains=query)
            | Q(empresa__razon_social__icontains=query)
            | Q(descripcion__icontains=query)
        )
    if categoria:
        queryset = queryset.filter(categoria_id=categoria)
    if medio:
        queryset = queryset.filter(medio_id=medio)
    export = tabular_export(
        request,
        "actividades-edo",
        ["Fecha", "Hora", "RUC", "Empresa", "Medio", "Categoría", "Descripción"],
        [
            [item.fecha, item.hora, item.empresa.ruc, item.empresa.razon_social, item.medio.nombre, item.categoria.nombre, item.descripcion]
            for item in queryset
        ],
    )
    if export:
        return export
    return render(
        request,
        "bitacora/actividades.html",
        {
            "actividades": queryset[:100],
            "query": query,
            "categoria_seleccionada": categoria,
            "medio_seleccionado": medio,
            "categorias": CategoriaActividad.objects.filter(activo=True),
            "medios": Medio.objects.filter(activo=True),
        },
    )


def actividad_nueva(request):
    initial = {"empresa": request.GET.get("empresa")} if request.GET.get("empresa") else None
    form = ActividadForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Actividad registrada.")
        return redirect("bitacora:actividades")
    return render(request, "bitacora/actividad_form.html", {"form": form})


def criticas(request):
    queryset = Critica.objects.select_related("empresa")
    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(
            Q(empresa__ruc__icontains=query)
            | Q(empresa__razon_social__icontains=query)
            | Q(variable_analizada__icontains=query)
        )
    export = tabular_export(
        request,
        "sustento-critica-edo",
        ["RUC", "Empresa", "Variable", "Registro", "Tareas", "Nivel educativo", "CIIU", "Remuneración", "Valor original", "Valor resultante", "Resultado", "Evidencia", "Método", "Justificación", "Confianza", "Estado revisión", "Creado"],
        [
            [
                item.empresa.ruc, item.empresa.razon_social, item.variable_analizada,
                item.registro_referencia, item.contexto_tareas, item.contexto_nivel_educativo,
                item.contexto_ciiu, item.contexto_remuneracion, item.valor_original,
                item.valor_resultante, item.get_tipo_resultado_display(), item.evidencia,
                item.metodo_analisis, item.justificacion, item.get_nivel_confianza_display(),
                item.get_estado_revision_display(), item.creado_en,
            ]
            for item in queryset
        ],
    )
    if export:
        return export
    return render(
        request,
        "bitacora/criticas.html",
        {"criticas": queryset[:100], "query": query},
    )


def critica_nueva(request):
    initial = {"empresa": request.GET.get("empresa")} if request.GET.get("empresa") else None
    form = CriticaForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Caso de crítica guardado.")
        return redirect("bitacora:criticas")
    return render(request, "bitacora/critica_form.html", {"form": form})
