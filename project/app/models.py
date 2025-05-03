from pydantic import BaseModel

class AnalysisResult(BaseModel):
    speed_wpm: float
    filler_words: int
    dominant_emotion: str
    recommendations: list[str]
