from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AskQuestionAPIView, DocumentViewSet, QAHistoryViewSet, StatusAPIView

router = DefaultRouter(trailing_slash=True)
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"history", QAHistoryViewSet, basename="history")

urlpatterns = [
    path("", include(router.urls)),
    path("ask/", AskQuestionAPIView.as_view(), name="ask"),
    path("status/", StatusAPIView.as_view(), name="status"),
]
