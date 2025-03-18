import time
import logging
from django.core.management.base import BaseCommand
from jobs.scheduler import get_scheduler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Starts the job scheduler to process jobs in the background"

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS("Starting job scheduler..."))

            # Get scheduler instance
            scheduler = get_scheduler()

            # Start the scheduler
            scheduler.start()

            self.stdout.write(self.style.SUCCESS("Job scheduler started"))

            # Keep the command running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Stopping job scheduler..."))
            scheduler.stop()
            self.stdout.write(self.style.SUCCESS("Job scheduler stopped"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            logger.exception("Error in job scheduler command")
