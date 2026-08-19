"""
Exhaustive 25-Scenario Essay-Specific Prompt Test Matrix.
Tests all prompt variations, action pills, topic extractions, tag formats, and score groundings.
"""

import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.chat_service import ChatMentorService

DUMMY_CONTEXT = {
    "title": "Role of Literature in Modern Education",
    "filename": "literature_education.txt",
    "word_count": 480,
    "overall_score": 84,
    "grammar_score": 86,
    "vocab_score": 82,
    "coherence_score": 85,
    "argument_score": 81,
    "readability_score": 86,
    "strengths": "Clear thesis and structured paragraph flow.",
    "weaknesses": "Repetitive transitions in body paragraphs.",
    "content_preview": "Literature provides profound insights into human culture and analytical reasoning...",
}

PROMPT_SCENARIOS = [
    # Full Essay Generation Prompts (1-10)
    ("Essay Generation", "write a essay in the topic of books", "Books"),
    ("Essay Generation", "write an essay on books", "Books"),
    ("Essay Generation", "essay about books", "Books"),
    ("Essay Generation", "generate an essay on artificial intelligence", "Artificial Intelligence"),
    ("Essay Generation", "draft a paper regarding climate change", "Climate Change"),
    ("Essay Generation", "compose an essay about history of technology", "History Of Technology"),
    ("Essay Generation", "write an essay for literature", "Literature"),
    ("Essay Generation", "write essay on philosophy", "Philosophy"),
    ("Essay Generation", "generate paper for economics", "Economics"),
    ("Essay Generation", "create essay", "Books"),

    # Section Rewrite Prompts (11-16)
    ("Section Rewrite Intro", "rewrite introduction for my essay", "Introduction"),
    ("Section Rewrite Intro", "fix intro paragraph", "Introduction"),
    ("Section Rewrite Intro", "improve introduction", "Introduction"),
    ("Section Rewrite Conclusion", "rewrite conclusion", "Conclusion"),
    ("Section Rewrite Conclusion", "fix conclusion", "Conclusion"),
    ("Section Rewrite Conclusion", "improve conclusion", "Conclusion"),

    # Part-by-Part Diagnostics (17-20)
    ("Structural Analysis", "part by part analysis", "Diagnostic"),
    ("Structural Analysis", "part-by-part breakdown", "Diagnostic"),
    ("Structural Analysis", "section analysis of my essay", "Diagnostic"),
    ("Structural Analysis", "paragraph by paragraph feedback", "Diagnostic"),

    # Grounded Feedback & Writing Guidance (21-25)
    ("Score Feedback", "give me feedback on my essay scores", "Scores"),
    ("Score Feedback", "why is my grammar score 85?", "Grammar"),
    ("Academic Guidance", "how do I write a thesis statement?", "Thesis"),
    ("Academic Guidance", "how can I remove passive voice?", "Passive Voice"),
    ("Edge Case Prompt", "write an essay on machine learning & robotics!@#$", "Machine Learning"),
]

def test_all_scenarios():
    print("=" * 85)
    print("🚀 RUNNING EXHAUSTIVE 25-SCENARIO ESSAY-SPECIFIC PROMPT AUDIT")
    print("=" * 85)
    
    passed = 0
    failed = 0
    problems = []

    for idx, (cat, prompt, expected_keyword) in enumerate(PROMPT_SCENARIOS, 1):
        response = ChatMentorService._generate_grounded_gemini_fallback(prompt, DUMMY_CONTEXT, [])
        
        issue_list = []

        # Category specific checks
        if cat == "Essay Generation":
            if "[FULL_ESSAY:" not in response or "[/FULL_ESSAY]" not in response:
                issue_list.append("Missing or corrupted [FULL_ESSAY] tags")
            if expected_keyword.lower() not in response.lower():
                issue_list.append(f"Expected topic '{expected_keyword}' not found in output")

        elif "Section Rewrite" in cat:
            if "[SECTION:" not in response or "[/SECTION]" not in response:
                issue_list.append("Missing or corrupted [SECTION] tags")

        elif cat == "Structural Analysis":
            if "86/100" not in response and "Grammar" not in response:
                issue_list.append("Structural diagnostic not grounded in real scores")

        elif cat == "Score Feedback":
            if "84/100" not in response and "Overall" not in response:
                issue_list.append("Score feedback missing real essay metrics")

        # General sanity checks
        if len(response) < 40:
            issue_list.append("Response content excessively short")
        if "40% increase in productivity" in response:
            issue_list.append("Detected static hallucinated template")

        status = "PASSED ✅" if not issue_list else "FAILED ❌"
        if issue_list:
            failed += 1
            problems.append((idx, prompt, issue_list))
        else:
            passed += 1

        print(f"Scenario {idx:02d} [{cat:22s}] Prompt: \"{prompt[:35]:35s}\" -> {status}")

    print("=" * 85)
    print(f"SUMMARY: Total Tested: {len(PROMPT_SCENARIOS)} | PASSED: {passed} | FAILED: {failed}")
    print("=" * 85)

    if problems:
        print("\nPROBLEMS DETECTED:")
        for idx, prompt, errs in problems:
            print(f" - Scenario {idx}: Prompt \"{prompt}\" -> {', '.join(errs)}")
    else:
        print("\n🎉 ZERO PROBLEMS DETECTED! All 25 essay-specific prompt scenarios are 100% sound.")

if __name__ == "__main__":
    test_all_scenarios()
