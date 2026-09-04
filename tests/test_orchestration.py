from ai.teacher.orchestration import TeacherStepEngine
from ai.teacher.schemas.actions import AssessmentResult
from ai.teacher.schemas.enums import AnswerCorrectness, TeachingAction
from ai.teacher.state.in_memory_store import InMemoryStateStore
from ai.teacher.state.manager import TeacherStateManager


def make_engine():
    manager = TeacherStateManager(InMemoryStateStore())
    state = manager.create_session("student-1", "fractions")
    return TeacherStepEngine(manager), manager, state.session_id


def test_correct_assessment_moves_on_and_updates_mastery():
    engine, manager, session_id = make_engine()
    result = engine.process_assessment(
        session_id,
        AssessmentResult(
            correctness=AnswerCorrectness.CORRECT,
            score=1.0,
            confidence=0.95,
            raw_student_answer="one half",
        ),
    )

    state = manager.load(session_id)
    assert result.action == TeachingAction.MOVE_ON
    assert state.mastery_score == 0.15
    assert state.attempt_count == 1
    assert state.last_action == TeachingAction.MOVE_ON


def test_partial_assessment_asks_for_followup():
    engine, manager, session_id = make_engine()
    result = engine.process_assessment(
        session_id,
        AssessmentResult(
            correctness=AnswerCorrectness.PARTIALLY_CORRECT,
            score=0.5,
            confidence=0.7,
            raw_student_answer="I started by finding the denominator",
        ),
    )

    assert result.action == TeachingAction.ASK_FOLLOWUP
    assert manager.load(session_id).mastery_score == 0.025


def test_incorrect_assessment_reexplains_known_misconception():
    engine, manager, session_id = make_engine()
    result = engine.process_assessment(
        session_id,
        AssessmentResult(
            correctness=AnswerCorrectness.INCORRECT,
            score=0.0,
            confidence=0.9,
            misconception="added denominators instead of multiplying",
            raw_student_answer="2/6",
        ),
    )

    state = manager.load(session_id)
    assert result.action == TeachingAction.RE_EXPLAIN
    assert state.misconception == "added denominators instead of multiplying"
    assert state.attempt_count == 1