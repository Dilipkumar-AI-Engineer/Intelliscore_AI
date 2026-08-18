from datetime import datetime
from pydantic import BaseModel


class EssayResponse(BaseModel):
    id: int
    title: str
    original_filename: str
    file_type: str
    word_count: int
    category: str = "General Essay"
    created_at: datetime
    overall_score: float | None = None
    grammar_score: float | None = None
    vocabulary_score: float | None = None
    coherence_score: float | None = None
    argument_score: float | None = None
    readability_score: float | None = None
    analyzed_at: datetime | None = None

    class Config:
        from_attributes = True


class EssayDetailResponse(EssayResponse):
    """Includes the full extracted text -- used for the single-essay view."""
    raw_text: str


class EssayUpdateRequest(BaseModel):
    raw_text: str
    title: str | None = None


class SubScoreDetail(BaseModel):
    score: float
    explanation: str


class GrammarErrorSchema(BaseModel):
    id: int
    type: str
    severity: str  # 'Major' | 'Minor' | 'Style'
    paragraph: str
    original: str
    suggestion: str
    explanation: str


class SuggestionSchema(BaseModel):
    id: int
    category: str
    impact: str  # 'High' | 'Medium' | 'Low'
    title: str
    description: str


class StylometricMetricsSchema(BaseModel):
    lexical_diversity: str
    readability_grade: str
    avg_sentence_length: str
    passive_voice_ratio: str


class StructureSectionSchema(BaseModel):
    section_type: str  # Title, Introduction, Argument, Counterargument, Conclusion
    title: str
    content_snippet: str
    confidence: int  # 0-100


class StructureDetectionResponse(BaseModel):
    sections: list[StructureSectionSchema]
    overall_confidence: int


class OrganizeEssayRequest(BaseModel):
    raw_text: str


class OrganizeEssayResponse(BaseModel):
    original_text: str
    organized_text: str
    sections: list[StructureSectionSchema]
    changes_summary: list[str]


class PromptAssistRequest(BaseModel):
    prompt: str
    essay_text: str | None = None


class PromptAssistResponse(BaseModel):
    reply: str
    suggested_structure: list[str] | None = None
    model: str


class TextPasteUploadRequest(BaseModel):
    title: str | None = None
    text: str


class AIDetectionEstimateSchema(BaseModel):
    estimated_probability: float  # 0-100
    confidence: str
    classification: str
    perplexity_variance: str
    burstiness_index: str
    disclaimer: str = "This is an estimate based on stylometric variance and should not be treated as definitive evidence."


class SimilarityMatchSchema(BaseModel):
    compared_essay_id: int | str
    compared_title: str
    similarity_score: float
    matched_passages: list[str]


class SimilarityResultSchema(BaseModel):
    overall_similarity: float
    matches: list[SimilarityMatchSchema]
    academic_sources_pct: float
    web_sources_pct: float
    risk_level: str


class EssayAnalysisResponse(BaseModel):
    """Full standardized analysis result for frontend consumption."""
    essay_id: int
    title: str
    filename: str
    word_count: int
    category: str = "General Essay"
    overall_score: float
    grammar_score: float | None = None
    vocabulary_score: float | None = None
    coherence_score: float | None = None
    argument_score: float | None = None
    readability_score: float | None = None
    sub_scores: dict[str, SubScoreDetail]
    features: dict
    metrics: StylometricMetricsSchema
    strengths: list[str]
    weaknesses: list[str]
    grammar_errors: list[GrammarErrorSchema]
    suggestions: list[SuggestionSchema]
    ai_detection_estimate: AIDetectionEstimateSchema
    similarity_result: SimilarityResultSchema
    
class EssayCompareRequest(BaseModel):
    essay_ids: list[int]


class EssayCompareRanking(BaseModel):
    rank: int
    essay_id: int
    title: str
    overall_score: float
    grammar_score: float
    vocabulary_score: float
    coherence_score: float
    argument_score: float
    readability_score: float


class EssayCompareResponse(BaseModel):
    rankings: list[EssayCompareRanking]
    winner_essay_id: int
    winner_title: str
    insights: list[str]


