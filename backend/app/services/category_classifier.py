"""
Category Classifier Service.
Uses weighted term frequency & keyword density analysis over essay title and body content
to classify essays into standardized academic/thematic categories.
"""

import re
from typing import Dict, List

# Standardized Categories
CAT_TECH = "Technology & AI"
CAT_CLIMATE = "Climate & Environment"
CAT_SCIENCE = "Academic & Science"
CAT_LITERATURE = "Literature & Arts"
CAT_BUSINESS = "Business & Economics"
CAT_SOCIAL = "Social & Political Science"
CAT_EDUCATION = "Education & Learning"
CAT_GENERAL = "General Essay"

ALL_CATEGORIES = [
    CAT_TECH,
    CAT_CLIMATE,
    CAT_SCIENCE,
    CAT_LITERATURE,
    CAT_BUSINESS,
    CAT_SOCIAL,
    CAT_EDUCATION,
    CAT_GENERAL,
]

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    CAT_TECH: [
        "ai", "artificial intelligence", "machine learning", "deep learning", "neural",
        "algorithm", "computer", "software", "digital", "cyber", "internet", "automation",
        "robotics", "data science", "tech", "technology", "cloud", "programming", "code",
        "llm", "chatgpt", "generative", "model", "virtual", "metaverse", "network", "semiconductor",
        "computing", "hardware", "database", "cybersecurity", "blockchain"
    ],
    CAT_CLIMATE: [
        "climate", "environment", "environmental", "global warming", "carbon", "emissions",
        "renewable", "solar", "wind", "ecology", "ecological", "sustainability", "sustainable",
        "pollution", "ocean", "atmosphere", "greenhouse", "conservation", "biodiversity",
        "planet", "deforestation", "fossil fuel", "recycling", "ecosystem", "glacier"
    ],
    CAT_SCIENCE: [
        "science", "scientific", "biology", "biological", "physics", "chemistry", "chemical",
        "medicine", "medical", "gene", "genetics", "dna", "experiment", "experimental",
        "research", "empirical", "hypothesis", "organism", "laboratory", "disease", "vaccine",
        "cell", "molecular", "anatomy", "neuroscience", "quantum", "astronomy", "pharmacology"
    ],
    CAT_LITERATURE: [
        "literature", "literary", "poetry", "poem", "novel", "fiction", "author", "writer",
        "drama", "theatre", "theater", "shakespeare", "philosophy", "philosophical", "ethics",
        "ethical", "art", "artistic", "painting", "sculpture", "history", "historical",
        "culture", "cultural", "myth", "mythology", "narrative", "prose", "aesthetic", "metaphor"
    ],
    CAT_BUSINESS: [
        "business", "economy", "economic", "economics", "market", "finance", "financial",
        "investment", "capital", "trade", "industry", "industrial", "corporate", "corporation",
        "commerce", "inflation", "stock", "revenue", "profit", "management", "entrepreneurship",
        "supply chain", "consumer", "gdp", "banking", "marketing", "workforce"
    ],
    CAT_SOCIAL: [
        "society", "social", "politics", "political", "government", "democracy", "democratic",
        "law", "legal", "justice", "rights", "policy", "election", "citizenship", "human rights",
        "sociology", "geopolitics", "constitution", "public policy", "freedom", "liberty",
        "sovereignty", "discrimination", "equality", "civilian", "nation"
    ],
    CAT_EDUCATION: [
        "education", "educational", "school", "university", "college", "teaching", "teacher",
        "student", "students", "learning", "pedagogy", "curriculum", "academic", "classroom",
        "literacy", "tuition", "pedagogical", "homework", "campus", "scholarship"
    ]
}


def classify_essay_category(title: str = "", raw_text: str = "") -> str:
    """
    Analyzes title and raw_text using weighted keyword frequency scores.
    Title words carry 3x weight compared to body text words.
    Returns the highest scoring category, or 'General Essay' if scores are below threshold.
    """
    clean_title = (title or "").lower()
    clean_text = (raw_text or "").lower()

    # Pre-calculate category scores
    scores: Dict[str, float] = {cat: 0.0 for cat in CATEGORY_KEYWORDS}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            # Word boundary regex for matching whole words / key phrases
            pattern = rf"\b{re.escape(kw)}\b"
            
            # Title matches carry 3.0 weight per occurrence
            title_matches = len(re.findall(pattern, clean_title))
            scores[cat] += title_matches * 3.0

            # Body text matches carry 1.0 weight per occurrence
            text_matches = len(re.findall(pattern, clean_text))
            scores[cat] += text_matches * 1.0

    # Find category with maximum score
    max_cat, max_score = max(scores.items(), key=lambda x: x[1])

    # Minimum threshold to assign a specific topic category
    if max_score >= 1.5:
        return max_cat

    return CAT_GENERAL
