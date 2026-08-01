"""
Coherence math: pure functions operating on pre-computed embeddings.

Deliberately separated from model_loader.py and the text-processing
wrapper below. These functions take numpy arrays in, dicts out -- no
model loading, no network calls, no spaCy. This means they can be fully
unit tested with fabricated embeddings (see ml/tests/test_coherence.py),
which is how we validate this module's logic without needing the actual
Sentence-Transformers model downloaded.
"""

import numpy as np


def compute_local_coherence(embeddings: np.ndarray) -> dict:
    """
    Cosine similarity between each pair of CONSECUTIVE sentence embeddings.
    High average = smooth, logically connected flow. A low value at a
    specific index flags an abrupt topic jump at that transition.
    """
    n = len(embeddings)
    if n < 2:
        return {
            "avg_local_coherence": None,
            "min_local_coherence": None,
            "weakest_transition_sentence_index": None,
            "pairwise_similarities": [],
        }

    similarities = []
    for i in range(n - 1):
        sim = _cosine_similarity(embeddings[i], embeddings[i + 1])
        similarities.append(round(sim, 4))

    min_sim = min(similarities)
    weakest_index = similarities.index(min_sim)

    return {
        "avg_local_coherence": round(float(np.mean(similarities)), 4),
        "min_local_coherence": round(float(min_sim), 4),
        # +1 because this marks the transition INTO this sentence index
        # (i.e. the drop happens between sentence[weakest_index] and
        # sentence[weakest_index + 1]).
        "weakest_transition_sentence_index": weakest_index + 1,
        "pairwise_similarities": similarities,
    }


def compute_topic_focus(embeddings: np.ndarray) -> dict:
    """
    Cosine similarity of each sentence to the essay's centroid (mean
    embedding across all sentences). Sentences with low similarity to the
    centroid are candidates for "off-topic" or "wandering" content.
    """
    n = len(embeddings)
    if n < 2:
        return {
            "avg_topic_focus": None,
            "min_topic_focus": None,
            "least_focused_sentence_index": None,
        }

    centroid = np.mean(embeddings, axis=0)
    similarities = [round(_cosine_similarity(emb, centroid), 4) for emb in embeddings]

    min_sim = min(similarities)
    least_focused_index = similarities.index(min_sim)

    return {
        "avg_topic_focus": round(float(np.mean(similarities)), 4),
        "min_topic_focus": round(float(min_sim), 4),
        "least_focused_sentence_index": least_focused_index,
    }


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """Standard cosine similarity: dot product / (magnitude_a * magnitude_b)."""
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
