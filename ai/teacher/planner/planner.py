"""LLM-driven, domain-independent lesson planner."""
from ai.teacher.providers.llm_provider import LLMProvider, LLMProviderError
from ai.teacher.schemas.lesson import LessonPlan, LessonRequest
from ai.teacher.planner.prompts import build_lesson_plan_prompt

class LessonPlanningError(RuntimeError):
    """Planning failed; no fabricated fallback plan is returned."""

class LessonPlanner:
    def __init__(self, provider: LLMProvider):
        self._provider = provider

    def plan(self, request: LessonRequest) -> LessonPlan:
        prompt = build_lesson_plan_prompt(request)
        try:
            result = self._provider.generate_structured(prompt, LessonPlan)
            return result if isinstance(result, LessonPlan) else LessonPlan.model_validate(result)
        except (LLMProviderError, ValueError, TypeError) as exc:
            raise LessonPlanningError(f"lesson planning failed: {exc}") from exc

    create_plan = plan
