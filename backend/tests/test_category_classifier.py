"""
Unit tests for Category Classifier service.
Verifies accurate topic classification across multiple academic and domain topics.
"""

import sys
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services.category_classifier import (
    classify_essay_category,
    CAT_TECH,
    CAT_CLIMATE,
    CAT_SCIENCE,
    CAT_LITERATURE,
    CAT_BUSINESS,
    CAT_SOCIAL,
    CAT_EDUCATION,
    CAT_GENERAL,
)

def test_category_classification():
    test_cases = [
        (
            "The Future of Artificial Intelligence",
            "Machine learning algorithms and neural networks are transforming deep learning software systems in modern technology.",
            CAT_TECH
        ),
        (
            "Global Warming and Climate Change",
            "Carbon emissions, renewable solar power, and ecosystem sustainability are essential to combat rising environmental pollution.",
            CAT_CLIMATE
        ),
        (
            "Advances in Genetic Engineering",
            "DNA sequencing, molecular biology experiments, and scientific hypothesis testing have accelerated medical research and vaccine development.",
            CAT_SCIENCE
        ),
        (
            "Shakespeare and Elizabethan Literature",
            "An analysis of poetic metaphors, narrative prose, and theatrical drama in classic historical literature and artistic culture.",
            CAT_LITERATURE
        ),
        (
            "The Global Market and Inflation Trends",
            "Corporate finance, capital investments, stock market trade, and consumer economics shape supply chain profit margins.",
            CAT_BUSINESS
        ),
        (
            "Democracy and Public Policy",
            "Elections, constitutional rights, government legislation, and social justice form the core principles of political science and civil law.",
            CAT_SOCIAL
        ),
        (
            "Transforming Higher Education Pedagogy",
            "School university curriculum, classroom student engagement, and literacy teaching methodologies enhance academic learning.",
            CAT_EDUCATION
        ),
        (
            "My Thoughts",
            "A short personal reflection on daily routine without specific academic domain keywords.",
            CAT_GENERAL
        )
    ]

    passed = 0
    for title, body, expected in test_cases:
        result = classify_essay_category(title, body)
        assert result == expected, f"Failed for '{title}': Expected '{expected}', got '{result}'"
        print(f"[PASS] '{title}' -> '{result}'")
        passed += 1

    print(f"\nAll {passed}/{len(test_cases)} category classification tests passed!")

if __name__ == "__main__":
    test_category_classification()
