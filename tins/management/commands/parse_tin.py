import logging
from argparse import ArgumentParser

from django.core.management import BaseCommand

from tins.Kaczmarski import Kaczmarski

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument(
            "--tin", type=str, required=True, help="TIN/NIP to find the information."
        )

    def handle(self, *args, **options):
        tin: str = options["tin"]
        kaczmarski = Kaczmarski()
        kaczmarski.parse_tin(tin)
