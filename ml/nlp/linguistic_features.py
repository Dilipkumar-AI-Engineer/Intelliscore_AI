"""
Linguistic feature extraction: part-of-speech distribution, named entity
recognition, and lexical diversity.

Concept notes:
- POS distribution tells us the essay's grammatical "shape" — e.g. an
  essay overloaded with adjectives and short on verbs often reads as
  weaker argumentative writing than one with balanced noun/verb usage.
- Lexical diversity (Type-Token Ratio) measures vocabulary richness:
  ratio of UNIQUE words to TOTAL words. A student repeating the same 20
  words scores low; varied vocabulary scores high. Raw TTR is biased by
  text length though (longer texts naturally reuse words more) — we use
  the commonly cited "Root TTR" (Guiraud's Index) which corrects for this,
  so essays of different lengths can be fairly compared.
"""

from collections import Counter

from spacy.tokens import Doc

# Human-readable labels for spaCy's universal POS tags.
POS_LABELS = {
    "NOUN": "Nouns",
    "VERB": "Verbs",
    "ADJ": "Adjectives",
    "ADV": "Adverbs",
    "PRON": "Pronouns",
    "ADP": "Prepositions",
    "CONJ": "Conjunctions",
    "CCONJ": "Conjunctions",
    "SCONJ": "Conjunctions",
    "DET": "Determiners",
    "NUM": "Numerals",
    "INTJ": "Interjections",
}


def compute_pos_distribution(doc: Doc) -> dict:
    """Count how many tokens fall into each part-of-speech category."""
    counts = Counter()
    total = 0
    for token in doc:
        if token.is_punct or token.is_space:
            continue
        label = POS_LABELS.get(token.pos_, token.pos_)
        counts[label] += 1
        total += 1

    if total == 0:
        return {"distribution": {}, "total_tagged_tokens": 0}

    distribution = {
        label: {"count": count, "percentage": round(100 * count / total, 1)}
        for label, count in counts.most_common()
    }
    return {"distribution": distribution, "total_tagged_tokens": total}


def compute_named_entities(doc: Doc) -> list[dict]:
    """
    Extract named entities (people, organizations, locations, dates, etc.).
    Used both for display (highlighting in the essay preview) and as a
    signal of concrete, specific writing vs. vague generalization.
    """
    return [
        {"text": ent.text, "label": ent.label_, "explanation": _spacy_label_meaning(ent.label_)}
        for ent in doc.ents
    ]


def _spacy_label_meaning(label: str) -> str:
    """Human-readable descriptions for spaCy's entity labels, for UI tooltips."""
    meanings = {
        "PERSON": "Person",
        "ORG": "Organization",
        "GPE": "Country/City/State",
        "LOC": "Location",
        "DATE": "Date",
        "TIME": "Time",
        "MONEY": "Monetary value",
        "PERCENT": "Percentage",
        "CARDINAL": "Number",
        "ORDINAL": "Ordinal (e.g. 'first')",
        "NORP": "Nationality/Group",
        "EVENT": "Event",
        "WORK_OF_ART": "Title of work",
    }
    return meanings.get(label, label)


def compute_lexical_diversity(doc: Doc) -> dict:
    """
    Root TTR (Guiraud's Index) = unique_words / sqrt(total_words).
    Higher = richer vocabulary relative to essay length.
    """
    words = [
        token.text.lower()
        for token in doc
        if not token.is_punct and not token.is_space and not token.is_stop
    ]
    total_words = len(words)
    unique_words = len(set(words))

    if total_words == 0:
        return {"unique_words": 0, "total_content_words": 0, "root_ttr": 0.0}

    root_ttr = round(unique_words / (total_words ** 0.5), 2)

    return {
        "unique_words": unique_words,
        "total_content_words": total_words,
        "root_ttr": root_ttr,
    }
