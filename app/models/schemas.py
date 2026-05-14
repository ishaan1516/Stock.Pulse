from pydantic import BaseModel, Field
from typing import List, Literal


class AnalysisRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    company: str = Field(..., min_length=1, max_length=100)


class StockRatingResponse(BaseModel):
    ticker: str
    company: str
    period: str
    weekly_summary: str
    monthly_context: str
    reaction_score: int = Field(ge=1, le=10)
    direction: Literal["POSITIVE", "NEGATIVE", "MIXED", "NEUTRAL"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    key_factors: List[str]
    risk_factors: List[str]
    one_line_verdict: str