from rest_framework import serializers
from .models import JobApplication, Attachment, FollowUp, Notification

class JobApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobApplication
        fields = "__all__"
        read_only_fields = ("user",)

    def update(self, instance, validated_data):
        old_files = {}

        for field_name in ("resume_file", "cover_letter_file"):
            new_file = validated_data.get(field_name)

            if new_file:
                old_file = getattr(instance, field_name)

                if old_file and old_file.name:
                    old_files[field_name] = (
                        old_file.storage,
                        old_file.name,
                    )

        updated_instance = super().update(instance, validated_data)

        for field_name, (storage, old_name) in old_files.items():
            new_file = getattr(updated_instance, field_name)

            if new_file and new_file.name != old_name:
                if storage.exists(old_name):
                    storage.delete(old_name)

        return updated_instance


class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = "__all__"
        read_only_fields = ("file_size", "uploaded_at")

    def validate_application(self, value):
        request = self.context.get("request")

        if request and value.user_id != request.user.id:
            raise serializers.ValidationError(
                "You can only attach files to your own applications."
            )

        return value

    def create(self, validated_data):
        uploaded_file = validated_data.get("file")

        if uploaded_file:
            validated_data["file_size"] = uploaded_file.size

        return super().create(validated_data)


class FollowUpSerializer(serializers.ModelSerializer):

    class Meta:
        model = FollowUp
        fields = "__all__"

    def validate_application(self, value):
        request = self.context.get("request")

        if request and value.user_id != request.user.id:
            raise serializers.ValidationError(
                "You can only add follow-ups to your own applications."
            )

        return value
class NotificationSerializer(serializers.ModelSerializer):
    application_id = serializers.IntegerField(
        source="follow_up.application_id",
        read_only=True
    )

    company = serializers.CharField(
        source="follow_up.application.company",
        read_only=True
    )

    role = serializers.CharField(
        source="follow_up.application.role",
        read_only=True
    )

    follow_up_date = serializers.DateField(
        source="follow_up.follow_up_date",
        read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "follow_up",
            "application_id",
            "company",
            "role",
            "follow_up_date",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "user",
            "follow_up",
            "title",
            "message",
            "notification_type",
            "created_at",
            "updated_at",
        )