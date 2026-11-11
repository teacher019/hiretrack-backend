from django.contrib import admin
from .models import JobApplication, Attachment, FollowUp


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "role",
        "candidate_name",
        "status",
        "application_date",
    )
    list_filter = ("status", "job_type")
    search_fields = ("company", "role", "candidate_name")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("original_name", "application", "file_size", "uploaded_at")
    search_fields = ("original_name",)


@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = ("application", "follow_up_date", "completed")
    list_filter = ("completed",)