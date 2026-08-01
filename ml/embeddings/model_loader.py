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

Hardware note: this model (and device="cpu" below) was deliberately
chosen to run comfortably on modest hardware -- e.g. a dual-core laptop
CPU with 8GB RAM and integrated (non-CUDA) graphics. MiniLM's ~80MB of
weights and 384-dim output keep both load time and per-essay inference
memory low. Explicitly pinning device="cpu" avoids PyTorch spending time
probing for a CUDA GPU that doesn't exist on this kind of machine.

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
        import torch
        from sentence_transformers import SentenceTransformer

        # Match thread count to physical cores. PyTorch defaults to
        # spawning threads equal to ALL logical cores, which on a 2-core/
        # 4-thread CPU causes more contention/context-switching overhead
        # than benefit for a model this small. 2 threads is the sweet spot
        # for this hardware profile; raise it if running on a beefier machine.
        torch.set_num_threads(2)

        _model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cpu")
    return _model
