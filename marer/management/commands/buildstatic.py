import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand

logger = logging.getLogger('django')


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('Calling bower install')
        call_command('bower_install', **dict(force=True))
        logger.info('Calling collect static files')
        call_command('collectstatic', **dict(clear=True, interactive=False))
