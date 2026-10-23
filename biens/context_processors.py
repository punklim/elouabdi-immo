from django.conf import settings


def agence(request):
    return {"AGENCE": settings.AGENCE}
