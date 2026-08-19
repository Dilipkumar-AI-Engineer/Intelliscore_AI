"""
Tests for Essay-Specific Gemini AI Chatbot Mentor Service & API Routes.
Verifies Anti-Duplication, Anti-Repetition, Grounded Non-Hallucination, and Structured Actions.
"""

import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.chat_service import ChatMentorService


def test_history_sanitization_and_deduplication():
    """Verify that sanitize_history removes consecutive identical turns."""
    raw_history = [
        {"role": "user", "content": "Hello mentor"},
        {"role": "user", "content": "Hello mentor"},  # duplicate turn
        {"role": "assistant", "content": "Hello! How can I help with your essay today?"},
        {"role": "assistant", "content": "Hello! How can I help with your essay today?"},  # duplicate turn
        {"role": "user", "content": "Analyze my intro paragraph"},
    ]

    cleaned = ChatMentorService.sanitize_history(raw_history)
    assert len(cleaned) == 3, f"Expected 3 turns, got {len(cleaned)}"
    assert cleaned[0]["content"] == "Hello mentor"
    assert cleaned[1]["content"] == "Hello! How can I help with your essay today?"
    assert cleaned[2]["content"] == "Analyze my intro paragraph"
    print("✅ test_history_sanitization_and_deduplication passed!")


def test_prevent_repetition():
    """Verify that prevent_repetition removes repeated internal paragraphs and flags identical replies."""
    history = [
        {"role": "user", "content": "Give me introduction feedback"},
        {"role": "assistant", "content": "Here is a refined introduction for your essay draft."},
    ]

    # Duplicate reply attempt
    duplicate_reply = "Here is a refined introduction for your essay draft."
    result = ChatMentorService.prevent_repetition(duplicate_reply, history)
    assert "fresh Gemini perspective" in result or result != duplicate_reply

    # Repetitive internal paragraphs
    internal_rep = "Paragraph 1: Good thesis.\n\nParagraph 1: Good thesis.\n\nParagraph 2: Clear evidence."
    cleaned_internal = ChatMentorService.prevent_repetition(internal_rep, [])
    assert cleaned_internal.count("Paragraph 1: Good thesis.") == 1
    print("✅ test_prevent_repetition passed!")


def test_full_essay_generation_formatting():
    """Verify that essay generation includes correct [FULL_ESSAY:Title] structured tags."""
    dummy_context = {
        "title": "Test Essay",
        "filename": "test.txt",
        "word_count": 250,
        "overall_score": 80,
        "grammar_score": 82,
        "vocab_score": 78,
        "coherence_score": 85,
        "argument_score": 80,
        "readability_score": 84,
        "strengths": "Clear structure",
        "weaknesses": "Transitions",
        "content_preview": "Sample essay preview...",
    }

    reply = ChatMentorService._generate_grounded_gemini_fallback(
        message="Write an essay on Climate Change Solutions",
        ctx=dummy_context,
        history=[]
    )

    assert "[FULL_ESSAY:" in reply
    assert "[/FULL_ESSAY]" in reply
    assert "Climate Change" in reply
    print("✅ test_full_essay_generation_formatting passed!")


def test_section_rewrite_formatting():
    """Verify section rewrite returns [SECTION:Introduction] tags."""
    dummy_context = {
        "title": "Test Essay",
        "filename": "test.txt",
        "word_count": 250,
        "overall_score": 80,
        "grammar_score": 82,
        "vocab_score": 78,
        "coherence_score": 85,
        "argument_score": 80,
        "readability_score": 84,
        "strengths": "Clear structure",
        "weaknesses": "Transitions",
        "content_preview": "Sample essay preview...",
    }

    reply = ChatMentorService._generate_grounded_gemini_fallback(
        message="Rewrite introduction for my essay",
        ctx=dummy_context,
        history=[]
    )

    assert "[SECTION:Introduction]" in reply
    assert "[/SECTION]" in reply
    print("✅ test_section_rewrite_formatting passed!")


def test_no_hallucinated_statistics():
    """Verify that fallback responses do not invent fake studies like 40% productivity increase."""
    dummy_context = {
        "title": "Test Essay",
        "filename": "test.txt",
        "word_count": 250,
        "overall_score": 80,
        "grammar_score": 82,
        "vocab_score": 78,
        "coherence_score": 85,
        "argument_score": 80,
        "readability_score": 84,
        "strengths": "Clear structure",
        "weaknesses": "Transitions",
        "content_preview": "Sample essay preview...",
    }

    reply = ChatMentorService._generate_grounded_gemini_fallback(
        message="Give me part by part breakdown",
        ctx=dummy_context,
        history=[]
    )

    # Ensure fake stat isn't present
    assert "40% increase in productivity" not in reply
    # Ensure real metrics are present
    assert "82/100" in reply or "Grammar" in reply
    print("✅ test_no_hallucinated_statistics passed!")


def test_user_books_prompt_essay_generation():
    """Verify that user prompt 'write a essay in the topic of books' extracts 'Books' and generates full essay."""
    dummy_context = {
        "title": "Test Essay",
        "filename": "test.txt",
        "word_count": 250,
        "overall_score": 80,
        "grammar_score": 82,
        "vocab_score": 78,
        "coherence_score": 85,
        "argument_score": 80,
        "readability_score": 84,
        "strengths": "Clear structure",
        "weaknesses": "Transitions",
        "content_preview": "Sample essay preview...",
    }

    reply = ChatMentorService._generate_grounded_gemini_fallback(
        message="write a essay in the topic of books",
        ctx=dummy_context,
        history=[]
    )

    assert "[FULL_ESSAY:Academic Essay: Books]" in reply
    assert "Books" in reply
    assert "1. Introduction & Thesis" in reply
    print("✅ test_user_books_prompt_essay_generation passed!")


if __name__ == "__main__":
    print("🚀 Running Essay-Specific Gemini AI Chatbot Verification Suite...")
    test_history_sanitization_and_deduplication()
    test_prevent_repetition()
    test_full_essay_generation_formatting()
    test_section_rewrite_formatting()
    test_no_hallucinated_statistics()
    test_user_books_prompt_essay_generation()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 100% Verified.")

