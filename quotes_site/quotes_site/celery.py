import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quotes_site.settings")

app = Celery("quotes_site")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

from services import scraper
