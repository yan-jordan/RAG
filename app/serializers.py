import os
import zipfile
from pathlib import Path

from django.conf import settings
from rest_framework import serializers

from .models import Document, QAHistory


class DocumentSerializer(serializers.ModelSerializer):
    """Lightweight representation used in lists (no full text)."""

    text_length = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    title = serializers.CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = Document
        fields = [
            "id", "title", "file", "size", "uploaded_at",
            "status", "error_message", "text_length", "preview",
        ]
        read_only_fields = ["uploaded_at", "status", "error_message"]

    def get_text_length(self, obj):
        return len(obj.full_text)

    def get_preview(self, obj):
        return obj.full_text[:220]

    def get_size(self, obj):
        try:
            return obj.file.size
        except (OSError, ValueError):
            return None

    def validate_file(self, value):
        limit = settings.MAX_UPLOAD_MB * 1024 * 1024
        if value.size > limit:
            raise serializers.ValidationError(f"حجم فایل نباید بیشتر از {settings.MAX_UPLOAD_MB} مگابایت باشد.")
        # a .docx is a zip container – reject renamed / corrupt files early
        if not zipfile.is_zipfile(value):
            raise serializers.ValidationError("این فایل، یک سند Word معتبر نیست.")
        value.seek(0)
        return value

    def validate(self, attrs):
        if self.instance is None and not (attrs.get("title") or "").strip():
            attrs["title"] = Path(os.path.basename(attrs["file"].name)).stem[:255]
        return attrs


class DocumentDetailSerializer(DocumentSerializer):
    class Meta(DocumentSerializer.Meta):
        fields = DocumentSerializer.Meta.fields + ["full_text"]
        read_only_fields = DocumentSerializer.Meta.read_only_fields + ["full_text"]


class DocumentRenameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["title"]


class QAHistorySerializer(serializers.ModelSerializer):
    document_title = serializers.CharField(source="document.title", read_only=True, allow_null=True)

    class Meta:
        model = QAHistory
        fields = [
            "id", "document", "document_title", "question", "answer",
            "retrieved_context", "sources", "created_at",
        ]
        read_only_fields = fields


class QueryRequestSerializer(serializers.Serializer):
    question = serializers.CharField(min_length=3, max_length=1000, trim_whitespace=True)
    document_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), required=False, allow_empty=True, max_length=100
    )
