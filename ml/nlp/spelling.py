"""
Spelling mistake detection.

Uses `pyspellchecker` — a pure-Python, dictionary + edit-distance based
checker (no Java, no network calls, works fully offline). It flags words
not found in its English dictionary and suggests the most likely
correction based on edit distance and word frequency.

Important limitation to be upfront about: dictionary-based spellcheckers
cannot catch mistakes that happen to form a DIFFERENT valid word (e.g.
"there" vs "their", "affect" vs "effect"). Catching those requires
context-aware grammar checking, which is a known gap here — flagged in
Module 2's README notes as a candidate for a future LLM-assisted pass
(Module 11's AI Writing Mentor is a natural place to add this later).
"""

import re

from spellchecker import SpellChecker

_spell = SpellChecker()

# Words that are valid in academic/essay contexts but may not be in the
# default dictionary (proper nouns, common academic terms). Extend this
# list as false positives are discovered during testing.
_CUSTOM_WHITELIST = {
    "esg", "covid", "ai", "nlp", "gdp", "ceo", "un", "nasa",
}


def analyze_spelling(raw_text: str) -> dict:
    """
    Find misspelled words and suggest corrections.
    Named entities and proper nouns should ideally be excluded by the
    caller (ml/nlp/linguistic_features.py already extracts these) —
    this function operates on raw words only.
    """
    # Extract alphabetic words only, lowercase for dictionary lookup,
    # but keep original casing for the display report.
    words_with_original_case = re.findall(r"[A-Za-z']+", raw_text)

    misspelled_lookup = {}
    seen_lowercase = set()

    for word in words_with_original_case:
        lower = word.lower()
        if lower in seen_lowercase:
            continue
        if lower in _CUSTOM_WHITELIST:
            continue
        seen_lowercase.add(lower)

        if lower in _spell:
            continue  # correctly spelled

        # `unknown()` re-confirms it's not recognized (accounts for
        # case/frequency nuances); skip single-letter tokens (e.g. "a", "I"
        # artifacts) which are always technically "unknown" to the checker.
        if len(lower) <= 1:
            continue
        if lower not in _spell.unknown([lower]):
            continue

        correction = _spell.correction(lower)
        if correction and correction != lower:
            misspelled_lookup[word] = correction

    misspelled_list = [
        {"word": original, "suggested_correction": correction}
        for original, correction in misspelled_lookup.items()
    ]

    return {
        "misspelled_count": len(misspelled_list),
        "misspelled_words": misspelled_list,
    }
