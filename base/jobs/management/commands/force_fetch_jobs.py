from django.core.management.base import BaseCommand
from jobs.tasks import fetch_and_save_jobs

class Command(BaseCommand):
    help = 'Force fetch jobs from the XML feed immediately'

    def handle(self, *args, **options):
        self.stdout.write('Starting immediate job fetch...')
        try:
            result = fetch_and_save_jobs()  # Note: not using .delay() to run synchronously
            self.stdout.write(self.style.SUCCESS(f'Job fetch completed: {result}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching jobs: {str(e)}')) 