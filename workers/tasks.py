from celery import shared_task
from django.utils import timezone

from tins.Kaczmarski import Kaczmarski
from tins.models import Tin


@shared_task
def scrape_tin(tin, save_updated_in_tin: bool):
    raw_parsed_data = Kaczmarski(tin).parse_tin()
    if save_updated_in_tin:
        Tin.objects.filter(tin=tin).update(updated=timezone.now())

    return raw_parsed_data
