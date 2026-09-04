"""
Output contracts.

TeachingActionOutput  -> what the Teacher Brain hands to FastAPI/frontend/video layer.
AssessmentResult      -> the contract Person 6's Assessment module must produce;
                         send them this file so integration doesn't block on you.
"""
from typing import Optional

from pydantic import BaseModel, Field

from ai.teacher.schemas.enums import (
    AnswerCorrectness,
    TeachingAction,
    TeachingStrategy,
)


class TeachingActionOutput(BaseModel):
    session_id: str
    action: TeachingAction
    strategy: TeachingStrategy
    content: str = Field(..., description="Explanation/question/analogy text to show the student")
    visual_spec: Optional[str] = Field(
        default=None, description="Optional hint for the Video/Voice module (e.g. diagram type)"
    )
    concept: str
    difficulty: str
    is_final_action: bool = False


class AssessmentResult(BaseModel):
    """Produced by the Assessment module (Person 6), consumed by the Teacher Brain."""

    correctness: AnswerCorrectness
    score: float = Field(..., ge=0.0, le=1.0)
    misconception: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    raw_student_answer: str
