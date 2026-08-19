"""
Comprehensive Audit & Stress Testing Script for Gemini AI Essay Chatbot.
Executes 15+ real-world user scenarios, edge cases, anti-duplication checks, and formatting verifications.
"""

import sys
import os
import re

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.chat_service import ChatMentorService

DUMMY_CONTEXT = {
    "title": "Impact of Digital Media on Modern Education",
    "filename": "digital_media_education.txt",
    "word_count": 450,
    "overall_score": 83,
    "grammar_score": 85,
    "vocab_score": 80,
    "coherence_score": 84,
    "argument_score": 79,
    "readability_score": 86,
    "strengths": "Clear thesis and structured paragraph flow.",
    "weaknesses": "Vocabulary repetition in body paragraph 2.",
    "content_preview": "Digital media has fundamentally altered how students acquire knowledge...",
}

audit_results = []

def run_scenario(category: str, prompt: str, history=None):
    if history is None:
        history = []
    
    sanitized_hist = ChatMentorService.sanitize_history(history)
    raw_response = ChatMentorService._generate_grounded_gemini_fallback(prompt, DUMMY_CONTEXT, sanitized_hist)
    clean_response = ChatMentorService.prevent_repetition(raw_response, sanitized_hist)
    
    issues = []
    
    # 1. Hallucination check
    if "40% increase in productivity" in clean_response or "78% of students" in clean_response:
        issues.append("Found fake static hallucinated statistics")
        
    # 2. Tag format check
    if "[FULL_ESSAY:" in clean_response and "[/FULL_ESSAY]" not in clean_response:
        issues.append("Unclosed [FULL_ESSAY] tag")
    if "[SECTION:" in clean_response and "[/SECTION]" not in clean_response:
        issues.append("Unclosed [SECTION] tag")
        
    # 3. Topic extraction check for essay gen
    if category == "Essay Generation":
        if "[FULL_ESSAY:" not in clean_response:
            issues.append("Failed to output [FULL_ESSAY] block")
        if "Artificial Intelligence Ethics" in clean_response and "ethics" not in prompt.lower() and "artificial intelligence" not in prompt.lower():
            issues.append("Fallback to default topic despite topic in prompt")
            
    # 4. Section rewrite check
    if category == "Section Rewrite":
        if "[SECTION:" not in clean_response:
            issues.append("Failed to output [SECTION] block")
            
    # 5. Length & structure check
    if len(clean_response) < 50:
        issues.append("Response too short (< 50 chars)")
        
    status = "PASSED ✅" if not issues else f"FAILED ❌ ({', '.join(issues)})"
    
    audit_results.append({
        "category": category,
        "prompt": prompt,
        "status": status,
        "issues": issues,
        "response_preview": clean_response[:120].replace('\n', ' ') + "..."
    })

def main():
    print("=" * 80)
    print("🔍 RUNNING COMPREHENSIVE GEMINI AI CHATBOT AUDIT (15 SCENARIOS)")
    print("=" * 80)
    
    # Category 1: Essay Generation Prompts
    run_scenario("Essay Generation", "write a essay in the topic of books")
    run_scenario("Essay Generation", "please generate an essay about artificial intelligence in healthcare")
    run_scenario("Essay Generation", "draft a paper on climate change and renewable energy")
    run_scenario("Essay Generation", "write essay")
    run_scenario("Essay Generation", "create an essay regarding philosophy")
    
    # Category 2: Section Rewrites
    run_scenario("Section Rewrite", "rewrite introduction for my essay")
    run_scenario("Section Rewrite", "fix intro")
    run_scenario("Section Rewrite", "rewrite conclusion")

    # Category 3: Part-by-Part & Structural Analysis
    run_scenario("Part-by-Part Analysis", "give me part by part analysis")
    run_scenario("Part-by-Part Analysis", "break down my essay structure")
    run_scenario("Part-by-Part Analysis", "structural diagnostic")

    # Category 4: General Academic Q&A
    run_scenario("Academic Q&A", "how do I write a strong thesis statement?")
    run_scenario("Academic Q&A", "what is the difference between active and passive voice?")
    run_scenario("Academic Q&A", "how can I improve my essay vocabulary?")
    run_scenario("Academic Q&A", "can you give me feedback on my essay scores?")

    # Category 5: Anti-Duplication & Edge Cases
    repeat_hist = [
        {"role": "user", "content": "write a essay in the topic of books"},
        {"role": "assistant", "content": "I've written a complete, structured 5-paragraph academic essay draft..."}
    ]
    run_scenario("Anti-Duplication", "write a essay in the topic of books", repeat_hist)
    run_scenario("Edge Case", "write an essay on space exploration!@#$%^&*()")
    
    passed_count = sum(1 for r in audit_results if "PASSED" in r["status"])
    failed_count = len(audit_results) - passed_count
    
    print("\n" + "-" * 80)
    print("📊 AUDIT RESULTS SUMMARY")
    print("-" * 80)
    for idx, r in enumerate(audit_results, 1):
        print(f"Scenario {idx:02d} [{r['category']}]")
        print(f"  Prompt : \"{r['prompt']}\"")
        print(f"  Status : {r['status']}")
        print(f"  Preview: {r['response_preview']}")
        print("-" * 80)
        
    print(f"\nTOTAL SCENARIOS AUDITED: {len(audit_results)}")
    print(f"PASSED: {passed_count}")
    print(f"FAILED: {failed_count}")
    print("=" * 80)

if __name__ == "__main__":
    main()
