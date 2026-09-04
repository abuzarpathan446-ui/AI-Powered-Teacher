from ai.teacher.schemas.actions import AssessmentResult, TeachingActionOutput
from ai.teacher.schemas.enums import (
    AnswerCorrectness,
    TeachingAction,
    TeachingStrategy,
)
from ai.teacher.state.manager import TeacherStateManager


class TeacherStepEngine:
    """Apply one assessment result and produce the next teaching action."""

    def __init__(self, state_manager: TeacherStateManager):
        self._state_manager = state_manager

    def process_assessment(
        self, session_id: str, assessment: AssessmentResult
    ) -> TeachingActionOutput:
        action, strategy, content = self._decision(assessment)

        def mutate(state):
            state.increment_attempt()
            state.apply_mastery_delta(self._mastery_delta(assessment))
            state.set_misconception(assessment.misconception)
            state.next_action = action
            state.teaching_strategy = strategy
            state.record_action(action)

        state = self._state_manager.update(session_id, mutate)
        return TeachingActionOutput(
            session_id=state.session_id,
            action=action,
            strategy=strategy,
            content=content,
            concept=state.current_concept,
            difficulty=state.difficulty.value,
            is_final_action=action == TeachingAction.END_LESSON,
        )

    @staticmethod
    def _mastery_delta(assessment: AssessmentResult) -> float:
        if assessment.correctness == AnswerCorrectness.CORRECT:
            return 0.15 * assessment.score
        if assessment.correctness == AnswerCorrectness.PARTIALLY_CORRECT:
            return 0.05 * assessment.score
        return 0.0

    @staticmethod
    def _decision(
        assessment: AssessmentResult,
    ) -> tuple[TeachingAction, TeachingStrategy, str]:
        if assessment.correctness == AnswerCorrectness.CORRECT:
            return (
                TeachingAction.MOVE_ON,
                TeachingStrategy.SOCRATIC_QUESTIONING,
                "Good work. You are ready to move on to the next concept.",
            )
        if assessment.correctness == AnswerCorrectness.PARTIALLY_CORRECT:
            return (
                TeachingAction.ASK_FOLLOWUP,
                TeachingStrategy.STEP_BY_STEP,
                "You have part of it. Let us work through the missing step together.",
            )
        if assessment.misconception:
            return (
                TeachingAction.RE_EXPLAIN,
                TeachingStrategy.DIRECT_EXPLANATION,
                f"Let us revisit this carefully: {assessment.misconception}.",
            )
        return (
            TeachingAction.SIMPLIFY,
            TeachingStrategy.ANALOGY,
            "Let us try the idea with a simpler example.",
        )