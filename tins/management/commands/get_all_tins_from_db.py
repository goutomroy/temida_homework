import logging

from django.core.management import BaseCommand

from tins.models import Source

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        for source in Source.objects.filter().order_by("-updated").values():
            for key, value in source.items():
                logger.info(f"{key} : {value}")
            logger.info("-" * 89)
