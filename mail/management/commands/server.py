from django.core.management.base import BaseCommand

from kureta.utils import Database


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
        database = Database()
        database.initialize()
