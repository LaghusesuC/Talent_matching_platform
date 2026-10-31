"""
Resume and Job Description parsing service.
Extracts raw text from PDF and DOCX files.
Optimized for speed: uses PyMuPDF (fitz) as the primary fast PDF parser
with pdfplumber as fallback, and caches results by content hash.
"""
import io
import hashlib
from pathlib import Path


# In-memory cache for parsed text (keyed by MD5 of file content)
_text_cache: dict[str, str] = {}


def _content_hash(file_bytes: bytes) -> str:
    """Fast MD5 hash of file content for cache keying."""
    return hashlib.md5(file_bytes).hexdigest()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF (fast) with pdfplumber fallback."""
    # Try PyMuPDF first — significantly faster than pdfplumber
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text("text") for page in doc]
        doc.close()
        text = "\n".join(pages).strip()
        if text:
            return text
    except ImportError:
        pass  # PyMuPDF not installed, fall through to pdfplumber
    except Exception:
        pass  # PyMuPDF failed on this file, try pdfplumber

    # Fallback to pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n".join(pages).strip()
    except Exception as e:
        return f"[PDF parse error: {e}]"


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        return f"[DOCX parse error: {e}]"


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from a file, with in-memory caching for repeated uploads."""
    # Return cached result if this exact file was seen before
    content_hash = _content_hash(file_bytes)
    if content_hash in _text_cache:
        return _text_cache[content_hash]

    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        text = extract_text_from_docx(file_bytes)
    else:
        # Try as plain text
        try:
            text = file_bytes.decode("utf-8", errors="ignore").strip()
        except Exception:
            text = ""

    # Cache result
    _text_cache[content_hash] = text
    return text
