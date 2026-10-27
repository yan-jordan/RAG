"""Fill the database with the sample documents and a few answered questions.

    python manage.py seed_demo            # add what's missing
    python manage.py seed_demo --reset    # wipe documents + history first

Questions are answered with the offline demo retriever, so no API key is needed.
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.test.utils import override_settings

from app.models import Document, QAHistory
from app.rag_service import RAGService, reset_index_cache

QUESTIONS = [
    "مرخصی سالانه چند روزه؟",
    "زمان پاسخ‌گویی به درخواست بحرانی چقدر است؟",
    "اضافه‌کاری چطور پرداخت می‌شود؟",
    "نرخ حفظ مشتری در فصل سوم چقدر بود؟",
    "هزینه پشتیبانی سالانه چقدر است؟",
]


class Command(BaseCommand):
    help = "Create sample documents and question history for trying the app."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="delete all documents and history first")

    def handle(self, *args, reset=False, **options):
        samples = sorted((Path(settings.BASE_DIR) / "samples").glob("*.docx"))
        if not samples:
            raise CommandError("No files in ./samples — run `python scripts/make_samples.py` first.")

        if reset:
            for doc in Document.objects.all():
                doc.delete()  # also removes the stored file
            QAHistory.objects.all().delete()

        for path in samples:
            if Document.objects.filter(title=path.stem).exists():
                continue
            with path.open("rb") as fh:
                doc = Document.objects.create(title=path.stem, file=File(fh, name=path.name))
            self.stdout.write(f"  + {doc.title} ({doc.status}, {len(doc.full_text)} chars)")

        if not QAHistory.objects.exists():
            reset_index_cache()
            with override_settings(RAG_DEMO_MODE=True):
                for question in QUESTIONS:
                    RAGService.ask_question(question)
            reset_index_cache()
            self.stdout.write(f"  + {len(QUESTIONS)} answered questions")

        self.stdout.write(self.style.SUCCESS("Sample data ready."))
