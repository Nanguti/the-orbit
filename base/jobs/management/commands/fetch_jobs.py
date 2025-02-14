from django.core.management.base import BaseCommand
from jobs.tasks import fetch_and_save_jobs

class Command(BaseCommand):
    help = 'Fetch jobs from the XML feed'

    def handle(self, *args, **options):
        self.stdout.write('Fetching jobs...')
        result = fetch_and_save_jobs.delay()
        self.stdout.write(self.style.SUCCESS('Jobs fetch task initiated')) 