"""
Readability scoring.

Concept: readability formulas estimate how difficult a text is to read,
based on sentence length and word/syllable complexity. They were
originally designed for grading textbooks, but are a standard signal in
automated essay scoring because overly simple OR overly convoluted
sentence structure both hurt writing quality.

We use the `textstat` library rather than hand-rolling syllable counting:
syllable counting from text alone is a solved-but-fiddly problem (English
spelling doesn't map cleanly to pronunciation), and textstat implements
the standard, peer-reviewed formulas correctly.
"""

import textstat


def compute_readability(raw_text: str) -> dict:
    """
    Returns Flesch Reading Ease (0-100, higher = easier) and
    Flesch-Kincaid Grade Level (approximate US school grade needed
    to comprehend the text).
    """
    return {
        "flesch_reading_ease": round(textstat.flesch_reading_ease(raw_text), 2),
        "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(raw_text), 2),
        "readability_label": _interpret_flesch(textstat.flesch_reading_ease(raw_text)),
    }


def _interpret_flesch(score: float) -> str:
    """
    Map the raw Flesch Reading Ease number to a human-readable label.
    Scale per the original Flesch formula documentation.
    """
    if score >= 90:
        return "Very Easy"
    if score >= 70:
        return "Easy"
    if score >= 60:
        return "Standard"
    if score >= 50:
        return "Fairly Difficult"
    if score >= 30:
        return "Difficult"
    return "Very Difficult"
