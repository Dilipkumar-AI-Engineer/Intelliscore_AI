"""
PDF text extraction via PyMuPDF (imported as `fitz`, its legacy module name).

Concept: PyMuPDF reads a PDF's internal text layer directly -- this works
for PDFs that contain real, selectable text (e.g. exported from Word,
Google Docs, LaTeX). It will NOT work for scanned/photographed PDFs with
no text layer, only page images -- those need OCR instead (see
image_ocr_parser.py). Detecting which case we're in is handled by
document_parser.py's facade: if PyMuPDF extracts near-zero text, that's
a signal the PDF is actually scanned and should fall back to OCR.
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """Extract all text from a PDF's text layer, page by page."""
    text_parts = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n\n".join(text_parts).strip()
