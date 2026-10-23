from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext as _

from .models import Alerte


def _lien_desinscription(alerte):
    return settings.SITE_URL + reverse("alerte_supprimer", args=[alerte.token])


def envoyer_confirmation(alerte):
    with translation.override(alerte.langue):
        send_mail(
            _("Votre alerte immobilière est activée"),
            _("Bonjour,\n\nVotre alerte est bien enregistrée : vous recevrez un e-mail à chaque nouveau bien correspondant à votre recherche.\n\nPour vous désinscrire : %(lien)s")
            % {"lien": _lien_desinscription(alerte)},
            None, [alerte.email], fail_silently=True,
        )


def notifier_nouveau_bien(bien):
    prix = f"{int(bien.prix):,}".replace(",", " ")
    for alerte in Alerte.objects.filter(actif=True):
        if not alerte.correspond(bien):
            continue
        with translation.override(alerte.langue):
            send_mail(
                _("Nouveau bien : %(titre)s") % {"titre": bien.titre_affiche},
                _("Un nouveau bien correspond à votre alerte :\n\n%(titre)s\n%(ville)s · %(prix)s MAD\n\n%(lien)s\n\nSe désinscrire : %(stop)s")
                % {
                    "titre": bien.titre_affiche,
                    "ville": bien.ville.nom_affiche,
                    "prix": prix,
                    "lien": settings.SITE_URL + bien.get_absolute_url(),
                    "stop": _lien_desinscription(alerte),
                },
                None, [alerte.email], fail_silently=True,
            )
