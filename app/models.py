from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .documents import DocumentExtractionError, extract_docx_text


class Document(models.Model):
    """An uploaded Word file and the text extracted from it."""

    class Status(models.TextChoices):
        READY = "ready", "آماده"
        FAILED = "failed", "ناموفق"

    title = models.CharField(max_length=255, verbose_name="عنوان سند")
    file = models.FileField(
        upload_to="documents/",
        validators=[FileExtensionValidator(allowed_extensions=["docx"])],
        verbose_name="فایل سند (فقط DOCX)",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان بارگذاری")
    full_text = models.TextField(blank=True, verbose_name="متن کامل استخراج‌شده")
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.READY, verbose_name="وضعیت"
    )
    error_message = models.CharField(max_length=255, blank=True, verbose_name="پیام خطا")

    class Meta:
        verbose_name = "سند متنی"
        verbose_name_plural = "اسناد متنی"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        should_extract = (
            bool(self.file)
            and not kwargs.get("update_fields")
            and (self._state.adding or not self.full_text)
        )
        super().save(*args, **kwargs)
        if should_extract:
            self.extract_text()

    def extract_text(self):
        """Fill ``full_text`` / ``status``. A failure never pollutes ``full_text``."""
        try:
            self.full_text = extract_docx_text(self.file.path)
            self.status, self.error_message = self.Status.READY, ""
        except DocumentExtractionError as exc:
            self.full_text, self.status, self.error_message = "", self.Status.FAILED, str(exc)
        self.save(update_fields=["full_text", "status", "error_message"])


@receiver(post_delete, sender=Document)
def delete_document_file(sender, instance, **kwargs):
    """Don't leave orphaned .docx files on disk."""
    if instance.file:
        instance.file.delete(save=False)


class QAHistory(models.Model):
    """A question, its answer and the passages the answer was grounded on."""

    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qa_histories",
        verbose_name="سند مرجع اصلی",
    )
    question = models.TextField(verbose_name="پرسش کاربر")
    answer = models.TextField(verbose_name="پاسخ تولید شده")
    retrieved_context = models.TextField(blank=True, verbose_name="بافتار بازیابی‌شده")
    sources = models.JSONField(default=list, blank=True, verbose_name="منابع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ و زمان ثبت")

    class Meta:
        verbose_name = "تاریخچه پرسش و پاسخ"
        verbose_name_plural = "تاریخچه پرسش‌ها و پاسخ‌ها"
        ordering = ["-created_at"]

    def __str__(self):
        return f"پرسش: {self.question[:40]}..."
