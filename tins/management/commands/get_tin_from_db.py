import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

from tins.models import Source

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--tin", type=str, required=True, help="TIN/NIP to find the information."
        )

    def handle(self, *args, **options):
        tin: str = options["tin"]
        if Source.objects.filter(tin=tin).exists():
            source = Source.objects.filter(tin=tin).values().first()
            for key, value in source.items():
                logger.info(f"{key} : {value}")
        else:
            logger.info(f"TIN: {tin} Not Found")
