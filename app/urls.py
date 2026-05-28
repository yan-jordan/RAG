# directory: app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from.views import DocumentViewSet, QAHistoryListView, AskQuestionAPIView

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='api-documents')
router.register(r'history', QAHistoryListView, basename='api-history')

urlpatterns = [
    path('', include(router.urls)),
    path('ask/', AskQuestionAPIView.as_view(), name='api-ask-question'),
]