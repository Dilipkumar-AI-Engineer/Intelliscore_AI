"""
Shared text preprocessing utilities for the NLP feature extraction pipeline.

Design decision: we load the spaCy model ONCE at module level (not inside
every function call). Loading a spaCy model involves reading trained
weights from disk — doing that per-essay would make the app unusably slow
once we're processing hundreds of essays. Every function in this package
receives an already-processed spaCy `Doc` object rather than raw text,
so the expensive parsing step happens exactly once per essay.
"""

import re

import spacy

# Loaded once, reused everywhere. `en_core_web_sm` gives us tokenization,
# sentence boundaries, POS tags, and named entities in a single pipeline.
try:
    _nlp = spacy.load("en_core_web_sm")
except Exception:
    _nlp = spacy.blank("en")


def get_nlp():
    """Expose the shared spaCy pipeline so other modules don't each load their own."""
    return _nlp


def split_paragraphs(raw_text: str) -> list[str]:
    """
    Split raw essay text into paragraphs.

    Convention: a paragraph break is one or more blank lines. This is a
    simple heuristic — it assumes essays are typed/pasted with blank lines
    between paragraphs (true for DOCX/plain text exports, which is what
    Module 6's document parsers will hand us). Single newlines within a
    paragraph (soft wraps) are NOT treated as paragraph breaks.
    """
    # Normalize Windows-style line endings before splitting.
    normalized = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    raw_paragraphs = re.split(r"\n\s*\n", normalized)
    return [p.strip() for p in raw_paragraphs if p.strip()]


def process_text(raw_text: str) -> spacy.tokens.Doc:
    """
    Run the full spaCy pipeline on cleaned essay text.

    We collapse internal whitespace/newlines to single spaces before
    parsing — spaCy's sentence segmenter can misfire on essays with
    irregular line breaks (e.g. text extracted from a PDF where every
    visual line ends in \\n even mid-sentence).
    """
    cleaned = re.sub(r"\s+", " ", raw_text).strip()
    return _nlp(cleaned)
