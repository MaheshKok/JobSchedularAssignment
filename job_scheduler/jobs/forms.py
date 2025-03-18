from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Job


class JobForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
        ),
        help_text="Deadline for job completion",
    )

    class Meta:
        model = Job
        fields = ["name", "estimated_duration", "priority", "deadline"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["estimated_duration"].help_text = "Duration in seconds"
        self.fields["priority"].help_text = "Higher priority jobs are executed first"

        # Set default deadline to 24 hours from now
        if not self.instance.pk and not self.initial.get("deadline"):
            self.initial["deadline"] = (timezone.now() + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M"
            )

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Deadline must be in the future.")
        return deadline

    def clean_estimated_duration(self):
        duration = self.cleaned_data.get("estimated_duration")
        if duration <= 0:
            raise forms.ValidationError("Duration must be greater than zero")
        return duration
