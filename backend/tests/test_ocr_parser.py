"""
Tests for the EasyOCR image parser.

Unlike PDF/DOCX/TXT (which are deterministic, byte-exact extraction),
OCR is a machine learning prediction -- it can misread individual
characters (e.g. "Renewable" -> "Reneiable") even on clean, synthetic
text. Assertions here are deliberately LENIENT: we check that OCR ran
successfully and detected the general content, not that it transcribed
every character perfectly. Verified working live during development
(see ml/embeddings/README.md for the analogous situation with Module 4 --
this one, unlike that one, WAS successfully tested end-to-end here,
since EasyOCR's models are hosted on GitHub releases, which this sandbox
can reach, unlike Hugging Face's hub).

Run with: pytest backend/tests/test_ocr_parser.py -v
NOTE: first run downloads ~10-20MB of model weights and will be slower.
"""

from PIL import Image, ImageDraw

from app.utils.parsers.document_parser import extract_text
from app.utils.parsers.image_ocr_parser import extract_text_from_image


def _make_text_image(path: str, text: str):
    img = Image.new("RGB", (600, 150), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), text, fill="black")
    img.save(path)


def test_ocr_detects_text_in_image(tmp_path):
    image_path = tmp_path / "essay_snippet.png"
    _make_text_image(str(image_path), "Renewable energy is the future")

    text = extract_text_from_image(str(image_path))

    # Lenient check: OCR should detect the KEY WORDS, not necessarily
    # transcribe every character perfectly.
    assert "energy" in text.lower()
    assert "future" in text.lower()


def test_facade_dispatches_png_to_ocr(tmp_path):
    image_path = tmp_path / "essay_snippet.png"
    _make_text_image(str(image_path), "Climate change policy")

    text = extract_text(str(image_path), "essay_snippet.png")
    assert len(text) > 0


def test_facade_dispatches_jpg_to_ocr(tmp_path):
    image_path = tmp_path / "essay_snippet.jpg"
    img = Image.new("RGB", (600, 150), color="white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 50), "Solar panel adoption", fill="black")
    img.save(str(image_path), format="JPEG")

    text = extract_text(str(image_path), "essay_snippet.jpg")
    assert len(text) > 0
