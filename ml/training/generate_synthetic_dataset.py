"""
Synthetic training data generator.

IMPORTANT — read this before trusting any model trained on this data:

This does NOT generate real essays or real human-assigned scores. It
generates random FEATURE VECTORS directly (skipping text entirely) and
computes a target score from a hand-written formula that mimics what a
human grader plausibly cares about (rewards vocabulary richness and
transition usage; penalizes passive voice, spelling errors, and overly
short/long sentences).

Purpose: this lets us build, test, and debug the entire training
pipeline (train/test split, XGBoost fitting, evaluation metrics, model
persistence) TODAY, without waiting on a real labeled essay dataset.

Before this project can make genuinely trustworthy predictions, you must
replace this with a real dataset — e.g. ASAP-AES from Kaggle
(https://www.kaggle.com/c/asap-aes/data), which provides real student
essays with real human-assigned scores. The training script
(train_model.py) is written to consume a CSV of [essay_text, score] --
once you have real essays, extract_features()/vectorize_features() from
Module 1-3 will convert them the same way; nothing else changes.
"""

import random

import numpy as np
import pandas as pd

from ml.features.vectorizer import FEATURE_NAMES

random.seed(42)
np.random.seed(42)


def _generate_one_row() -> dict:
    """
    Generate one plausible (but synthetic) feature vector + target score.
    Ranges are chosen to roughly resemble real essay statistics.
    """
    word_count = random.randint(150, 600)
    sentence_count = max(int(word_count / random.uniform(10, 25)), 1)
    paragraph_count = max(int(sentence_count / random.uniform(3, 6)), 1)

    row = {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "avg_words_per_sentence": round(word_count / sentence_count, 2),
        "avg_sentences_per_paragraph": round(sentence_count / paragraph_count, 2),
        "flesch_reading_ease": round(random.uniform(20, 90), 2),
        "flesch_kincaid_grade": round(random.uniform(4, 16), 2),
        "pos_pct_nouns": round(random.uniform(15, 35), 1),
        "pos_pct_verbs": round(random.uniform(8, 20), 1),
        "pos_pct_adjectives": round(random.uniform(3, 15), 1),
        "pos_pct_adverbs": round(random.uniform(1, 8), 1),
        "pos_pct_pronouns": round(random.uniform(1, 10), 1),
        "named_entity_count": random.randint(0, 10),
        "unique_words": int(word_count * random.uniform(0.4, 0.75)),
        "root_ttr": round(random.uniform(2.5, 7.0), 2),
        "passive_ratio_percent": round(random.uniform(0, 60), 1),
        "unique_overused_word_count": random.randint(0, 8),
        "transitions_per_sentence": round(random.uniform(0, 0.8), 2),
        "misspelled_count": random.randint(0, 10),
    }

    # Hand-written scoring formula (0-100 scale). This encodes assumptions
    # about what "good writing" looks like -- transparent and adjustable,
    # unlike a black-box label. Replace with real human scores when
    # real data is available.
    score = 50.0
    score += (row["root_ttr"] - 4.5) * 4          # richer vocabulary -> higher
    score += row["transitions_per_sentence"] * 15  # more transitions -> higher
    score -= row["passive_ratio_percent"] * 0.25   # more passive voice -> lower
    score -= row["misspelled_count"] * 2.5         # more typos -> lower
    score -= row["unique_overused_word_count"] * 1.5  # more repetition -> lower
    # Penalize essays that are too short/simple OR extremely long-winded.
    if word_count < 250:
        score -= (250 - word_count) * 0.05
    if word_count > 500:
        score -= (word_count - 500) * 0.03
    # Small random noise to mimic real-world grading inconsistency.
    score += np.random.normal(0, 4)

    row["score"] = round(float(np.clip(score, 0, 100)), 1)
    return row


def generate_synthetic_dataset(n_samples: int = 500) -> pd.DataFrame:
    """Generate a synthetic labeled dataset as a pandas DataFrame."""
    rows = [_generate_one_row() for _ in range(n_samples)]
    df = pd.DataFrame(rows)
    # Column order must match FEATURE_NAMES + score, for clarity/consistency.
    return df[FEATURE_NAMES + ["score"]]


if __name__ == "__main__":
    import pathlib

    output_path = pathlib.Path(__file__).resolve().parents[2] / "data" / "processed" / "synthetic_training_data.csv"
    df = generate_synthetic_dataset(n_samples=500)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} synthetic rows -> {output_path}")
