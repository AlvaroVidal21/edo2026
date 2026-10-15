from django.conf import settings


def environment(request):
    return {"demo_mode": settings.DEMO_MODE, "real_app_url": settings.REAL_APP_URL}
