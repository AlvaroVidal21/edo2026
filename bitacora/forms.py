from django import forms
from django.core.exceptions import ValidationError

from .models import Actividad, CategoriaActividad, Critica, Empresa, Medio


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
            field.widget.attrs["class"] = f"{field.widget.attrs.get('class', '')} {css_class}".strip()


class EmpresaForm(BootstrapModelForm):
    class Meta:
        model = Empresa
        fields = [
            "ruc", "razon_social", "region", "ciiu",
            "contacto_principal_nombre", "contacto_principal_cargo",
            "contacto_principal_telefono", "contacto_principal_correo",
            "contacto_principal_estado", "contacto_principal_correo_confirmado",
            "contacto_alternativo_nombre", "contacto_alternativo_cargo",
            "contacto_alternativo_telefono", "contacto_alternativo_correo",
            "contacto_alternativo_estado", "contacto_alternativo_correo_confirmado",
            "estado_encuesta", "estado_critica",
        ]
        labels = {
            "ruc": "RUC",
            "razon_social": "Razón social",
            "region": "Región",
            "ciiu": "CIIU",
            "contacto_principal_nombre": "Nombre del contacto",
            "contacto_principal_cargo": "Cargo del contacto",
            "contacto_principal_telefono": "Teléfono",
            "contacto_principal_correo": "Correo electrónico",
            "contacto_principal_estado": "Estado de contacto",
            "contacto_principal_correo_confirmado": "Correo confirmado",
            "contacto_alternativo_nombre": "Nombre del contacto alternativo",
            "contacto_alternativo_cargo": "Cargo del contacto alternativo",
            "contacto_alternativo_telefono": "Teléfono alternativo",
            "contacto_alternativo_correo": "Correo alternativo",
            "contacto_alternativo_estado": "Estado de contacto alternativo",
            "contacto_alternativo_correo_confirmado": "Correo alternativo confirmado",
            "estado_encuesta": "Estado de Encuesta",
            "estado_critica": "Estado de Crítica",
        }
        widgets = {
            "contacto_principal_correo_confirmado": forms.CheckboxInput(),
            "contacto_alternativo_correo_confirmado": forms.CheckboxInput(),
        }


class ActividadForm(BootstrapModelForm):
    class Meta:
        model = Actividad
        fields = ["empresa", "medio", "categoria", "fecha", "hora", "descripcion"]
        labels = {
            "empresa": "Empresa",
            "medio": "Medio",
            "categoria": "Categoría de actividad",
            "fecha": "Fecha de la gestión",
            "hora": "Hora (opcional)",
            "descripcion": "Descripción de lo realizado",
        }
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora": forms.TimeInput(attrs={"type": "time"}),
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["medio"].queryset = Medio.objects.filter(activo=True)
        self.fields["categoria"].queryset = CategoriaActividad.objects.filter(activo=True)


class CriticaForm(BootstrapModelForm):
    class Meta:
        model = Critica
        fields = [
            "empresa", "variable_analizada", "registro_referencia",
            "contexto_tareas", "contexto_nivel_educativo", "contexto_ciiu",
            "contexto_remuneracion",
            "valor_original", "valor_resultante", "tipo_resultado",
            "evidencia", "metodo_analisis", "justificacion",
            "nivel_confianza", "estado_revision",
        ]
        labels = {
            "empresa": "Empresa",
            "variable_analizada": "Variable analizada",
            "registro_referencia": "Registro concreto de la encuesta",
            "contexto_tareas": "Tareas revisadas",
            "contexto_nivel_educativo": "Nivel educativo relacionado",
            "contexto_ciiu": "CIIU usado en el análisis",
            "contexto_remuneracion": "Remuneración relacionada",
            "valor_original": "Valor original",
            "valor_resultante": "Valor validado o asignado",
            "tipo_resultado": "Decisión",
            "evidencia": "Evidencia consultada",
            "metodo_analisis": "Método de análisis",
            "justificacion": "Justificación",
            "nivel_confianza": "Nivel de confianza",
            "estado_revision": "Estado de revisión",
        }
        help_texts = {
            "registro_referencia": "Ejemplo: ocupación 2 del formulario 3.2. Si no hay ID, escribe una referencia que distinga este registro de los demás.",
            "justificacion": "Obligatoria para validaciones y recodificaciones. Explica brevemente el criterio aplicado.",
        }
        widgets = {
            "contexto_tareas": forms.Textarea(attrs={"rows": 3}),
            "evidencia": forms.Textarea(attrs={"rows": 3}),
            "justificacion": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        result_type = cleaned_data.get("tipo_resultado")
        original = cleaned_data.get("valor_original")
        result = cleaned_data.get("valor_resultante")
        if result_type == Critica.TipoResultado.VALIDACION and original and not result:
            cleaned_data["valor_resultante"] = original
        if result_type == Critica.TipoResultado.RECODIFICACION and not result:
            self.add_error("valor_resultante", ValidationError("Indica el valor o código asignado."))
        return cleaned_data
