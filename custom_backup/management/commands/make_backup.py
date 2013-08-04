from custom_backup.utils import perform_backup
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    args = ''
    help = 'Performs backup of project'

    def handle(self, *args, **options):
        perform_backup()
