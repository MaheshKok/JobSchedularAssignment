# jobs/scheduler.py
import logging
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from django.utils import timezone
from django.db import transaction
from .models import Job, JobExecution

logger = logging.getLogger(__name__)

# Maximum number of concurrent jobs
MAX_CONCURRENT_JOBS = 3


class JobScheduler:
    """
    Job scheduler that implements priority-based scheduling with deadline awareness.
    Uses a combination of:
    1. Priority Queue - prioritizes high priority jobs
    2. Earliest Deadline First (EDF) - prioritizes jobs with closer deadlines
    """

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS)
        self._running = False
        self._lock = threading.Lock()
        self._current_jobs = set()

    def start(self):
        """Start the scheduler in a background thread"""
        if self._running:
            return

        self._running = True
        thread = threading.Thread(target=self._run_scheduler, daemon=True)
        thread.start()
        logger.info("Job scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self._running = False
        self.executor.shutdown(wait=False)
        logger.info("Job scheduler stopped")

    def _run_scheduler(self):
        """Main scheduler loop that continuously checks for jobs to run"""
        while self._running:
            try:
                # Process jobs if we have capacity
                with self._lock:
                    if len(self._current_jobs) < MAX_CONCURRENT_JOBS:
                        available_slots = MAX_CONCURRENT_JOBS - len(self._current_jobs)
                        jobs_to_run = self._get_next_jobs(limit=available_slots)

                        for job in jobs_to_run:
                            self._current_jobs.add(job.id)
                            self.executor.submit(self._execute_job, job)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")

            # Sleep for a bit to avoid high CPU usage
            time.sleep(1)

    def _get_next_jobs(self, limit=1):
        """Get the next jobs to run based on priority and deadline"""
        with transaction.atomic():
            # Get pending jobs
            pending_jobs = Job.objects.filter(status="pending").select_for_update(
                skip_locked=True
            )

            # No jobs to run
            if not pending_jobs.exists():
                return []

            # Implement our prioritization algorithm
            # First prioritize by priority level
            high_priority = pending_jobs.filter(priority="high")
            medium_priority = pending_jobs.filter(priority="medium")
            low_priority = pending_jobs.filter(priority="low")

            result = []

            # For each priority level, sort by deadline (earliest first)
            for priority_group in [high_priority, medium_priority, low_priority]:
                if not priority_group.exists():
                    continue

                # Get jobs sorted by deadline
                deadline_sorted = priority_group.order_by("deadline")

                # Take up to our remaining limit
                remaining = limit - len(result)
                if remaining <= 0:
                    break

                batch = list(deadline_sorted[:remaining])
                result.extend(batch)

                # If we've reached our limit, stop
                if len(result) >= limit:
                    break

            # Mark selected jobs as running
            for job in result:
                job.status = "running"
                job.started_at = timezone.now()
                job.save(update_fields=["status", "started_at"])

            return result

    def _execute_job(self, job):
        """Execute a single job"""
        try:
            # Create execution record
            execution = JobExecution.objects.create(job=job)

            # Log start
            logger.info(f"Starting job {job.name} ({job.id})")

            # Simulate work
            time.sleep(job.estimated_duration)

            # Mark job as completed
            with transaction.atomic():
                # Re-fetch the job to ensure we have the latest state
                job = Job.objects.get(id=job.id)

                # Only update if the job is still running
                if job.status == "running":
                    job.status = "completed"
                    job.completed_at = timezone.now()
                    job.save(update_fields=["status", "completed_at"])

                    # Update execution record
                    execution.completed_at = job.completed_at
                    execution.success = True
                    execution.save(update_fields=["completed_at", "success"])

                    logger.info(f"Completed job {job.name} ({job.id})")

        except Exception as e:
            # Mark job as failed
            try:
                # Re-fetch the job
                job = Job.objects.get(id=job.id)
                job.status = "failed"
                job.completed_at = timezone.now()
                job.save(update_fields=["status", "completed_at"])

                # Update execution record
                execution.completed_at = timezone.now()
                execution.success = False
                execution.error_message = str(e)
                execution.save(
                    update_fields=["completed_at", "success", "error_message"]
                )

                logger.error(f"Job {job.name} ({job.id}) failed: {e}")
            except Exception as inner_e:
                logger.error(f"Error handling job failure: {inner_e}")

        finally:
            # Remove job from the current jobs set
            with self._lock:
                self._current_jobs.discard(job.id)


# Create a singleton instance
scheduler = JobScheduler()


def get_scheduler():
    """Get the scheduler instance"""
    return scheduler
