"""
Feature extraction orchestrator.

This is the single public entrypoint for Module 1. Every other layer of
the app (FastAPI routes, later the XGBoost scorer) should call
`extract_features(raw_text)` and get back one structured dict — they
should NOT need to know that spaCy, textstat, or scikit-learn exist
underneath. This is the "facade" pattern: hide subsystem complexity
behind one simple interface.
"""

from ml.nlp.basic_stats import compute_basic_stats
from ml.nlp.keywords import extract_keywords
from ml.nlp.linguistic_features import (
    compute_lexical_diversity,
    compute_named_entities,
    compute_pos_distribution,
)
from ml.nlp.preprocessing import process_text
from ml.nlp.readability import compute_readability


def extract_features(raw_text: str) -> dict:
    """
    Run the full NLP feature extraction pipeline on a single essay.

    Args:
        raw_text: The essay's raw text content (already extracted from
                   whatever source format — PDF/DOCX/OCR — by Module 6).

    Returns:
        A structured dict with basic_stats, readability, pos_distribution,
        named_entities, lexical_diversity, and keywords sections.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("Cannot extract features from empty text")

    # Parse ONCE, reuse the resulting Doc across every feature function
    # that needs tokens/sentences/POS/entities. This is the payoff of the
    # facade: callers never see this reuse happening, but it's why the
    # pipeline is fast.
    doc = process_text(raw_text)

    return {
        "basic_stats": compute_basic_stats(doc, raw_text),
        "readability": compute_readability(raw_text),
        "pos_distribution": compute_pos_distribution(doc),
        "named_entities": compute_named_entities(doc),
        "lexical_diversity": compute_lexical_diversity(doc),
        "keywords": extract_keywords(raw_text),
    }
