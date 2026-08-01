"""
Tests for Module 4's coherence math (ml/embeddings/coherence.py).

These tests use HAND-CONSTRUCTED embeddings, not the real
Sentence-Transformers model -- this validates the math is correct
without requiring a model download. The model-calling wrapper
(semantic_coherence.py) is NOT tested here; it must be verified locally
in an environment with internet access to Hugging Face's model hub.

Run with: pytest ml/tests/test_coherence.py -v
"""

import numpy as np

from ml.embeddings.coherence import compute_local_coherence, compute_topic_focus


def test_local_coherence_identical_sentences_scores_perfect():
    # Three identical embeddings -> every consecutive pair has cosine
    # similarity of exactly 1.0 (perfectly coherent, trivially).
    embeddings = np.array([[1.0, 0.0, 0.0]] * 3)
    result = compute_local_coherence(embeddings)
    assert result["avg_local_coherence"] == 1.0
    assert result["min_local_coherence"] == 1.0


def test_local_coherence_orthogonal_sentences_scores_zero():
    # Two perpendicular vectors have cosine similarity 0 -- maximally
    # "unrelated" by this measure.
    embeddings = np.array([[1.0, 0.0], [0.0, 1.0]])
    result = compute_local_coherence(embeddings)
    assert result["avg_local_coherence"] == 0.0


def test_local_coherence_flags_weakest_transition():
    # Sentences 0-1 are similar (coherent), sentence 2 jumps to an
    # unrelated topic (orthogonal), sentence 3 returns to the original topic.
    embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.9, 0.1, 0.0],   # similar to sentence 0 -> high coherence
        [0.0, 0.0, 1.0],   # orthogonal jump -> low coherence at this transition
        [0.1, 0.0, 0.9],   # similar to sentence 2
    ])
    result = compute_local_coherence(embeddings)
    # The weakest transition is INTO sentence index 2 (the topic jump).
    assert result["weakest_transition_sentence_index"] == 2
    assert result["min_local_coherence"] < result["avg_local_coherence"]


def test_local_coherence_handles_single_sentence():
    embeddings = np.array([[1.0, 0.0, 0.0]])
    result = compute_local_coherence(embeddings)
    assert result["avg_local_coherence"] is None
    assert result["pairwise_similarities"] == []


def test_local_coherence_handles_empty_input():
    result = compute_local_coherence([])
    assert result["avg_local_coherence"] is None


def test_topic_focus_identical_sentences_all_centered():
    embeddings = np.array([[1.0, 0.0, 0.0]] * 4)
    result = compute_topic_focus(embeddings)
    assert result["avg_topic_focus"] == 1.0
    assert result["min_topic_focus"] == 1.0


def test_topic_focus_flags_outlier_sentence():
    # Three sentences clustered around one topic, one clear outlier.
    embeddings = np.array([
        [1.0, 0.0, 0.0],
        [0.95, 0.05, 0.0],
        [0.9, 0.1, 0.0],
        [0.0, 0.0, 1.0],  # outlier: unrelated to the other three
    ])
    result = compute_topic_focus(embeddings)
    assert result["least_focused_sentence_index"] == 3
    assert result["min_topic_focus"] < result["avg_topic_focus"]


def test_topic_focus_handles_single_sentence():
    embeddings = np.array([[1.0, 0.0, 0.0]])
    result = compute_topic_focus(embeddings)
    assert result["avg_topic_focus"] is None


def test_zero_vector_does_not_crash():
    # Defensive edge case: a zero vector (shouldn't occur with real
    # embeddings, but must not cause a division-by-zero crash).
    embeddings = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0]])
    result = compute_local_coherence(embeddings)
    assert result["pairwise_similarities"][0] == 0.0
