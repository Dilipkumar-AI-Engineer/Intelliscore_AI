"""
Feature vectorization: the contract between NLP analysis and the ML model.

Concept: XGBoost (and every ML model) trains on a fixed-width numeric
matrix — every row (essay) must have the same columns in the same order.
But Module 1/2's `extract_features()` returns a nested, human-readable
dict whose keys can vary (e.g. `pos_distribution` only lists POS tags
that actually appeared in that essay).

This module is the ONE place that flattens that dict into a strict,
ordered vector. `FEATURE_NAMES` is the single source of truth for column
order — training and inference both import it from here, so it is
IMPOSSIBLE for the two to drift out of sync (a classic bug: training on
one feature order, predicting with another, and getting silently wrong
predictions with no error).
"""

from ml.nlp.feature_extractor import extract_features

# Fixed column order. Every entry here must always be produced by
# `vectorize_features`, even if the value is 0 (e.g. an essay with zero
# passive sentences still needs a "0" in that column, not a missing column).
FEATURE_NAMES = [
    "word_count",
    "sentence_count",
    "paragraph_count",
    "avg_words_per_sentence",
    "avg_sentences_per_paragraph",
    "flesch_reading_ease",
    "flesch_kincaid_grade",
    "pos_pct_nouns",
    "pos_pct_verbs",
    "pos_pct_adjectives",
    "pos_pct_adverbs",
    "pos_pct_pronouns",
    "named_entity_count",
    "unique_words",
    "root_ttr",
    "passive_ratio_percent",
    "unique_overused_word_count",
    "transitions_per_sentence",
    "misspelled_count",
]


def vectorize_features(features: dict) -> list[float]:
    """
    Flatten the nested feature dict (from extract_features) into the
    fixed-order numeric vector defined by FEATURE_NAMES.

    Uses `.get(..., 0)` defensively throughout: if an essay is short
    enough that, say, no adverbs appear, `pos_distribution` simply won't
    have an "Adverbs" key — that must map to 0, not crash the pipeline.
    """
    basic = features["basic_stats"]
    readability = features["readability"]
    pos_dist = features["pos_distribution"]["distribution"]
    diversity = features["lexical_diversity"]
    passive = features["passive_voice"]
    repeated = features["repeated_words"]
    transitions = features["transitions"]
    spelling = features["spelling"]

    def pos_pct(label: str) -> float:
        return pos_dist.get(label, {}).get("percentage", 0.0)

    return [
        basic["word_count"],
        basic["sentence_count"],
        basic["paragraph_count"],
        basic["avg_words_per_sentence"],
        basic["avg_sentences_per_paragraph"],
        readability["flesch_reading_ease"],
        readability["flesch_kincaid_grade"],
        pos_pct("Nouns"),
        pos_pct("Verbs"),
        pos_pct("Adjectives"),
        pos_pct("Adverbs"),
        pos_pct("Pronouns"),
        len(features["named_entities"]),
        diversity["unique_words"],
        diversity["root_ttr"],
        passive["passive_ratio_percent"],
        repeated["unique_overused_word_count"],
        transitions["transitions_per_sentence"],
        spelling["misspelled_count"],
    ]


def vectorize_text(raw_text: str) -> tuple[list[float], dict]:
    """
    Convenience wrapper: run the full Module 1/2 pipeline on raw essay
    text, then vectorize it. Returns both the vector (for the model) and
    the original nested features dict (for display/explanation in the UI).
    """
    features = extract_features(raw_text)
    return vectorize_features(features), features
