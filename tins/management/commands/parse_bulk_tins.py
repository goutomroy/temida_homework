import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

from tins.models import Tin
from workers.tasks import scrape_tin

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--num_of_records",
            default=5,
            type=str,
            required=False,
            help="Not Required, Default is 5, Number of records parsed from Tin to parse in bulk.",  # noqa
        )

    def handle(self, *args, **options):
        num_of_records = int(options["num_of_records"])
        for tin in Tin.objects.all().order_by("updated")[:num_of_records]:
            scrape_tin.apply_async((tin.tin, True))
        logger.info(
            "Task has been started. Check http://127.0.0.1:8000/admin/django_celery_results/taskresult/ for results."  # noqa
        )
