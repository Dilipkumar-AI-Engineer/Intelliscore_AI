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
    Starts at 100, subtracts points per issue found, clipped to [50, 98].
    """
    misspelled = features["spelling"]["misspelled_count"]
    passive_ratio = features["passive_voice"]["passive_ratio_percent"]

    score = 100 - (misspelled * 4) - (passive_ratio * 0.3)
    score = _clip(score, low=50.0, high=98.0)

    return {
        "score": round(score, 1),
        "explanation": (
            f"{misspelled} spelling issue(s) found; "
            f"{passive_ratio:.0f}% of sentences are passive voice."
        ),
    }


def compute_vocabulary_score(features: dict) -> dict:
    """
    Vocabulary score: rewards lexical diversity (Root TTR),
    penalizes word repetition. Clipped to [50, 98].
    """
    root_ttr = features["lexical_diversity"]["root_ttr"]
    overused_count = features["repeated_words"]["unique_overused_word_count"]

    diversity_component = _clip(root_ttr * 12, low=40.0, high=100.0)
    repetition_penalty = overused_count * 5

    score = _clip(diversity_component - repetition_penalty, low=50.0, high=98.0)

    return {
        "score": round(score, 1),
        "explanation": (
            f"Vocabulary richness score of {root_ttr:.1f} (Root TTR); "
            f"{overused_count} word(s) used repetitively."
        ),
    }


def compute_coherence_score(features: dict, semantic_coherence: dict | None = None) -> dict:
    """
    Coherence score: evaluates sentence flow, paragraph structure, and transition word density.
    Guarantees a baseline floor of 50.0 pts for non-empty text, up to 98.0 pts.
    """
    transitions_per_sentence = features["transitions"]["transitions_per_sentence"]
    avg_sentences_per_paragraph = features["basic_stats"]["avg_sentences_per_paragraph"]
    
    # Base coherence floor of 52 pts for structured sentences
    base_floor = 52.0
    transition_component = _clip(transitions_per_sentence * 75, low=0.0, high=35.0)
    paragraph_component = _clip(15 - abs(avg_sentences_per_paragraph - 4) * 3, low=0.0, high=15.0)
    
    raw_coherence = base_floor + transition_component + paragraph_component

    if semantic_coherence and semantic_coherence.get("local_coherence", {}).get("avg_local_coherence") is not None:
        avg_sim = semantic_coherence["local_coherence"]["avg_local_coherence"]
        semantic_component = _clip(avg_sim * 100, low=50.0, high=98.0)
        score = (raw_coherence * 0.4) + (semantic_component * 0.6)
        explanation = (
            f"Transition word usage and sentence-to-sentence semantic "
            f"similarity ({avg_sim:.2f}) both factored in."
        )
    else:
        score = raw_coherence
        explanation = (
            f"Based on paragraph flow and transition word density "
            f"({transitions_per_sentence:.2f} per sentence)."
        )

    return {"score": round(_clip(score, low=50.0, high=98.0), 1), "explanation": explanation}


def compute_argument_score(features: dict) -> dict:
    """
    Argument strength: combines named entity citations and paragraph development.
    Guarantees a baseline floor of 50.0 pts, clipped to [50, 98].
    """
    entity_count = len(features["named_entities"])
    avg_sentences_per_paragraph = features["basic_stats"]["avg_sentences_per_paragraph"]

    base_floor = 50.0
    entity_component = _clip(entity_count * 6, low=0.0, high=30.0)
    development_component = _clip(20.0 - abs(avg_sentences_per_paragraph - 4.5) * 4, low=0.0, high=20.0)

    score = base_floor + entity_component + development_component

    return {
        "score": round(_clip(score, low=50.0, high=98.0), 1),
        "explanation": (
            f"{entity_count} specific reference(s) (names, places, dates) found; "
            f"paragraphs average {avg_sentences_per_paragraph:.1f} sentences."
        ),
    }


def compute_readability_score(features: dict) -> dict:
    """
    Readability: maps Flesch Reading Ease to an essay quality evaluation scale (50-98 pts).
    Higher grade level / academic readability maps to optimal quality score range (75-95 pts).
    """
    flesch = features["readability"]["flesch_reading_ease"]
    label = features["readability"]["readability_label"]

    # Flesch 30-75 is standard academic writing range -> 75-92 pts
    if 30 <= flesch <= 75:
        score = 82.0 + (50 - abs(flesch - 52.5)) * 0.2
    elif flesch > 75: # Very easy text (e.g. 5th grade level)
        score = max(60.0, 90.0 - (flesch - 75) * 0.8)
    else: # Dense text (Flesch < 30)
        score = max(55.0, 75.0 + flesch * 0.4)

    return {
        "score": round(_clip(score, low=50.0, high=98.0), 1),
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
