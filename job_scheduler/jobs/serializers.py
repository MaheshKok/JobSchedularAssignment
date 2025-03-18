# jobs/serializers.py
from rest_framework import serializers
from django.utils import timezone
from .models import Job, JobExecution


class JobSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField()
    priority_display = serializers.SerializerMethodField()
    wait_time = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Job
        fields = [
            "id",
            "name",
            "user",
            "estimated_duration",
            "priority",
            "priority_display",
            "deadline",
            "status",
            "status_display",
            "created_at",
            "started_at",
            "completed_at",
            "wait_time",
            "duration",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
            "started_at",
            "completed_at",
            "wait_time",
            "duration",
            "status_display",
            "priority_display",
        ]

    def get_status_display(self, obj):
        """Get human-readable status"""
        return dict(Job.STATUS_CHOICES).get(obj.status, obj.status)

    def get_priority_display(self, obj):
        """Get human-readable priority"""
        return dict(Job.PRIORITY_CHOICES).get(obj.priority, obj.priority)

    def get_wait_time(self, obj):
        """Get wait time in seconds"""
        return obj.wait_time

    def get_duration(self, obj):
        """Get job duration in seconds"""
        return obj.duration

    def validate_deadline(self, value):
        """Validate that the deadline is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future")
        return value

    def validate_estimated_duration(self, value):
        # Ensure estimated duration is positive
        if value <= 0:
            raise serializers.ValidationError(
                "Estimated duration must be greater than zero"
            )
        return value

    def create(self, validated_data):
        """Create a new job and set the user from the request"""
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class JobExecutionSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = JobExecution
        fields = [
            "id",
            "job",
            "started_at",
            "completed_at",
            "success",
            "error_message",
            "duration",
        ]
        read_only_fields = fields

    def get_duration(self, obj):
        """Get execution duration in seconds"""
        return obj.duration
