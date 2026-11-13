from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import JobApplication, Attachment, FollowUp, Notification
from .serializers import (
    JobApplicationSerializer,
    AttachmentSerializer,
    FollowUpSerializer,
    NotificationSerializer,
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
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).select_related(
            "follow_up",
            "follow_up__application"
        ).order_by("-created_at")

    @action(detail=False, methods=["post"])
    def sync(self, request):
        today = timezone.localdate()

        follow_ups = FollowUp.objects.filter(
            application__user=request.user,
            completed=False
        ).select_related("application")

        for follow_up in follow_ups:
            application = follow_up.application

            if follow_up.follow_up_date < today:
                notification_type = "overdue"
                title = "Overdue Follow-up"
                message = (
                    f"Your follow-up with {application.company} "
                    f"for {application.role} was due on "
                    f"{follow_up.follow_up_date}."
                )
            else:
                notification_type = "upcoming"
                title = "Upcoming Follow-up"
                message = (
                    f"Your follow-up with {application.company} "
                    f"for {application.role} is scheduled for "
                    f"{follow_up.follow_up_date}."
                )

            Notification.objects.update_or_create(
                user=request.user,
                follow_up=follow_up,
                defaults={
                    "title": title,
                    "message": message,
                    "notification_type": notification_type,
                }
            )

        # Remove notifications for completed follow-ups.
        Notification.objects.filter(
            user=request.user,
            follow_up__completed=True
        ).delete()

        notifications = self.get_queryset()

        return Response(
            self.get_serializer(notifications, many=True).data
        )

    @action(detail=True, methods=["patch"])
    def read(self, request, pk=None):
        notification = self.get_object()

        is_read = request.data.get("is_read", True)

        if not isinstance(is_read, bool):
            return Response(
                {"detail": "is_read must be a boolean."},
                status=status.HTTP_400_BAD_REQUEST
            )

        notification.is_read = is_read
        notification.save(update_fields=["is_read", "updated_at"])

        return Response(self.get_serializer(notification).data)