import logging
import threading

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from .models import Bien, Demande

logger = logging.getLogger(__name__)


def _en_ligne(bien):
    return bien.publie and bien.statut == Bien.Statut.DISPONIBLE


@receiver(pre_save, sender=Bien)
def memoriser_etat(sender, instance, **kwargs):
    ancien = Bien.objects.filter(pk=instance.pk).first() if instance.pk else None
    instance._etait_en_ligne = bool(ancien and _en_ligne(ancien))


@receiver(post_save, sender=Bien)
def alerter(sender, instance, raw=False, **kwargs):
    """Quand un bien passe en ligne (création ou publication), prévient les alertes correspondantes."""
    if raw or not _en_ligne(instance) or getattr(instance, "_etait_en_ligne", False):
        return
    pk = instance.pk

    def envoyer():
        from .alertes import notifier_nouveau_bien
        notifier_nouveau_bien(Bien.objects.select_related("ville").get(pk=pk))

    transaction.on_commit(envoyer)  # après l'enregistrement des photos et équipements


@receiver(post_save, sender=Demande)
def prevenir_agence(sender, instance, created=False, raw=False, **kwargs):
    """Envoie un e-mail à l'agence à chaque nouvelle demande (contact, visite, estimation)."""
    if raw or not created:
        return
    pk = instance.pk

    def envoyer():
        try:
            d = Demande.objects.select_related("bien").get(pk=pk)
            destinataire = settings.AGENCE["email"]
            lien = settings.SITE_URL + reverse("admin:biens_demande_change", args=[d.pk])
            bien = f"{d.bien.reference} – {d.bien.titre}" if d.bien_id else "—"
            corps = (
                f"Nouvelle demande reçue sur le site.\n\n"
                f"Type : {d.get_origine_display()}\n"
                f"Nom : {d.nom}\n"
                f"Téléphone : {d.telephone}\n"
                f"E-mail : {d.email or '—'}\n"
                f"Bien : {bien}\n\n"
                f"Message :\n{d.message or '—'}\n\n"
                f"Ouvrir dans l'administration : {lien}\n"
            )
            send_mail(
                subject=f"Nouvelle demande : {d.nom} ({d.get_origine_display()})",
                message=corps,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[destinataire],
                fail_silently=False,
            )
        except Exception:
            # Un problème d'e-mail ne doit jamais empêcher le visiteur d'envoyer sa demande.
            logger.exception("Envoi de l'e-mail de nouvelle demande impossible (demande n°%s)", pk)

    # L'envoi se fait en arrière-plan : le visiteur n'attend jamais le serveur d'e-mail.
    transaction.on_commit(lambda: threading.Thread(target=envoyer, daemon=True).start())