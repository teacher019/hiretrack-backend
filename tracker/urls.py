
from rest_framework.routers import DefaultRouter
from .views import (
    JobApplicationViewSet,
    AttachmentViewSet,
    FollowUpViewSet,
    NotificationViewSet,
)

router = DefaultRouter()

router.register(
    "applications",
    JobApplicationViewSet,
    basename="application"
)

router.register(
    "attachments",
    AttachmentViewSet,
    basename="attachment"
)

router.register(
    "followups",
    FollowUpViewSet,
    basename="followup"
)

router.register(
    "notifications",
    NotificationViewSet,
    basename="notification"
)

urlpatterns = router.urls
