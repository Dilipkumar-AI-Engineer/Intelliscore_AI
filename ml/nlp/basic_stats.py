"""
Basic structural statistics: counts and estimates that don't require
linguistic analysis, just counting tokens/sentences/paragraphs.
"""

from spacy.tokens import Doc

# Average adult silent reading speed. Used only for the "estimated reading
# time" UI display — not a scoring feature.
WORDS_PER_MINUTE = 200


def compute_basic_stats(doc: Doc, raw_text: str) -> dict:
    """
    Compute word count, sentence count, paragraph count, and reading time.

    We deliberately exclude punctuation-only tokens from the word count
    (e.g. a standalone "." or "," is a spaCy token but not a word) —
    otherwise essays with heavy punctuation would show inflated word counts.
    """
    words = [token for token in doc if not token.is_punct and not token.is_space]
    sentences = list(doc.sents)

    # Reuse the same paragraph-splitting logic as preprocessing so counts
    # are consistent with what the user sees in the essay preview.
    from ml.nlp.preprocessing import split_paragraphs

    paragraphs = split_paragraphs(raw_text)

    word_count = len(words)
    sentence_count = max(len(sentences), 1)  # avoid divide-by-zero downstream
    paragraph_count = max(len(paragraphs), 1)

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_words_per_sentence": round(word_count / sentence_count, 2),
        "avg_sentences_per_paragraph": round(sentence_count / paragraph_count, 2),
        "estimated_reading_time_minutes": round(word_count / WORDS_PER_MINUTE, 1),
    }
