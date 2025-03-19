import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Job(models.Model):
    PRIORITY_CHOICES = (
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    )

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs")
    name = models.CharField(max_length=255)
    estimated_duration = models.PositiveIntegerField(help_text="Duration in seconds")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def duration(self):
        """Calculate actual duration if job has completed"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    @property
    def wait_time(self):
        """Calculate wait time before job started"""
        if self.started_at:
            return (self.started_at - self.created_at).total_seconds()
        return (timezone.now() - self.created_at).total_seconds()

    @property
    def is_overdue(self):
        """Check if job has missed its deadline"""
        return timezone.now() > self.deadline

    @property
    def status_color(self):
        """Return Bootstrap color class based on status"""
        colors = {
            "pending": "secondary",
            "running": "primary",
            "completed": "success",
            "failed": "danger",
        }
        return colors.get(self.status, "secondary")

    @property
    def priority_value(self):
        """Return numeric value for priority for sorting"""
        values = {
            "high": 3,
            "medium": 2,
            "low": 1,
        }
        return values.get(self.priority, 0)

    def start(self):
        """Mark job as running"""
        self.status = "running"
        self.started_at = timezone.now()
        self.save()

    def complete(self):
        """Mark job as completed"""
        self.status = "completed"
        self.completed_at = timezone.now()
        self.save()

    def fail(self):
        """Mark job as failed"""
        self.status = "failed"
        self.completed_at = timezone.now()
        self.save()


class JobExecution(models.Model):
    """Record of each job run"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="executions")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    execution_time = models.FloatField(null=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Execution of {self.job.name}"

    @property
    def duration(self):
        """Calculate execution duration in seconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class JobLog(models.Model):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    LOG_TYPE_CHOICES = [
        (INFO, "Information"),
        (WARNING, "Warning"),
        (ERROR, "Error"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES, default=INFO)

    def __str__(self):
        return f"{self.job.name} - {self.timestamp} - {self.log_type}"

    class Meta:
        ordering = ["-timestamp"]
