# directory: app/views.py
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from.models import Document, QAHistory
from.serializers import DocumentSerializer, QAHistorySerializer, QueryRequestSerializer
from.rag_service import RAGService

class DocumentViewSet(viewsets.ModelViewSet):
    """
    مجموعه اکشن‌های استاندارد API جهت مدیریت فرآیندهای بارگذاری، حذف، ویرایش و مشاهده اسناد متنی.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class QAHistoryListView(viewsets.ReadOnlyModelViewSet):
    """
    نقطه دسترسی فقط‌خواندنی جهت پایش و دریافت سوابق پرسش‌ها و پاسخ‌های ثبت شده در سیستم.
    """
    queryset = QAHistory.objects.all()
    serializer_class = QAHistorySerializer


class AskQuestionAPIView(APIView):
    """
    نقطه دسترسی پردازش اصلی موتور RAG که پرسش را دریافت کرده و پاسخ نهایی را به همراه بافتار بازیابی شده برمی‌گرداند.
    """
    def post(self, request, *args, **kwargs):
        serializer = QueryRequestSerializer(data=request.data)
        if serializer.is_valid():
            question_text = serializer.validated_data['question']
            
            # فراخوانی هسته استنتاج هوشمند
            answer, retrieved_context = RAGService.ask_question(question_text)
            
            # بازگرداندن پاسخ نهایی به همراه متادیتای بافتار بازیابی شده
            return Response({
                "question": question_text,
                "answer": answer,
                "context_retrieved": retrieved_context
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)