from django.core.management.base import BaseCommand

from kureta.utils import (
    Database,
    Static
)


class Command(BaseCommand):
    help = 'Initialize the project'

    def add_arguments(self, parser):
        parser.add_argument(
            '-i', '--install',
            action='store_true',
            help='Initialize the project'
        )

    def handle(self, *args, **options):
        if options.get('install'):
            Command.install()

    @staticmethod
    def install():
        _database = Database()
        _database.initialize()

        _static = Static()
        _static.initialize()
