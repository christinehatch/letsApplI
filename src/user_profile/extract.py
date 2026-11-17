"""
Plain text from profile uploads, read locally (Milestone 6.1).

No AI and no network: PDF text comes from PyMuPDF, Word text from the
.docx file's own XML, plain text is decoded as-is. Anything else is refused.
"""

from __future__ import annotations

import io
import re
import zipfile
from xml.etree import ElementTree

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 200_000

PDF = "pdf"
DOCX = "docx"
TXT = "txt"

_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class ExtractionError(ValueError):
    """The file can't be read; the message is safe to show the user."""


def file_type(filename: str, data: bytes) -> str:
    """Decide by content first (magic bytes), then by extension for plain text."""
    name = (filename or "").lower()
    if data.startswith(b"%PDF"):
        return PDF
    if data.startswith(b"PK") and name.endswith(".docx"):
        return DOCX
    if name.endswith((".txt", ".md")):
        return TXT
    raise ExtractionError("Upload a PDF, a Word (.docx) file, or a plain text file.")


def _tidy(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:MAX_TEXT_CHARS]


def _pdf_text(data: bytes) -> str:
    try:
        import pymupdf  # type: ignore
    except ImportError:  # older PyMuPDF
        import fitz as pymupdf  # type: ignore

    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            if doc.needs_pass:
                raise ExtractionError("This PDF is password-protected. Save an unlocked copy and upload that.")
            return "\n\n".join(page.get_text() for page in doc)
    except ExtractionError:
        raise
    except Exception:
        raise ExtractionError("This PDF couldn't be opened. It may be damaged.")


def _docx_text(data: bytes) -> str:
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            info = zf.getinfo("word/document.xml")
            if info.file_size > 50 * 1024 * 1024:
                raise ExtractionError("This Word file is too large to read.")
            xml = zf.read(info)
    except ExtractionError:
        raise
    except (zipfile.BadZipFile, KeyError):
        raise ExtractionError("This Word file couldn't be opened. Try saving it again as .docx or PDF.")

    root = ElementTree.fromstring(xml)
    paragraphs = []
    for p in root.iter(f"{_WORD_NS}p"):
        parts = []
        for node in p.iter():
            if node.tag == f"{_WORD_NS}t" and node.text:
                parts.append(node.text)
            elif node.tag == f"{_WORD_NS}tab":
                parts.append("\t")
            elif node.tag in (f"{_WORD_NS}br", f"{_WORD_NS}cr"):
                parts.append("\n")
        paragraphs.append("".join(parts))
    return "\n".join(paragraphs)


def extract_text(filename: str, data: bytes) -> tuple[str, str]:
    """Return (file_type, text). Raises ExtractionError with a user-facing message."""
    if not data:
        raise ExtractionError("That file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ExtractionError("That file is over 10 MB. Upload a smaller copy.")

    kind = file_type(filename, data)
    if kind == PDF:
        raw = _pdf_text(data)
    elif kind == DOCX:
        raw = _docx_text(data)
    else:
        raw = data.decode("utf-8", errors="replace")

    text = _tidy(raw)
    if not text:
        if kind == PDF:
            raise ExtractionError(
                "No text found in this PDF. It may be a scanned image; upload a PDF with selectable text."
            )
        raise ExtractionError("No text found in this file.")
    return kind, text
