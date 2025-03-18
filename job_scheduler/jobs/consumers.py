import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Job


class JobConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for providing real-time job updates"""

    async def connect(self):
        """
        Connect to the WebSocket and add to the jobs group.
        Authenticate the user and save their ID for later use.
        """
        self.user = self.scope["user"]

        # Anonymous users cannot connect
        if not self.user.is_authenticated:
            await self.close()
            return

        # Set the user-specific group name
        self.group_name = f"jobs_{self.user.id}"

        # Join user's group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

        # Send initial stats
        await self.send_job_stats()

    async def disconnect(self, close_code):
        """Leave the group when disconnecting"""
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        data = json.loads(text_data)
        command = data.get("command")

        if command == "get_stats":
            await self.send_job_stats()
        elif command == "get_jobs":
            status_filter = data.get("status")
            await self.send_job_list(status_filter)

    @database_sync_to_async
    def get_user_jobs_stats(self):
        """Get statistics about the user's jobs"""
        user_jobs = Job.objects.filter(user=self.user)

        # Get counts by status
        status_counts = {}
        for status, _ in Job.STATUS_CHOICES:
            status_counts[status] = user_jobs.filter(status=status).count()

        # Get counts by priority
        priority_counts = {}
        for priority, _ in Job.PRIORITY_CHOICES:
            priority_counts[priority] = user_jobs.filter(priority=priority).count()

        # Calculate average wait times
        waiting_times = []
        completed_jobs = user_jobs.filter(status="completed")
        for job in completed_jobs:
            if job.started_at and job.created_at:
                waiting_times.append((job.started_at - job.created_at).total_seconds())

        avg_wait_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0

        return {
            "status_counts": status_counts,
            "priority_counts": priority_counts,
            "avg_wait_time": avg_wait_time,
            "total_jobs": user_jobs.count(),
        }

    @database_sync_to_async
    def get_user_jobs(self, status_filter=None):
        """Get jobs belonging to the user with optional status filter"""
        query = Job.objects.filter(user=self.user)

        if status_filter and status_filter in dict(Job.STATUS_CHOICES):
            query = query.filter(status=status_filter)

        jobs = []
        for job in query.order_by("-created_at"):
            jobs.append(
                {
                    "id": str(job.id),
                    "name": job.name,
                    "status": job.status,
                    "priority": job.priority,
                    "deadline": job.deadline.isoformat() if job.deadline else None,
                    "created_at": job.created_at.isoformat(),
                    "started_at": job.started_at.isoformat()
                    if job.started_at
                    else None,
                    "completed_at": job.completed_at.isoformat()
                    if job.completed_at
                    else None,
                    "wait_time": job.wait_time,
                    "duration": job.duration,
                    "status_color": job.status_color,
                }
            )

        return jobs

    async def send_job_stats(self):
        """Send job statistics to the WebSocket"""
        stats = await self.get_user_jobs_stats()

        await self.send(text_data=json.dumps({"type": "stats", "data": stats}))

    async def send_job_list(self, status_filter=None):
        """Send job list to the WebSocket"""
        jobs = await self.get_user_jobs(status_filter)

        await self.send(text_data=json.dumps({"type": "jobs", "data": jobs}))

    async def job_update(self, event):
        """Handle job update event from channel layer"""
        await self.send(
            text_data=json.dumps({"type": "job_update", "data": event["data"]})
        )

    async def stats_update(self, event):
        """Handle stats update event from channel layer"""
        await self.send(text_data=json.dumps({"type": "stats", "data": event["data"]}))
