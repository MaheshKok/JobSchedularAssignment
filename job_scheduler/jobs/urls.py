from django.urls import path, include
from rest_framework import routers
from . import views

# DRF router
router = routers.DefaultRouter()
router.register(r"jobs", views.JobViewSet, basename="api-job")
router.register(r"executions", views.JobExecutionViewSet, basename="api-execution")

app_name = "jobs"

urlpatterns = [
    # Web interface URLs
    path("", views.job_list, name="job_list"),
    path("create/", views.job_create, name="job_create"),
    path("<uuid:job_id>/", views.job_detail, name="job_detail"),
    path("<uuid:job_id>/edit/", views.job_edit, name="job_edit"),
    path("<uuid:job_id>/delete/", views.job_delete, name="job_delete"),
    path("stats/", views.job_stats, name="job_stats"),
    path("executions/", views.job_execution_list, name="job_execution_list"),
    # API URLs
    path("api/", include(router.urls)),
]
