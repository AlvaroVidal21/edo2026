from typing import ClassVar

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from .carga import whatsapp_url


class SituacionEmpresa(models.TextChoices):
    COMPLETADO = "1", "Completado"
    FUSIONADA = "2", "Fusionada/Absorbida"
    PARALIZADA = "3", "Paralizada"
    LIQUIDADA = "4", "Liquidada"
    DE_BAJA = "5", "De baja"
    SUSPENSION_TEMPORAL = "6", "Suspensión temporal"
    EMPRESA_ESTADO = "7", "Empresa del Estado"
    NO_INGRESO = "8", "No ingresó al aplicativo a gestionar la encuesta"
    RECHAZO = "9", "Se negó a dar información (rechazo)"
    NO_UBICADA = "10", "No ubicada"
    EN_PROCESO = "11", "En proceso: quedó pendiente de terminar; pese a la insistencia, nunca terminó"


class EstadoEncuesta(models.TextChoices):
    BUSQUEDA = "busqueda", "Sin datos / En búsqueda"
    POR_CONTACTAR = "por_contactar", "Por contactar"
    EN_SEGUIMIENTO = "en_seguimiento", "En seguimiento / Llenando"
    FINALIZADA = "finalizada", "Encuesta finalizada"


class EstadoCritica(models.TextChoices):
    SIN_INICIAR = "sin_iniciar", "Sin iniciar"
    EN_ANALISIS = "en_analisis", "En análisis"
    VALIDADA_CERRADA = "validada_cerrada", "Validada / Cerrada"


class EstadoContacto(models.TextChoices):
    PENDIENTE = "pendiente", "Pendiente"
    CONTACTADO = "contactado", "Contactado"
    NO_CONTESTA = "no_contesta", "No contesta"
    NUMERO_INCORRECTO = "numero_incorrecto", "Número incorrecto"


class Medio(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["nombre"]
        verbose_name = "medio"
        verbose_name_plural = "medios"

    def __str__(self):
        return self.nombre


class CategoriaActividad(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.CharField(max_length=240, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["nombre"]
        verbose_name = "categoría de actividad"
        verbose_name_plural = "categorías de actividad"

    def __str__(self):
        return self.nombre


class Empresa(models.Model):
    ruc = models.CharField(
        max_length=11,
        unique=True,
        validators=[RegexValidator(r"^\d{11}$", "El RUC debe contener 11 dígitos.")],
    )
    razon_social = models.CharField(max_length=240)
    region = models.CharField(max_length=100)
    ciiu = models.CharField(max_length=20)

    contacto_principal_nombre = models.CharField(max_length=180, blank=True)
    contacto_principal_cargo = models.CharField(max_length=160, blank=True)
    contacto_principal_telefono = models.CharField(max_length=40, blank=True)
    contacto_principal_correo = models.EmailField(blank=True)
    contacto_principal_estado = models.CharField(
        max_length=24, choices=EstadoContacto.choices, default=EstadoContacto.PENDIENTE
    )
    contacto_principal_correo_confirmado = models.BooleanField(default=False)

    contacto_alternativo_nombre = models.CharField(max_length=180, blank=True)
    contacto_alternativo_cargo = models.CharField(max_length=160, blank=True)
    contacto_alternativo_telefono = models.CharField(max_length=40, blank=True)
    contacto_alternativo_correo = models.EmailField(blank=True)
    contacto_alternativo_estado = models.CharField(
        max_length=24, choices=EstadoContacto.choices, blank=True
    )
    contacto_alternativo_correo_confirmado = models.BooleanField(null=True, blank=True)

    situacion_empresa = models.CharField(max_length=2, choices=SituacionEmpresa.choices, blank=True)
    situacion_actualizada_en = models.DateField(null=True, blank=True)
    estado_encuesta = models.CharField(
        max_length=24, choices=EstadoEncuesta.choices, default=EstadoEncuesta.BUSQUEDA
    )
    estado_critica = models.CharField(
        max_length=24, choices=EstadoCritica.choices, default=EstadoCritica.SIN_INICIAR
    )
    datos_carga = models.JSONField(default=dict, blank=True)

    history = HistoricalRecords()

    class Meta:
        ordering: ClassVar[list[str]] = ["razon_social"]
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        constraints: ClassVar[list[models.CheckConstraint]] = [
            models.CheckConstraint(
                condition=models.Q(ruc__regex=r"^\d{11}$"),
                name="empresa_ruc_11_digitos",
            )
        ]

    def __str__(self):
        return f"{self.razon_social} ({self.ruc})"

    @property
    def whatsapp_url(self):
        return whatsapp_url(self.contacto_principal_telefono)


class Actividad(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="actividades")
    medio = models.ForeignKey(Medio, on_delete=models.PROTECT, related_name="actividades")
    categoria = models.ForeignKey(
        CategoriaActividad, on_delete=models.PROTECT, related_name="actividades"
    )
    fecha = models.DateField(default=timezone.localdate)
    hora = models.TimeField(null=True, blank=True)
    descripcion = models.TextField()

    class Meta:
        ordering: ClassVar[list[str]] = ["-fecha", "-hora", "-id"]
        verbose_name = "actividad"
        verbose_name_plural = "actividades"

    def __str__(self):
        return f"{self.categoria} · {self.empresa} · {self.fecha}"


class Critica(models.Model):
    class TipoResultado(models.TextChoices):
        VALIDACION = "validacion", "Validación"
        RECODIFICACION = "recodificacion", "Recodificación"

    class NivelConfianza(models.TextChoices):
        ALTA = "alta", "Alta"
        MEDIA = "media", "Media"
        BAJA = "baja", "Baja"

    class EstadoRevision(models.TextChoices):
        REQUERIDA = "revision_requerida", "Revisión requerida"
        REVISADA = "revisado", "Revisado"
        VALIDADA = "validado", "Validado"

    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="criticas")
    variable_analizada = models.CharField(max_length=120)
    registro_referencia = models.CharField(max_length=160)
    contexto_tareas = models.TextField(blank=True)
    contexto_nivel_educativo = models.CharField(max_length=180, blank=True)
    contexto_ciiu = models.CharField(max_length=30, blank=True)
    contexto_remuneracion = models.CharField(max_length=120, blank=True)
    valor_original = models.TextField()
    valor_resultante = models.TextField(blank=True)
    tipo_resultado = models.CharField(max_length=20, choices=TipoResultado.choices, blank=True)
    evidencia = models.TextField(blank=True)
    metodo_analisis = models.CharField(max_length=160, blank=True)
    justificacion = models.TextField()
    nivel_confianza = models.CharField(
        max_length=10, choices=NivelConfianza.choices, blank=True
    )
    estado_revision = models.CharField(
        max_length=24, choices=EstadoRevision.choices, default=EstadoRevision.REQUERIDA
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        ordering: ClassVar[list[str]] = ["-creado_en", "-id"]
        verbose_name = "caso de crítica"
        verbose_name_plural = "casos de crítica"
        constraints: ClassVar[list[models.CheckConstraint]] = [
            models.CheckConstraint(
                condition=~models.Q(justificacion=""),
                name="critica_requiere_justificacion",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(tipo_resultado="recodificacion")
                    | ~models.Q(valor_resultante="")
                ),
                name="recodificacion_requiere_resultado",
            ),
        ]

    def __str__(self):
        return f"{self.variable_analizada} · {self.empresa}"
