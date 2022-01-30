import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

from workers.tasks import scrape_tin

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--tin", type=str, required=True, help="TIN/NIP to find the information."
        )

    def handle(self, *args, **options):
        scrape_tin.apply_async((options["tin"], False))
        logger.info(
            "Task has been started. Check http://127.0.0.1:8000/admin/django_celery_results/taskresult/ for results."  # noqa
        )
