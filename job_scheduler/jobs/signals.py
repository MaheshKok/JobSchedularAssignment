from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Job


@receiver(post_save, sender=Job)
def job_post_save(sender, instance, created, **kwargs):
    """
    Signal to send WebSocket notifications when a job is created or updated.
    Sends notifications to the job owner's group.
    """
    channel_layer = get_channel_layer()

    # Skip if no channel layer (e.g., during tests)
    if not channel_layer:
        return

    # Prepare job data for WebSocket
    job_data = {
        "id": str(instance.id),
        "name": instance.name,
        "status": instance.status,
        "priority": instance.priority,
        "deadline": instance.deadline.isoformat() if instance.deadline else None,
        "created_at": instance.created_at.isoformat(),
        "started_at": instance.started_at.isoformat() if instance.started_at else None,
        "completed_at": instance.completed_at.isoformat()
        if instance.completed_at
        else None,
        "wait_time": instance.wait_time,
        "duration": instance.duration,
        "status_color": instance.status_color,
    }

    # Send to user's group
    group_name = f"jobs_{instance.user.id}"

    # Send job update
    async_to_sync(channel_layer.group_send)(
        group_name, {"type": "job_update", "data": job_data}
    )

    # Also send updated stats for dashboard
    # This would typically be done only on status changes, but for simplicity
    # we'll send it on all updates
    async_to_sync(channel_layer.group_send)(
        group_name, {"type": "stats_update", "data": get_user_stats(instance.user)}
    )


def get_user_stats(user):
    """
    Get statistics about a user's jobs for WebSocket notifications
    """

    user_jobs = Job.objects.filter(user=user)

    # Get counts by status
    status_counts = {}
    for status, _ in Job.STATUS_CHOICES:
        status_counts[status] = user_jobs.filter(status=status).count()

    # Get counts by priority
    priority_counts = {}
    for priority, _ in Job.PRIORITY_CHOICES:
        priority_counts[priority] = user_jobs.filter(priority=priority).count()

    return {
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "total_jobs": user_jobs.count(),
    }
