import pytest
from pydantic import ValidationError

from ai.teacher.schemas.actions import AssessmentResult, TeachingActionOutput
from ai.teacher.schemas.enums import (
    AnswerCorrectness,
    TeachingAction,
    TeachingStrategy,
)
from ai.teacher.schemas.lesson import LessonPlan, LessonRequest, LessonSection
from ai.teacher.schemas.state import TeacherState


def test_teacher_state_defaults():
    s = TeacherState(student_id="user_42", current_concept="resistance")
    assert s.mastery_score == 0.0
    assert s.attempt_count == 0
    assert s.version == 1
    assert s.session_id.startswith("sess_")


def test_teacher_state_rejects_out_of_range_mastery():
    s = TeacherState(student_id="u1", current_concept="c1", mastery_score=1.7)
    # clamped by validator, not rejected
    assert s.mastery_score == 1.0


def test_record_action_bumps_version_and_history():
    s = TeacherState(student_id="u1", current_concept="c1")
    v0 = s.version
    s.record_action(TeachingAction.EXPLAIN)
    assert s.last_action == TeachingAction.EXPLAIN
    assert s.recent_actions == [TeachingAction.EXPLAIN]
    assert s.version == v0 + 1


def test_recent_actions_capped():
    s = TeacherState(student_id="u1", current_concept="c1")
    for _ in range(15):
        s.record_action(TeachingAction.ASK_FOLLOWUP)
    assert len(s.recent_actions) == 10


def test_apply_mastery_delta_clamped():
    s = TeacherState(student_id="u1", current_concept="c1", mastery_score=0.9)
    s.apply_mastery_delta(0.5)
    assert s.mastery_score == 1.0
    s.apply_mastery_delta(-2.0)
    assert s.mastery_score == 0.0


def test_advance_concept_resets_attempts_and_misconception():
    s = TeacherState(student_id="u1", current_concept="resistance", attempt_count=3)
    s.set_misconception("inverse_relationship_confusion")
    s.advance_concept("voltage")
    assert s.current_concept == "voltage"
    assert s.concept_sequence_index == 1
    assert s.attempt_count == 0
    assert s.misconception is None


def test_invalid_enum_rejected():
    with pytest.raises(ValidationError):
        TeacherState(student_id="u1", current_concept="c1", difficulty="impossible")


def test_teaching_action_output_roundtrip():
    out = TeachingActionOutput(
        session_id="sess_1",
        action=TeachingAction.EXPLAIN,
        strategy=TeachingStrategy.WATER_PIPE_ANALOGY,
        content="Resistance is like a narrow pipe...",
        concept="resistance",
        difficulty="easy",
    )
    assert out.is_final_action is False
    assert out.model_dump()["action"] == "EXPLAIN"


def test_assessment_result_bounds():
    with pytest.raises(ValidationError):
        AssessmentResult(
            correctness=AnswerCorrectness.CORRECT,
            score=1.5,
            confidence=0.9,
            raw_student_answer="because current divides",
        )


def test_lesson_plan_computes_total_minutes():
    plan = LessonPlan(
        topic="Circuits",
        sections=[
            LessonSection(concept="voltage", order=0, estimated_minutes=4),
            LessonSection(concept="resistance", order=1, estimated_minutes=5),
        ],
    )
    assert plan.total_estimated_minutes == 9
