from .models import *


def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "PH":
            Physician.objects.create(account=instance)
        elif instance.role == "PA":
            Patient.objects.create(account=instance)
        else:
            pass
