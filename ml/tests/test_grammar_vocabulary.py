"""
Tests for Module 2: grammar & vocabulary analysis.

Run with: pytest ml/tests/test_grammar_vocabulary.py -v
"""

from ml.nlp.feature_extractor import extract_features
from ml.nlp.grammar_analysis import analyze_passive_voice
from ml.nlp.preprocessing import process_text
from ml.nlp.spelling import analyze_spelling
from ml.nlp.transitions import analyze_transitions
from ml.nlp.vocabulary_analysis import analyze_repeated_words

PASSIVE_TEXT = "The report was written by the committee. The decision was made yesterday."
ACTIVE_TEXT = "The committee wrote the report. They made the decision yesterday."

REPETITIVE_TEXT = (
    "The project is important. This important project matters a lot. "
    "Everyone agrees the project is important for the important goals we have."
)

TRANSITION_TEXT = (
    "First, we gathered data. However, the results were unclear. "
    "Therefore, we ran additional tests. In conclusion, more research is needed."
)

MISSPELLED_TEXT = "This paragraph has som obvoius speling mistaks in it."


def test_passive_voice_detected():
    doc = process_text(PASSIVE_TEXT)
    result = analyze_passive_voice(doc)
    assert result["passive_sentence_count"] == 2
    assert result["passive_ratio_percent"] == 100.0


def test_active_voice_not_flagged():
    doc = process_text(ACTIVE_TEXT)
    result = analyze_passive_voice(doc)
    assert result["passive_sentence_count"] == 0


def test_repeated_words_flagged_with_synonyms():
    doc = process_text(REPETITIVE_TEXT)
    result = analyze_repeated_words(doc)
    words = {w["word"] for w in result["overused_words"]}
    assert "important" in words
    important_entry = next(w for w in result["overused_words"] if w["word"] == "important")
    assert important_entry["count"] >= 4
    assert len(important_entry["synonyms"]) > 0


def test_transitions_detected_across_categories():
    result = analyze_transitions(TRANSITION_TEXT, sentence_count=4)
    assert result["total_transitions_found"] >= 4
    assert result["category_breakdown"]["contrast"] >= 1
    assert result["category_breakdown"]["cause_effect"] >= 1
    assert result["category_breakdown"]["conclusion"] >= 1


def test_transitions_no_double_counting_overlapping_phrases():
    # "in conclusion" should match once as a phrase, not also separately
    # match "conclusion" as a stray word from some other category.
    result = analyze_transitions("In conclusion, the results were clear.", sentence_count=1)
    phrases = [p["phrase"] for p in result["phrases_found"]]
    assert phrases.count("in conclusion") == 1


def test_spelling_mistakes_detected():
    result = analyze_spelling(MISSPELLED_TEXT)
    misspelled = {w["word"].lower() for w in result["misspelled_words"]}
    # Note: "som" is deliberately excluded from this assertion — it's a
    # real dictionary word (a currency name), which demonstrates the
    # documented limitation that dictionary-based spellcheckers can't
    # catch typos that happen to form another valid word.
    assert "obvoius" in misspelled
    assert "speling" in misspelled
    assert "mistaks" in misspelled


def test_spelling_correct_text_flags_nothing():
    result = analyze_spelling("This sentence is spelled correctly.")
    assert result["misspelled_count"] == 0


def test_whitelisted_acronyms_not_flagged():
    result = analyze_spelling("The AI and NLP research was funded by NASA.")
    misspelled = {w["word"].lower() for w in result["misspelled_words"]}
    assert "ai" not in misspelled
    assert "nlp" not in misspelled
    assert "nasa" not in misspelled


def test_full_pipeline_includes_module2_sections():
    result = extract_features(PASSIVE_TEXT)
    for key in ("passive_voice", "repeated_words", "transitions", "spelling"):
        assert key in result
