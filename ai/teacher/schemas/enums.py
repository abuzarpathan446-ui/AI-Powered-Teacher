"""
Fixed vocabulary for the AI Teacher Brain.

Anything outside these enums gets rejected by Pydantic at the boundary,
instead of silently corrupting the Teacher State or downstream logic.
"""
from enum import Enum


class TeachingAction(str, Enum):
    EXPLAIN = "EXPLAIN"
    ASK_FOLLOWUP = "ASK_FOLLOWUP"
    RE_EXPLAIN = "RE_EXPLAIN"
    SIMPLIFY = "SIMPLIFY"
    GIVE_HINT = "GIVE_HINT"
    MOVE_ON = "MOVE_ON"
    SUMMARIZE = "SUMMARIZE"
    END_LESSON = "END_LESSON"


class TeachingStrategy(str, Enum):
    DIRECT_EXPLANATION = "direct_explanation"
    ANALOGY = "analogy"
    WATER_PIPE_ANALOGY = "water_pipe_analogy"
    STEP_BY_STEP = "step_by_step"
    VISUAL_DIAGRAM = "visual_diagram"
    WORKED_EXAMPLE = "worked_example"
    SOCRATIC_QUESTIONING = "socratic_questioning"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class StudentLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Language(str, Enum):
    ENGLISH = "English"
    HINGLISH = "Hinglish"
    HINDI = "Hindi"


class AnswerCorrectness(str, Enum):
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"
    NO_ANSWER = "no_answer"
