"""
Vocabulary analysis: repeated word detection + synonym suggestions.

Concept: a word is "overused" if it appears far more often than natural
variation would predict for an essay of this length. We use a simple,
explainable threshold rather than a statistical model — a word occurring
5+ times in a short essay is a real signal a human reader would also
notice, and simple thresholds are easy to justify to a student ("you used
'important' 6 times") vs. an opaque statistical score.

For each overused word, we suggest synonyms via WordNet (a lexical
database bundled with NLTK) — this gives the student concrete, actionable
alternatives rather than just "vary your vocabulary."
"""

from collections import Counter

from nltk.corpus import wordnet
from spacy.tokens import Doc

# Below this count, repetition is normal and not worth flagging.
MIN_REPETITION_THRESHOLD = 4

# Cap on how many synonym suggestions to show per word — avoids overwhelming
# the student with an exhaustive WordNet dump.
MAX_SYNONYMS_PER_WORD = 5


def analyze_repeated_words(doc: Doc) -> dict:
    """
    Find content words (excluding stop words/punctuation) that appear at
    or above MIN_REPETITION_THRESHOLD times, with synonym suggestions.
    """
    word_counter = Counter()
    # Track original casing/lemma for display and synonym lookup.
    lemma_to_display = {}

    for token in doc:
        if token.is_stop or token.is_punct or token.is_space:
            continue
        if not token.is_alpha:
            continue
        lemma = token.lemma_.lower()
        word_counter[lemma] += 1
        lemma_to_display.setdefault(lemma, token.text.lower())

    overused = []
    for lemma, count in word_counter.most_common():
        if count < MIN_REPETITION_THRESHOLD:
            continue
        overused.append(
            {
                "word": lemma_to_display[lemma],
                "count": count,
                "synonyms": _get_synonyms(lemma),
            }
        )

    return {"overused_words": overused, "unique_overused_word_count": len(overused)}


def _get_synonyms(word: str) -> list[str]:
    """
    Look up synonyms via WordNet. We only keep single-word synonyms
    (WordNet includes multi-word phrases too) and exclude the word itself,
    since a lemma can appear in its own synonym set.
    """
    synonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            candidate = lemma.name().replace("_", " ")
            if candidate.lower() != word and " " not in candidate:
                synonyms.add(candidate)
        if len(synonyms) >= MAX_SYNONYMS_PER_WORD:
            break

    return sorted(synonyms)[:MAX_SYNONYMS_PER_WORD]
