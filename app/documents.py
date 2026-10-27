"""DOCX text extraction (paragraphs + tables, in reading order)."""
from docx import Document as DocxReader
from docx.table import Table
from docx.text.paragraph import Paragraph


class DocumentExtractionError(Exception):
    """Raised with a user-facing (Persian) message when a file can't be read."""


def _table_to_text(table: Table) -> str:
    lines = []
    for row in table.rows:
        cells, previous = [], None
        for cell in row.cells:
            text = " ".join(cell.text.split())
            # merged cells repeat the same text – skip consecutive duplicates
            if text and text != previous:
                cells.append(text)
            previous = text
        if cells:
            lines.append(" | ".join(cells))
    return "\n".join(lines)


def extract_docx_text(path) -> str:
    try:
        doc = DocxReader(str(path))
    except Exception as exc:  # BadZipFile, PackageNotFoundError, KeyError...
        raise DocumentExtractionError("فایل Word معتبر نیست یا آسیب دیده است.") from exc

    blocks = []
    for item in doc.iter_inner_content():
        if isinstance(item, Paragraph):
            text = item.text.strip()
        else:
            text = _table_to_text(item)
        if text:
            blocks.append(text)

    full_text = "\n\n".join(blocks).strip()
    if not full_text:
        raise DocumentExtractionError("هیچ متنی در این فایل پیدا نشد.")
    return full_text
