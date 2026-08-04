"""
Sub-score computation: translates Module 1/2's raw NLP features into the
five labeled dimensions shown on the Essay Analysis UI (Grammar,
Vocabulary, Coherence, Argument Strength, Readability).

IMPORTANT -- read before trusting these numbers: these are RULE-BASED,
EXPLAINABLE decompositions of real features, not separately-trained ML
models. Each formula below is a transparent weighting the person reading
this code can inspect and adjust -- that's the point, for an "explainable
AI" project. They have NOT been validated against real human graders.
Only the Overall Score (ml/inference/predict_score.py) comes from the
XGBoost model, and that model is itself still trained on Module 3's
synthetic formula until real labeled data replaces it.

Each function returns {"score": 0-100, "explanation": "..."} so the UI
can show not just a number but WHY, per the project's explainability goal.
"""


def _clip(value: float, low: float = 0, high: float = 100) -> float:
    return max(low, min(high, value))


def compute_grammar_score(features: dict) -> dict:
    """
    Grammar score: penalizes spelling mistakes and excessive passive voice.
    Starts at 100, subtracts points per issue found.
    """
    misspelled = features["spelling"]["misspelled_count"]
    passive_ratio = features["passive_voice"]["passive_ratio_percent"]

    score = 100 - (misspelled * 4) - (passive_ratio * 0.3)
    score = _clip(score)

    return {
        "score": round(score, 1),
        "explanation": (
            f"{misspelled} spelling issue(s) found; "
            f"{passive_ratio:.0f}% of sentences are passive voice."
        ),
    }


def compute_vocabulary_score(features: dict) -> dict:
    """
    Vocabulary score: rewards lexical diversity (Root TTR from Module 1),
    penalizes word repetition.
    """
    root_ttr = features["lexical_diversity"]["root_ttr"]
    overused_count = features["repeated_words"]["unique_overused_word_count"]

    # Root TTR typically ranges ~2-8 for essay-length text; scale to 0-100.
    diversity_component = _clip(root_ttr * 12)
    repetition_penalty = overused_count * 5

    score = _clip(diversity_component - repetition_penalty)

    return {
        "score": round(score, 1),
        "explanation": (
            f"Vocabulary richness score of {root_ttr:.1f} (Root TTR); "
            f"{overused_count} word(s) used repetitively."
        ),
    }


def compute_coherence_score(features: dict, semantic_coherence: dict | None = None) -> dict:
    """
    Coherence score: primarily uses transition word density (always
    available, Module 2). If Module 4's semantic coherence analysis was
    also run (optional -- requires the embedding model), it's blended in
    for a stronger signal.
    """
    transitions_per_sentence = features["transitions"]["transitions_per_sentence"]
    transition_component = _clip(transitions_per_sentence * 125)

    if semantic_coherence and semantic_coherence.get("local_coherence", {}).get("avg_local_coherence") is not None:
        avg_sim = semantic_coherence["local_coherence"]["avg_local_coherence"]
        semantic_component = _clip(avg_sim * 100)
        score = (transition_component * 0.4) + (semantic_component * 0.6)
        explanation = (
            f"Transition word usage and sentence-to-sentence semantic "
            f"similarity ({avg_sim:.2f}) both factored in."
        )
    else:
        score = transition_component
        explanation = (
            f"Based on transition word density "
            f"({transitions_per_sentence:.2f} per sentence). "
            "Semantic coherence analysis (Module 4) not included in this run."
        )

    return {"score": round(_clip(score), 1), "explanation": explanation}


def compute_argument_score(features: dict) -> dict:
    """
    Argument strength: a WEAKER proxy than the other scores -- true
    argument evaluation needs semantic understanding of claims and
    evidence, which this rule-based layer cannot assess. This is a
    structural proxy only: essays with more named entities (concrete,
    specific references) and reasonably developed paragraphs tend to
    read as more substantiated than vague, short ones.
    """
    entity_count = len(features["named_entities"])
    avg_sentences_per_paragraph = features["basic_stats"]["avg_sentences_per_paragraph"]

    entity_component = _clip(entity_count * 8)
    # Ideal paragraph development is roughly 3-6 sentences; too few reads
    # as underdeveloped, too many can read as unfocused.
    development_component = _clip(100 - abs(avg_sentences_per_paragraph - 4.5) * 15)

    score = (entity_component * 0.5) + (development_component * 0.5)

    return {
        "score": round(_clip(score), 1),
        "explanation": (
            f"{entity_count} specific reference(s) (names, places, dates) found; "
            f"paragraphs average {avg_sentences_per_paragraph:.1f} sentences. "
            "Note: this is a structural proxy, not true argument evaluation."
        ),
    }


def compute_readability_score(features: dict) -> dict:
    """
    Readability: Flesch Reading Ease is already 0-100 (Module 1), used
    directly. Note this measures EASE of reading, not necessarily
    "good writing" -- a very simple essay scores high here while
    potentially being simplistic.
    """
    flesch = features["readability"]["flesch_reading_ease"]
    label = features["readability"]["readability_label"]

    return {
        "score": round(_clip(flesch), 1),
        "explanation": f"Flesch Reading Ease: {label} ({flesch:.0f}/100).",
    }


def compute_all_sub_scores(features: dict, semantic_coherence: dict | None = None) -> dict:
    """Compute all five sub-scores in one call -- the main entrypoint for this module."""
    return {
        "grammar": compute_grammar_score(features),
        "vocabulary": compute_vocabulary_score(features),
        "coherence": compute_coherence_score(features, semantic_coherence),
        "argument": compute_argument_score(features),
        "readability": compute_readability_score(features),
    }
