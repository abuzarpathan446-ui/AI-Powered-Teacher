"""
TeacherState — the object every module in the Teacher Brain reads and writes.

Deliberately holds NO decision logic. It is data plus safe mutation helpers.
The Rule Layer / Adaptation Engine decide *what* to change; this class only
guarantees changes are applied consistently and validated.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from ai.teacher.schemas.enums import (
    Difficulty,
    Language,
    StudentLevel,
    TeachingAction,
    TeachingStrategy,
)

MAX_RECENT_ACTIONS = 10


class TeacherState(BaseModel):
    session_id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:12]}")
    student_id: str

    current_concept: str
    concept_sequence_index: int = 0

    mastery_score: float = Field(default=0.0)
    difficulty: Difficulty = Difficulty.EASY
    attempt_count: int = 0

    misconception: Optional[str] = None
    teaching_strategy: TeachingStrategy = TeachingStrategy.DIRECT_EXPLANATION

    language: Language = Language.ENGLISH
    student_level: StudentLevel = StudentLevel.BEGINNER

    recent_actions: List[TeachingAction] = Field(default_factory=list)
    last_action: Optional[TeachingAction] = None
    next_action: Optional[TeachingAction] = None

    time_remaining_minutes: Optional[float] = None
    lesson_progress: float = Field(default=0.0)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1  # bumped on every mutation — used for optimistic concurrency

    @field_validator("mastery_score", "lesson_progress")
    @classmethod
    def _clamp_unit_interval(cls, v: float) -> float:
        return max(0.0, min(1.0, v))

    def record_action(self, action: TeachingAction) -> None:
        """Append an action to history, bump version, refresh timestamp."""
        self.recent_actions.append(action)
        if len(self.recent_actions) > MAX_RECENT_ACTIONS:
            self.recent_actions = self.recent_actions[-MAX_RECENT_ACTIONS:]
        self.last_action = action
        self._touch()

    def apply_mastery_delta(self, delta: float) -> None:
        self.mastery_score = max(0.0, min(1.0, self.mastery_score + delta))
        self._touch()

    def increment_attempt(self) -> None:
        self.attempt_count += 1
        self._touch()

    def reset_attempts(self) -> None:
        self.attempt_count = 0
        self._touch()

    def set_misconception(self, misconception: Optional[str]) -> None:
        self.misconception = misconception
        self._touch()

    def advance_concept(self, new_concept: str) -> None:
        self.current_concept = new_concept
        self.concept_sequence_index += 1
        self.attempt_count = 0
        self.misconception = None
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1
