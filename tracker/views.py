from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import JobApplication, Attachment, FollowUp
from .serializers import (
    JobApplicationSerializer,
    AttachmentSerializer,
    FollowUpSerializer,
)


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Attachment.objects.filter(
            application__user=self.request.user
        ).order_by("-uploaded_at")

    def perform_destroy(self, instance):
        file_field = instance.file
        file_storage = file_field.storage
        file_name = file_field.name

        instance.delete()

        if file_name and file_storage.exists(file_name):
            file_storage.delete(file_name)


class FollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FollowUp.objects.filter(
            application__user=self.request.user
        ).order_by("-follow_up_date")
