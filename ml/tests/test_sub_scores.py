"""
Tests for ml/scoring/sub_scores.py using hand-built feature dicts --
no model or text processing needed, since these are pure functions
operating on already-extracted features.

Run with: pytest ml/tests/test_sub_scores.py -v
"""

from ml.scoring.sub_scores import (
    compute_all_sub_scores,
    compute_argument_score,
    compute_coherence_score,
    compute_grammar_score,
    compute_readability_score,
    compute_vocabulary_score,
)

GOOD_FEATURES = {
    "spelling": {"misspelled_count": 0},
    "passive_voice": {"passive_ratio_percent": 5.0},
    "lexical_diversity": {"root_ttr": 6.5},
    "repeated_words": {"unique_overused_word_count": 0},
    "transitions": {"transitions_per_sentence": 0.5},
    "named_entities": [{"text": "NASA"}, {"text": "2030"}, {"text": "Paris"}],
    "basic_stats": {"avg_sentences_per_paragraph": 4.5},
    "readability": {"flesch_reading_ease": 65.0, "readability_label": "Standard"},
}

POOR_FEATURES = {
    "spelling": {"misspelled_count": 8},
    "passive_voice": {"passive_ratio_percent": 70.0},
    "lexical_diversity": {"root_ttr": 2.0},
    "repeated_words": {"unique_overused_word_count": 6},
    "transitions": {"transitions_per_sentence": 0.0},
    "named_entities": [],
    "basic_stats": {"avg_sentences_per_paragraph": 1.2},
    "readability": {"flesch_reading_ease": 20.0, "readability_label": "Very Difficult"},
}


def test_grammar_score_perfect_essay():
    result = compute_grammar_score(GOOD_FEATURES)
    assert result["score"] > 90


def test_grammar_score_poor_essay():
    result = compute_grammar_score(POOR_FEATURES)
    assert result["score"] < 50


def test_grammar_score_never_negative():
    extreme = {"spelling": {"misspelled_count": 100}, "passive_voice": {"passive_ratio_percent": 100}}
    result = compute_grammar_score(extreme)
    assert result["score"] == 0


def test_vocabulary_score_rewards_diversity():
    good = compute_vocabulary_score(GOOD_FEATURES)
    poor = compute_vocabulary_score(POOR_FEATURES)
    assert good["score"] > poor["score"]


def test_coherence_score_transitions_only():
    result = compute_coherence_score(GOOD_FEATURES, semantic_coherence=None)
    assert result["score"] > 0
    assert "Module 4" in result["explanation"]


def test_coherence_score_blends_semantic_when_available():
    semantic = {"local_coherence": {"avg_local_coherence": 0.9}}
    result = compute_coherence_score(GOOD_FEATURES, semantic_coherence=semantic)
    assert "semantic" in result["explanation"].lower()


def test_argument_score_never_exceeds_100():
    lots_of_entities = {
        "named_entities": [{"text": f"Entity{i}"} for i in range(50)],
        "basic_stats": {"avg_sentences_per_paragraph": 4.5},
    }
    result = compute_argument_score(lots_of_entities)
    assert result["score"] <= 100


def test_readability_score_matches_flesch_directly():
    result = compute_readability_score(GOOD_FEATURES)
    assert result["score"] == 65.0


def test_compute_all_sub_scores_returns_five_dimensions():
    result = compute_all_sub_scores(GOOD_FEATURES)
    assert set(result.keys()) == {"grammar", "vocabulary", "coherence", "argument", "readability"}
    for dimension in result.values():
        assert 0 <= dimension["score"] <= 100
        assert len(dimension["explanation"]) > 0


def test_good_essay_scores_higher_than_poor_essay_across_dimensions():
    good_scores = compute_all_sub_scores(GOOD_FEATURES)
    poor_scores = compute_all_sub_scores(POOR_FEATURES)
    for dimension in good_scores:
        assert good_scores[dimension]["score"] > poor_scores[dimension]["score"], (
            f"{dimension}: expected good > poor"
        )
