"""
Embedding model loader.

Model choice: `sentence-transformers/all-MiniLM-L6-v2` -- a small
(80MB, 384-dimensional output), fast, CPU-friendly model specifically
trained with a contrastive objective for semantic similarity tasks. This
matters: a raw DeBERTa-v3-base encoder is NOT trained to produce
embeddings where cosine similarity reflects meaning similarity -- it's a
general-purpose language model. Sentence-Transformers models ARE trained
for exactly that, which is why they're the right tool for coherence
scoring specifically (a true DeBERTa fine-tuning path, for an
end-to-end learned scorer, is deferred -- see Module 4 notes).

Like ml/nlp/preprocessing.py's spaCy loader, this model is loaded ONCE
and reused -- loading model weights from disk is expensive and must not
happen per-essay.
"""

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None


def get_embedding_model():
    """
    Lazily load and cache the sentence embedding model.

    Deliberately NOT imported at module load time (unlike spaCy in
    Module 1) -- this model requires a one-time download from Hugging
    Face's hub on first use, which we don't want triggered just by
    importing this file (e.g. during tests that don't need it).
    """
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model
