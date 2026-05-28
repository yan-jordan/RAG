# directory: app/admin.py
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib import messages
from.models import Document, QAHistory
from.rag_service import RAGService

# تغییر تایتل‌ها و هدرهای پنل مدیریت جنگو به منظور شخصی‌سازی برند پروژه
admin.site.site_header = "سامانه مدیریت هوشمند اسناد سازمانی (RAG)"
admin.site.site_title = "پنل مدیریت اسناد"
admin.site.index_title = "داشبورد ناظر سیستم"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_at', 'get_text_character_count')
    search_fields = ('title', 'full_text')
    readonly_fields = ('full_text',)
    
    # شخصی‌سازی قالب نمایش فرم لیست اسناد برای افزودن دکمه دسترسی به بخش پرسش و پاسخ
    change_list_template = "admin/document_change_list_custom.html"

    def get_text_character_count(self, obj):
        return len(obj.full_text) if obj.full_text else 0
    get_text_character_count.short_description = "تعداد کاراکترهای استخراج‌شده"

    def get_urls(self):
        """
        افزودن مسیر نمای پرسش و پاسخ هوشمند به معماری آدرس‌های پنل مدیریت.
        """
        urls = super().get_urls()
        custom_urls = [
            path('ask-document-engine/', self.admin_site.admin_view(self.ask_document_engine_view), name='ask-document-engine'),
        ]
        return custom_urls + urls

    def ask_document_engine_view(self, request):
        """
        نمای پردازشی و نمایش صفحه هوشمند پرسش و پاسخ در چهارچوب امن پنل ادمین.
        """
        context = self.admin_site.each_context(request)
        context['title'] = "پرسش از اسناد هوشمند"
        
        if request.method == "POST":
            question_query = request.POST.get("question")
            if question_query and len(question_query.strip()) >= 5:
                # اجرای پردازش RAG و استخراج پاسخ‌ها
                answer, retrieved_context = RAGService.ask_question(question_query)
                context['question'] = question_query
                context['answer'] = answer
                context['retrieved_context'] = retrieved_context
                messages.success(request, "تحلیل معنایی با موفقیت انجام شد و پاسخ صادر گردید.")
            else:
                messages.error(request, "متن پرسش ورودی معتبر نیست یا بسیار کوتاه است (حداقل ۵ کاراکتر).")

        # واکشی ۱۰ فعالیت پایانی تعاملات کاربر برای نمایش در داشبورد سیستم
        context['recent_histories'] = QAHistory.objects.all().select_related('document')[:10]
        return TemplateResponse(request, "admin/ask_document_dashboard.html", context)


@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    list_display = ('get_truncated_question', 'document', 'created_at')
    list_filter = ('document', 'created_at')
    readonly_fields = ('document', 'question', 'answer', 'retrieved_context', 'created_at')
    search_fields = ('question', 'answer', 'retrieved_context')

    def get_truncated_question(self, obj):
        return obj.question[:60] + "..." if len(obj.question) > 60 else obj.question
    get_truncated_question.short_description = "پرسش ثبت شده"

    # لغو امکان افزودن یا تغییر تاریخچه از طریق پنل ادمین جهت حفظ جامعیت لاگ‌های سیستم
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False