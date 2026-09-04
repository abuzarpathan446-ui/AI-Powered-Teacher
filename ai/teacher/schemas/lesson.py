"""Universal, domain-independent lesson-planning contracts."""
from typing import Any, List, Optional
import uuid

from pydantic import BaseModel, Field
from ai.teacher.schemas.enums import Difficulty, Language, StudentLevel


class LessonRequest(BaseModel):
    student_id: str
    topic: str
    student_level: StudentLevel = StudentLevel.BEGINNER
    language: Language = Language.ENGLISH
    time_budget_minutes: Optional[float] = Field(default=None, gt=0)
    learning_goal: Optional[str] = None
    current_mastery: Optional[float] = Field(default=None, ge=0, le=1)
    known_concepts: List[str] = Field(default_factory=list)
    weak_concepts: List[str] = Field(default_factory=list)
    learning_history: List[str] = Field(default_factory=list)
    rag_context: Optional[str] = None


class LessonSection(BaseModel):
    section_id: str = Field(default_factory=lambda: f"section_{uuid.uuid4().hex[:10]}")
    title: str = ""
    concept: str
    objectives: List[str] = Field(default_factory=list)
    order: int = 0
    sequence_order: Optional[int] = None
    difficulty: Difficulty = Difficulty.EASY
    estimated_minutes: float = Field(default=3.0, gt=0)
    estimated_duration: Optional[float] = None
    prerequisites: List[str] = Field(default_factory=list)
    key_points: List[str] = Field(default_factory=list)
    teaching_strategies: List[str] = Field(default_factory=list)
    assessment_required: bool = False

    def model_post_init(self, __context: Any) -> None:
        if not self.title:
            self.title = self.concept
        if self.sequence_order is None:
            self.sequence_order = self.order
        else:
            self.order = self.sequence_order
        if self.estimated_duration is None:
            self.estimated_duration = self.estimated_minutes
        else:
            self.estimated_minutes = self.estimated_duration


class LessonPlan(BaseModel):
    lesson_id: str = Field(default_factory=lambda: f"lesson_{uuid.uuid4().hex[:12]}")
    topic: str
    sections: List[LessonSection]
    total_estimated_minutes: float = Field(default=0.0)
    total_duration: Optional[float] = None
    student_level: StudentLevel = StudentLevel.BEGINNER
    language: Language = Language.ENGLISH
    learning_goal: Optional[str] = None
    title: str = ""
    description: str = ""
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    initial_difficulty: Difficulty = Difficulty.EASY
    assessment_points: List[str] = Field(default_factory=list)
    source_references: List[str] = Field(default_factory=list)
    planner_version: str = "1.0"
    metadata: dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.total_estimated_minutes:
            self.total_estimated_minutes = sum(s.estimated_minutes for s in self.sections)
        if self.total_duration is None:
            self.total_duration = self.total_estimated_minutes
