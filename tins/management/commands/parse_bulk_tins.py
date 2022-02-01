import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

from tins.Kaczmarski import Kaczmarski
from tins.models import Tin

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--num_of_records",
            default=2,
            type=str,
            required=False,
            help="Not Required, Default is 5, Number of records parsed from Tin to parse in bulk.",  # noqa
        )

    def handle(self, *args, **options):
        num_of_records = int(options["num_of_records"])
        for tin in Tin.objects.all().order_by("updated")[:num_of_records]:
            data = Kaczmarski(tin).parse_tin()
            for key, value in data.items():
                logger.info(f"{key} : {value}")
            logger.info("-" * 100)
