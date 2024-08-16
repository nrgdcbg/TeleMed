from django.apps import AppConfig
from django.db.models.signals import post_save


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        from . import signals
        from .models import Account

        post_save.connect(signals.create_profile, sender=Account)
