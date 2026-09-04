import pytest

from ai.teacher.planner import LessonPlanner, LessonPlanningError
from ai.teacher.providers import FakeLLMProvider
from ai.teacher.schemas.enums import Language, StudentLevel
from ai.teacher.schemas.lesson import LessonPlan, LessonRequest, LessonSection


def plan_for(topic="Quantum Entanglement", **kwargs):
    return LessonPlan(
        topic=topic,
        sections=[LessonSection(concept="foundations", order=0, estimated_minutes=8)],
        **kwargs,
    )


def test_valid_structured_plan_is_returned_and_provider_called():
    provider = FakeLLMProvider(structured_response=plan_for())
    result = LessonPlanner(provider).plan(LessonRequest(student_id="s1", topic="Quantum Entanglement"))
    assert result.topic == "Quantum Entanglement"
    assert len(provider.calls) == 1
    assert provider.calls[0][0] == "structured"


def test_provider_failure_is_controlled_and_not_hidden():
    provider = FakeLLMProvider(raise_error=True)
    with pytest.raises(LessonPlanningError, match="planning failed"):
        LessonPlanner(provider).plan(LessonRequest(student_id="s1", topic="Any topic"))


def test_prompt_contains_learner_context():
    provider = FakeLLMProvider(structured_response=plan_for())
    request = LessonRequest(student_id="s1", topic="Cellular Respiration", student_level=StudentLevel.ADVANCED,
                            language=Language.HINDI, learning_goal="apply the model", time_budget_minutes=25,
                            current_mastery=0.4, known_concepts=["energy"], weak_concepts=["pathways"],
                            learning_history=["prior quiz: partial"], rag_context="course notes")
    LessonPlanner(provider).plan(request)
    prompt = provider.calls[0][1]
    for text in ("Cellular Respiration", "advanced", "Hindi", "apply the model", "25", "0.4", "energy", "pathways", "course notes"):
        assert text in prompt


@pytest.mark.parametrize("topic", ["Ohm's Law", "Calculus Derivatives", "Python Recursion", "World War II",
                                    "Cellular Respiration", "Supply and Demand", "French Grammar", "Machine Learning"])
def test_same_planner_handles_unrelated_domains(topic):
    provider = FakeLLMProvider(structured_response=plan_for(topic))
    result = LessonPlanner(provider).plan(LessonRequest(student_id="s1", topic=topic))
    assert result.topic == topic
