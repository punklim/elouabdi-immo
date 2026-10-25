from django.apps import AppConfig


class BiensConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'biens'

    def ready(self):
        # Branche les signaux : alertes e-mail sur les nouveaux biens, e-mail de l'agence pour chaque demande.
        from . import signals  # noqa: F401