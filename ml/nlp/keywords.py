"""
TF-IDF keyword extraction.

Concept: TF-IDF (Term Frequency - Inverse Document Frequency) scores each
word by how often it appears in THIS essay, discounted by how common it is
across essays in general. This surfaces words that are distinctively
important to this specific essay rather than generically frequent words
like "the" or "said".

Important nuance: TF-IDF is a COMPARATIVE measure — it needs a "corpus"
(a collection of documents) to compute the IDF part meaningfully. For a
single essay in isolation, we approximate this using scikit-learn's
built-in English stop-word list combined with unigram+bigram frequency,
which still surfaces the most distinctive terms reasonably well. Once
Module 8 (Essay Comparison) is built, we'll extend this to compute true
cross-essay TF-IDF, which is far more meaningful when comparing multiple
students' essays on the same prompt.
"""

from sklearn.feature_extraction.text import TfidfVectorizer


def extract_keywords(raw_text: str, top_n: int = 10) -> list[dict]:
    """
    Extract the top N distinctive terms (unigrams + bigrams) from the essay.
    Returns terms sorted by TF-IDF weight, descending.
    """
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=200,
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([raw_text])
    except ValueError:
        # Raised when the essay is too short / entirely stop words after
        # cleaning — return no keywords rather than crashing the pipeline.
        return []

    scores = tfidf_matrix.toarray()[0]
    terms = vectorizer.get_feature_names_out()

    ranked = sorted(zip(terms, scores), key=lambda pair: pair[1], reverse=True)
    top_terms = [
        {"term": term, "score": round(float(score), 4)}
        for term, score in ranked[:top_n]
        if score > 0
    ]
    return top_terms
