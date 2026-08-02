"""
Document parsing facade -- the single entrypoint the rest of the app
(the upload API route) calls. Same "facade" pattern as
ml/nlp/feature_extractor.py in Module 1: callers don't need to know
PyMuPDF, python-docx, or EasyOCR exist -- they just call
`extract_text(file_path, filename)` and get text back.
"""

import pathlib

from app.utils.parsers.docx_parser import extract_text_from_docx
from app.utils.parsers.image_ocr_parser import extract_text_from_image
from app.utils.parsers.pdf_parser import extract_text_from_pdf
from app.utils.parsers.txt_parser import extract_text_from_txt

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}

# Below this character count, a "successfully" extracted PDF is treated
# as suspicious -- likely a SCANNED PDF with no real text layer (just
# page images), where PyMuPDF's text extraction returns near-nothing.
MIN_PDF_TEXT_LENGTH_BEFORE_OCR_FALLBACK = 20


class UnsupportedFileTypeError(Exception):
    pass


class EmptyDocumentError(Exception):
    """Raised when a file was parsed successfully but contained no usable text."""
    pass


def extract_text(file_path: str, filename: str) -> str:
    """
    Extract text from an uploaded document, dispatching by file extension.

    Args:
        file_path: path to the file ON DISK (already saved by the caller).
        filename: the ORIGINAL filename (used only to read the extension --
                  the saved file_path may have a different name to avoid
                  collisions, see essay_service.py).
    """
    extension = pathlib.Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(
            f"'{extension}' is not supported. Supported types: "
            f"{', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    if extension == ".pdf":
        text = extract_text_from_pdf(file_path)
        if len(text) < MIN_PDF_TEXT_LENGTH_BEFORE_OCR_FALLBACK:
            # Likely a scanned PDF with no text layer -- but PyMuPDF can
            # also render PDF pages AS images for OCR fallback. That
            # render-to-image step is a reasonable Module 6+ enhancement;
            # for now we surface a clear error rather than silently
            # returning near-empty text.
            raise EmptyDocumentError(
                "This PDF appears to have no extractable text layer "
                "(likely a scanned document). Try uploading it as an "
                "image (PNG/JPG) instead, so OCR can be used."
            )
        return text

    if extension == ".docx":
        text = extract_text_from_docx(file_path)
    elif extension == ".txt":
        text = extract_text_from_txt(file_path)
    else:  # .png, .jpg, .jpeg
        text = extract_text_from_image(file_path)

    if not text or not text.strip():
        raise EmptyDocumentError("No readable text was found in this file.")

    return text
