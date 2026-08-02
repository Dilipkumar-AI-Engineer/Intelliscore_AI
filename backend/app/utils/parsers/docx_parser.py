"""
DOCX text extraction via python-docx.

Concept: a DOCX file is internally a zip archive of XML files. python-docx
parses that structure for us and exposes paragraphs as simple text
objects. We join paragraphs with double newlines to preserve the
paragraph-break convention our preprocessing.py (Module 1) already
expects (blank-line-separated paragraphs).
"""

import docx


def extract_text_from_docx(file_path: str) -> str:
    """Extract all paragraph text from a DOCX file."""
    document = docx.Document(file_path)
    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs).strip()
