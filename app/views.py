import logging

from django.conf import settings
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Document, QAHistory
from .rag_service import RAGConfigError, RAGService, RAGUpstreamError
from .serializers import (
    DocumentDetailSerializer,
    DocumentRenameSerializer,
    DocumentSerializer,
    QAHistorySerializer,
    QueryRequestSerializer,
)

log = logging.getLogger(__name__)


class DocumentViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Upload (.docx), list, inspect, rename and delete documents."""

    queryset = Document.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DocumentDetailSerializer
        if self.action == "partial_update":
            return DocumentRenameSerializer
        return DocumentSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # re-read: text extraction runs inside save() after the first insert
        document = Document.objects.get(pk=response.data["id"])
        response.data = DocumentSerializer(document, context=self.get_serializer_context()).data
        return response


class HistoryPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100


class QAHistoryViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Read, delete or clear past questions and answers."""

    queryset = QAHistory.objects.select_related("document")
    serializer_class = QAHistorySerializer
    pagination_class = HistoryPagination

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        deleted, _ = QAHistory.objects.all().delete()
        return Response({"deleted": deleted})


class AskQuestionAPIView(APIView):
    """Answer a question from the uploaded documents."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ask"

    def post(self, request):
        serializer = QueryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data["question"]
        document_ids = serializer.validated_data.get("document_ids") or None

        try:
            result = RAGService.ask_question(question, document_ids)
        except RAGConfigError as exc:
            return Response({"detail": str(exc), "code": "not_configured"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except RAGUpstreamError as exc:
            return Response({"detail": str(exc), "code": "upstream_error"}, status=status.HTTP_502_BAD_GATEWAY)

        return Response(
            {
                "history_id": result.history.id if result.history else None,
                "question": question,
                "answer": result.answer,
                "sources": result.sources,
                "context_retrieved": result.context,
                "created_at": result.history.created_at if result.history else None,
            }
        )


class StatusAPIView(APIView):
    """Health + config snapshot the frontend uses for its status indicator."""

    def get(self, request):
        documents = Document.objects.all()
        return Response(
            {
                "configured": bool(settings.OPENROUTER_API_KEY) or settings.RAG_DEMO_MODE,
                "demo_mode": settings.RAG_DEMO_MODE,
                "chat_model": "offline-extractive" if settings.RAG_DEMO_MODE else settings.RAG_CHAT_MODEL,
                "embedding_model": "hashing-lexical" if settings.RAG_DEMO_MODE else settings.RAG_EMBEDDING_MODEL,
                "max_upload_mb": settings.MAX_UPLOAD_MB,
                "documents": {
                    "total": documents.count(),
                    "ready": documents.filter(status=Document.Status.READY).count(),
                    "failed": documents.filter(status=Document.Status.FAILED).count(),
                },
                "questions": QAHistory.objects.count(),
            }
        )
