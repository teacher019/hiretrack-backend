
from django.db import models
from django.conf import settings


class JobApplication(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_applications",
        null=True,
        blank=True
    )
    # Original frontend ID for safe, duplicate-free migration
    legacy_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        unique=True
    )

    JOB_TYPE_CHOICES = [
        ("Full-time", "Full-time"),
        ("Part-time", "Part-time"),
        ("Remote", "Remote"),
        ("Contract", "Contract"),
        ("Internship", "Internship"),
    ]
    STATUS_CHOICES = [
        ("Applied", "Applied"),
        ("Interview", "Interview"),
        ("Offer", "Offer"),
        ("Rejected", "Rejected"),
    ]

    candidate_name = models.CharField(max_length=150)
    candidate_email = models.EmailField(blank=True)
    candidate_phone = models.CharField(max_length=30, blank=True)

    company = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    job_location = models.CharField(max_length=200, blank=True)
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        blank=True
    )

    job_url = models.URLField(blank=True)
    salary_range = models.CharField(max_length=100, blank=True)
    application_source = models.CharField(max_length=100, blank=True)

    application_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Applied"
    )

    resume_version = models.CharField(max_length=100, blank=True)
    resume_file = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True
    )
    cover_letter_file = models.FileField(
        upload_to="cover_letters/",
        blank=True,
        null=True
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company} - {self.role}"


class Attachment(models.Model):

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="attachments"
    )

    file = models.FileField(upload_to="attachments/")
    original_name = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name


class FollowUp(models.Model):

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name="follow_ups"
    )

    follow_up_date = models.DateField()
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application.company} - {self.follow_up_date}"

from django.db.models.signals import pre_delete
from django.dispatch import receiver


@receiver(pre_delete, sender=JobApplication)
def delete_application_files(sender, instance, **kwargs):
    file_fields = [
        instance.resume_file,
        instance.cover_letter_file,
    ]

    for file_field in file_fields:
        if file_field and file_field.name:
            file_name = file_field.name
            file_storage = file_field.storage

            if file_storage.exists(file_name):
                file_storage.delete(file_name)

    for attachment in instance.attachments.all():
        file_name = attachment.file.name
        file_storage = attachment.file.storage

        if file_name and file_storage.exists(file_name):
            file_storage.delete(file_name)

class Notification(models.Model):

    NOTIFICATION_TYPE_CHOICES = [
        ("upcoming", "Upcoming"),
        ("overdue", "Overdue"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    follow_up = models.OneToOneField(
        FollowUp,
        on_delete=models.CASCADE,
        related_name="notification"
    )

    title = models.CharField(max_length=200)
    message = models.TextField()

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.user}"
