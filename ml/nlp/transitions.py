"""
Transition word analysis.

Concept: transition words (also called "connectors" or "linking phrases")
signal logical structure to the reader — addition, contrast, cause/effect,
sequence, and conclusion. Essays with too few transitions often read as a
disconnected list of statements rather than a coherent argument.

This is implemented as a curated-phrase-list lookup rather than an ML
model — transition words are a closed, well-known set in English
academic writing, so a lookup is both more precise AND fully explainable
to the student (no black box).
"""

import re

TRANSITION_CATEGORIES = {
    "addition": [
        "additionally", "furthermore", "moreover", "in addition", "besides",
        "also", "similarly", "likewise",
    ],
    "contrast": [
        "however", "on the other hand", "nevertheless", "nonetheless",
        "conversely", "in contrast", "despite", "although", "whereas",
        "yet", "but",
    ],
    "cause_effect": [
        "therefore", "thus", "consequently", "as a result", "because",
        "due to", "hence", "accordingly",
    ],
    "sequence": [
        "first", "second", "third", "next", "then", "finally",
        "subsequently", "meanwhile", "afterward",
    ],
    "conclusion": [
        "in conclusion", "to summarize", "in summary", "overall",
        "ultimately", "in short",
    ],
    "example": [
        "for example", "for instance", "specifically", "such as",
        "namely", "to illustrate",
    ],
}

# Flatten to a single list of (phrase, category) pairs, longest phrases
# first so multi-word phrases like "as a result" match before shorter
# overlapping single words would.
_ALL_PHRASES = sorted(
    ((phrase, category) for category, phrases in TRANSITION_CATEGORIES.items() for phrase in phrases),
    key=lambda pair: len(pair[0]),
    reverse=True,
)


def analyze_transitions(raw_text: str, sentence_count: int) -> dict:
    """
    Find transition words/phrases used in the essay and report coverage
    by category. `sentence_count` (from basic_stats) is used to compute a
    rough "transitions per sentence" density metric.
    """
    text_lower = raw_text.lower()
    found = []
    category_counts = {category: 0 for category in TRANSITION_CATEGORIES}

    # Avoid double-counting: once a span of text is matched by a longer
    # phrase, don't also match a shorter phrase contained within it.
    matched_spans = []

    for phrase, category in _ALL_PHRASES:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        for match in re.finditer(pattern, text_lower):
            span = (match.start(), match.end())
            overlaps = any(span[0] < end and span[1] > start for start, end in matched_spans)
            if overlaps:
                continue
            matched_spans.append(span)
            found.append({"phrase": phrase, "category": category})
            category_counts[category] += 1

    total_found = len(found)

    return {
        "total_transitions_found": total_found,
        "transitions_per_sentence": round(total_found / max(sentence_count, 1), 2),
        "category_breakdown": category_counts,
        "phrases_found": found,
    }
