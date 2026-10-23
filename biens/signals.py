from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Bien


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
