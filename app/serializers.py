# directory: app/serializers.py
from rest_framework import serializers
from.models import Document, QAHistory

class DocumentSerializer(serializers.ModelSerializer):
    """
    سریالایزر جامع اسناد جهت پردازش فرآیندهای CRUD وب‌سرویس.
    """
    text_length = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at', 'full_text', 'text_length']
        read_only_fields = ['uploaded_at', 'full_text']

    def get_text_length(self, obj):
        return len(obj.full_text) if obj.full_text else 0


class QAHistorySerializer(serializers.ModelSerializer):
    """
    سریالایزر تاریخچه تعاملات جهت ارائه گزارش‌های دقیق به کلاینت‌های متصل.
    """
    document_title = serializers.CharField(source='document.title', read_only=True)

    class Meta:
        model = QAHistory
        fields = ['id', 'document', 'document_title', 'question', 'answer', 'retrieved_context', 'created_at']
        read_only_fields = ['id', 'document_title', 'answer', 'retrieved_context', 'created_at']


class QueryRequestSerializer(serializers.Serializer):
    """
    سریالایزر اعتبارسنجی پرسش ورودی کلاینت به موتور استنتاجی RAG.
    """
    question = serializers.CharField(required=True, min_length=5, help_text="متن پرسش ارسالی کاربر")