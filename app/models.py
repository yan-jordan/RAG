# directory: app/models.py
from django.db import models
from django.core.validators import FileExtensionValidator
import os

class Document(models.Model):
    """
    مدل اصلی ذخیره‌سازی اطلاعات اسناد سازمانی و متون استخراج‌شده از آن‌ها.
    """
    title = models.CharField(max_length=255, verbose_name="عنوان سند")
    file = models.FileField(
        upload_to="documents/", 
        validators=[FileExtensionValidator(allowed_extensions=['docx'])],
        verbose_name="فایل سند (فقط DOCX)"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان بارگذاری")
    full_text = models.TextField(blank=True, verbose_name="متن کامل استخراج‌شده")

    class Meta:
        verbose_name = "سند متنی"
        verbose_name_plural = "اسناد متنی"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        بازنویسی متد ذخیره‌سازی به منظور استخراج خودکار متون بلافاصله پس از بارگذاری فایل.
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # فرآیند استخراج متن در صورت وجود فایل جدید یا خالی بودن فیلد متن کامل
        if self.file and (is_new or not self.full_text):
            self.extract_document_text()

    def extract_document_text(self):
        """
        استخراج متن از فایل ورد به کمک کتابخانه python-docx با ایجاد مکانیسم دفاعی در برابر خطاهای سیستمی.
        """
        from docx import Document as DocxReader
        try:
            doc_path = self.file.path
            doc = DocxReader(doc_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            self.full_text = "\n\n".join(paragraphs)
            # بروزرسانی اختصاصی فیلد متنی بدون فعال‌سازی مجدد زنجیره ذخیره‌سازی سیگنال‌ها
            Document.objects.filter(pk=self.pk).update(full_text=self.full_text)
        except Exception as e:
            # ذخیره گزارش خطا در فیلد متنی در صورت بروز نقص فنی در فرآیند پارس فایل
            self.full_text = f"خطای فنی در پردازش و استخراج محتوای فایل ورد رخ داده است: {str(e)}"
            Document.objects.filter(pk=self.pk).update(full_text=self.full_text)


class QAHistory(models.Model):
    """
    مدل ذخیره‌سازی تاریخچه کامل پرسش‌ها، پاسخ‌های هوشمند و جزئیات بافتار بازیابی‌شده.
    """
    document = models.ForeignKey(
        Document, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="qa_histories", 
        verbose_name="سند مرجع اصلی"
    )
    question = models.TextField(verbose_name="پرسش کاربر")
    answer = models.TextField(verbose_name="پاسخ تولید شده")
    retrieved_context = models.TextField(blank=True, verbose_name="بافتار بازیابی‌شده از سند برداری")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ثبت")

    class Meta:
        verbose_name = "تاریخچه پرسش و پاسخ"
        verbose_name_plural = "تاریخچه پرسش‌ها و پاسخ‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"پرسش: {self.question[:40]}..."