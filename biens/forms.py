from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Alerte, Demande


class _AntiSpam(forms.Form):
    # Champ piège : invisible pour les humains, rempli par les robots
    site_web = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    def clean_site_web(self):
        if self.cleaned_data.get("site_web"):
            raise forms.ValidationError("Spam détecté.")
        return ""


class DemandeForm(_AntiSpam, forms.ModelForm):
    class Meta:
        model = Demande
        fields = ["nom", "telephone", "email", "message"]
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}
        labels = {
            "nom": _("Nom complet"),
            "telephone": _("Téléphone"),
            "email": _("E-mail (facultatif)"),
            "message": _("Message"),
        }


class AlerteForm(_AntiSpam, forms.ModelForm):
    class Meta:
        model = Alerte
        fields = ["email", "transaction", "ville", "type_bien", "budget_max"]
