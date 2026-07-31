"""
Passive voice detection.

Concept: this is done via DEPENDENCY PARSING, not keyword matching. spaCy
labels each token's grammatical role relative to its head word. A passive
construction has:
  - a subject tagged `nsubjpass` (passive nominal subject) — e.g. "report"
    in "The report was written" (the report RECEIVES the action, doesn't
    perform it)
  - an auxiliary tagged `auxpass` (passive auxiliary, e.g. "was"/"were"/"been")

This is more reliable than looking for "was"/"were" + past participle via
regex, which produces false positives (e.g. "The meeting was long" is NOT
passive — "long" is an adjective, not a past participle).

We report each passive sentence found, plus an overall passive voice ratio,
since occasional passive voice is fine in academic writing but essays
that are majority passive tend to read as vague or evasive.
"""

from spacy.tokens import Doc


def analyze_passive_voice(doc: Doc) -> dict:
    """
    Scan every sentence for passive voice constructions.

    Returns a list of flagged sentences plus the overall passive ratio.
    """
    flagged_sentences = []

    for sent in doc.sents:
        is_passive = any(token.dep_ in {"nsubjpass", "auxpass"} for token in sent)
        if is_passive:
            flagged_sentences.append(
                {
                    "sentence": sent.text.strip(),
                    "suggestion": _suggest_active_rewrite_hint(sent),
                }
            )

    total_sentences = max(len(list(doc.sents)), 1)
    passive_count = len(flagged_sentences)

    return {
        "passive_sentence_count": passive_count,
        "total_sentences": total_sentences,
        "passive_ratio_percent": round(100 * passive_count / total_sentences, 1),
        "flagged_sentences": flagged_sentences,
    }


def _suggest_active_rewrite_hint(sent) -> str:
    """
    Generate a lightweight, generic hint (not a full rewrite — that's the
    AI Writing Mentor's job in Module 11, which will use an LLM for actual
    rewriting). Here we just point out WHO is performing the action, if
    findable, to nudge the student toward an active-voice version.
    """
    agent = None
    for token in sent:
        # "by <agent>" phrases mark who performed the action, e.g.
        # "The ball was thrown by John" -> agent = "John"
        if token.dep_ == "agent":
            agent_phrase = [child.text for child in token.subtree if child.pos_ != "ADP"]
            if agent_phrase:
                agent = " ".join(agent_phrase)

    if agent:
        return f"Consider rewriting with '{agent}' as the subject performing the action."
    return "Consider identifying who/what performs the action and making it the subject."
