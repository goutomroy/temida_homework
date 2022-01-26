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
        parser.add_argument(
            "--sell_for",
            type=str,
            required=False,
            help="Sell information you want to update",
        )
        parser.add_argument(
            "--document_type",
            type=str,
            required=False,
            help="Document type you want to update",
        )

    def handle(self, *args, **options):

        tin: str = options["tin"]
        data_to_update = {
            key: value
            for key, value in options.items()
            if key in ["sell_for", "document_type"] and options[key] is not None
        }

        if len(data_to_update) < 1:
            logger.info(
                "You need to specify at least one of 'sell_for', 'document_info'."
            )
            return

        if Source.objects.filter(tin=tin).exists():
            Source.objects.filter(tin=tin).update(**data_to_update)
            for key, value in Source.objects.filter(tin=tin).values().first().items():
                logger.info(f"{key} : {value}")
        else:
            logger.info(f"TIN: {tin} Not Found")
