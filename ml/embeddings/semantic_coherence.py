"""
Semantic coherence analysis: the public entrypoint for Module 4.

This is the ONLY function in this module that touches the actual
embedding model -- everything else (coherence.py) is pure, pre-tested
math. This wrapper cannot be exercised in a network-restricted sandbox
since it triggers a model download on first call; it must be tested in
an environment with normal internet access.
"""

from ml.embeddings.coherence import compute_local_coherence, compute_topic_focus
from ml.embeddings.model_loader import get_embedding_model
from ml.nlp.preprocessing import process_text


def analyze_semantic_coherence(raw_text: str) -> dict:
    """
    Full semantic coherence analysis for an essay: splits into sentences,
    embeds each one, then computes local coherence (sentence-to-sentence
    flow) and topic focus (sentence-to-overall-theme relevance).
    """
    doc = process_text(raw_text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    if len(sentences) < 2:
        # Coherence is only meaningful across multiple sentences.
        return {
            "sentence_count_analyzed": len(sentences),
            "local_coherence": compute_local_coherence([]),
            "topic_focus": compute_topic_focus([]),
        }

    model = get_embedding_model()
    embeddings = model.encode(sentences)

    return {
        "sentence_count_analyzed": len(sentences),
        "local_coherence": compute_local_coherence(embeddings),
        "topic_focus": compute_topic_focus(embeddings),
        "sentences": sentences,  # so the UI can display which sentence is which index
    }
