"""
Plain text (.txt) extraction.

Concept -- encoding handling: not all .txt files are UTF-8. A student
might upload a file saved by an older Windows tool in 'cp1252' (Windows-
1252) encoding, especially if it contains curly quotes or special
characters. We try UTF-8 first (the modern default), then fall back to
cp1252 with error replacement rather than crashing -- losing a rare
special character is much better than rejecting the whole upload.
"""


def extract_text_from_txt(file_path: str) -> str:
    """Read a plain text file, handling common encoding variations."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="cp1252", errors="replace") as f:
            return f.read().strip()
