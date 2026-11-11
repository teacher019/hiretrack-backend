
from rest_framework.routers import DefaultRouter
from .views import (
    JobApplicationViewSet,
    AttachmentViewSet,
    FollowUpViewSet,
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

urlpatterns = router.urls
