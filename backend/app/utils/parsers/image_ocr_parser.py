"""
Image OCR text extraction via EasyOCR.

Concept: for scanned/photographed essays (PNG/JPG uploads, or a scanned
PDF with no text layer), there's no text layer to read directly -- we
need Optical Character Recognition to detect and read characters from
pixels. EasyOCR uses a deep learning model (CRAFT for text detection +
a CRNN-style recognizer) trained across 80+ languages.

Hardware note: this is the heaviest parser in this module (PyTorch-based,
similar in spirit to Module 4's embedding model). Model weights download
automatically on first use (~10-20MB for English detection+recognition,
much lighter than Module 4's DeBERTa concerns). Expect a few seconds per
image on a CPU-only, low-core-count machine -- fine for occasional essay
uploads, not suitable for bulk/real-time processing at scale.

The reader is lazy-loaded and cached, same pattern as every other model
in this project (spaCy in Module 1, Sentence-Transformers in Module 4) --
loading model weights is expensive and must happen once, not per image.
"""

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr

        # gpu=False: forced explicitly since this project targets CPU-only
        # hardware (see hardware note above and Module 4's laptop
        # compatibility discussion) -- avoids EasyOCR spending time
        # probing for a CUDA GPU that isn't there.
        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


def extract_text_from_image(file_path: str) -> str:
    """
    Run OCR on an image file and return the detected text, reading
    order approximated top-to-bottom as EasyOCR returns detections.
    """
    reader = _get_reader()
    results = reader.readtext(file_path, detail=0)  # detail=0 -> just the text strings
    return "\n".join(results).strip()
