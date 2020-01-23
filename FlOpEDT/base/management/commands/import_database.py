from django.core.management.base import BaseCommand, CommandError
from misc.deploy_database.deploy_database import extract_database_file

class Command(BaseCommand):
    help = 'Import data'

    def add_arguments(self, parser):
        parser.add_argument('bookname', type=str)
        parser.add_argument('department_name', type=str)
        parser.add_argument('department_abbrev', type=str)

    def handle(self, *args, **options):
        kwargs = {
            'bookname': options['bookname'],
            'department_name': options['department_name'],
            'department_abbrev': options['department_abbrev'],
        }

        extract_database_file(**kwargs)        
        self.stdout.write(self.style.SUCCESS('Successfully imported data'))