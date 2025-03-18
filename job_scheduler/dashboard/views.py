# dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count

from jobs.models import Job


@login_required
def index(request):
    """
    Main dashboard view showing job statistics and recent jobs
    """
    # Get user's jobs
    user_jobs = Job.objects.filter(user=request.user)

    # Get counts for each status
    active_jobs_count = user_jobs.filter(status__in=["pending", "running"]).count()
    completed_jobs_count = user_jobs.filter(status="completed").count()
    failed_jobs_count = user_jobs.filter(status="failed").count()

    # Get recent jobs
    recent_jobs = user_jobs.order_by("-created_at")[:10]

    # Priority statistics
    priority_counts = user_jobs.values("priority").annotate(count=Count("priority"))
    priority_stats = {item["priority"]: item["count"] for item in priority_counts}

    context = {
        "active_jobs_count": active_jobs_count,
        "completed_jobs_count": completed_jobs_count,
        "failed_jobs_count": failed_jobs_count,
        "recent_jobs": recent_jobs,
        "priority_stats": priority_stats,
        "total_jobs": user_jobs.count(),
    }

    return render(request, "dashboard/index.html", context)
