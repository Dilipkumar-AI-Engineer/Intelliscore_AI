"""
Tests for the Module 1 NLP feature extraction pipeline.

Run with: pytest ml/tests/test_feature_extractor.py -v
"""

import pytest

from ml.nlp.feature_extractor import extract_features

SAMPLE_ESSAY = """
Climate change is one of the most pressing challenges of our time. Scientists
around the world, including researchers at NASA and the United Nations, have
gathered extensive evidence showing that global temperatures are rising.

This warming trend affects ecosystems, agriculture, and human health. Many
countries have begun implementing renewable energy policies to reduce carbon
emissions. However, significant work remains to meet international climate
goals set for 2030.

In conclusion, addressing climate change requires coordinated global action,
sustained investment in clean technology, and public awareness. The decisions
made today will determine the world future generations inherit.
"""


def test_extract_features_returns_all_sections():
    result = extract_features(SAMPLE_ESSAY)
    expected_sections = {
        "basic_stats",
        "readability",
        "pos_distribution",
        "named_entities",
        "lexical_diversity",
        "keywords",
    }
    assert expected_sections.issubset(result.keys())


def test_basic_stats_are_sane():
    result = extract_features(SAMPLE_ESSAY)
    stats = result["basic_stats"]

    assert stats["word_count"] > 50
    assert stats["sentence_count"] >= 5
    assert stats["paragraph_count"] == 3  # three blank-line-separated paragraphs
    assert stats["avg_words_per_sentence"] > 0
    assert stats["estimated_reading_time_minutes"] > 0


def test_readability_score_in_valid_range():
    result = extract_features(SAMPLE_ESSAY)
    readability = result["readability"]

    # Flesch Reading Ease can technically go slightly outside 0-100 for
    # extreme texts, but for normal prose it should fall roughly in range.
    assert -50 <= readability["flesch_reading_ease"] <= 121.22
    assert readability["flesch_kincaid_grade"] > 0
    assert readability["readability_label"] in {
        "Very Easy", "Easy", "Standard", "Fairly Difficult", "Difficult", "Very Difficult",
    }


def test_named_entities_detected():
    result = extract_features(SAMPLE_ESSAY)
    entity_texts = {ent["text"] for ent in result["named_entities"]}

    # NASA and United Nations should be picked up as organizations.
    assert "NASA" in entity_texts or "United Nations" in entity_texts


def test_pos_distribution_sums_correctly():
    result = extract_features(SAMPLE_ESSAY)
    pos = result["pos_distribution"]

    total_from_distribution = sum(v["count"] for v in pos["distribution"].values())
    assert total_from_distribution == pos["total_tagged_tokens"]


def test_lexical_diversity_computed():
    result = extract_features(SAMPLE_ESSAY)
    diversity = result["lexical_diversity"]

    assert diversity["unique_words"] > 0
    assert diversity["root_ttr"] > 0


def test_keywords_extracted():
    result = extract_features(SAMPLE_ESSAY)
    keywords = result["keywords"]

    assert len(keywords) > 0
    assert all("term" in kw and "score" in kw for kw in keywords)


def test_empty_text_raises_value_error():
    with pytest.raises(ValueError):
        extract_features("")

    with pytest.raises(ValueError):
        extract_features("   ")


def test_very_short_text_does_not_crash():
    # Edge case: a trivially short essay should still produce a result,
    # not crash the pipeline (e.g. a student submitting one sentence).
    result = extract_features("This is short.")
    assert result["basic_stats"]["word_count"] == 3
